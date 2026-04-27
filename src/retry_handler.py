"""
Enhanced Retry Logic with Exponential Backoff
This module provides intelligent retry mechanisms for handling transient
failures in Mathpix API calls with exponential backoff and jitter.
"""
import time
import random
import logging
from typing import Callable, Any, Optional, List, Type, Dict, Union
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
from datetime import datetime, timedelta
import requests
from requests.exceptions import (
    ConnectionError, Timeout, HTTPError, RequestException
)
from src.logger_config import get_logger

class RetryStrategy(Enum):
    """Different retry strategies for different error types"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    CONSTANT_DELAY = "constant_delay"
    FIBONACCI_BACKOFF = "fibonacci_backoff"
    ADAPTIVE = "adaptive"

@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_retries: int = 3
    base_delay: float = 1.0  # Base delay in seconds
    max_delay: float = 60.0  # Maximum delay in seconds
    jitter: bool = True      # Add random jitter to prevent thundering herd
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    retryable_exceptions: List[Type[Exception]] = field(default_factory=list)
    retryable_status_codes: List[int] = field(default_factory=lambda: [429, 500, 502, 503, 504])
    exponential_multiplier: float = 2.0
    max_jitter_factor: float = 0.3

class ErrorType(Enum):
    """Classification of error types for adaptive retry"""
    CONNECTION_ERROR = "connection_error"
    TIMEOUT_ERROR = "timeout_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    SERVER_ERROR = "server_error"
    CLIENT_ERROR = "client_error"
    AUTH_ERROR = "auth_error"
    UNKNOWN_ERROR = "unknown_error"

@dataclass
class ErrorRecord:
    """Record of an error for analysis"""
    error_type: ErrorType
    exception_type: str
    message: str
    context: str
    timestamp: datetime
    retry_delay: float = 0.0
    retry_attempt: int = 0
    was_success: bool = False

class MathpixRetryHandler:
    """
    Intelligent retry handler for Mathpix API calls
    Features:
    - Multiple retry strategies
    - Configurable exception handling
    - Jitter to prevent thundering herd
    - Detailed logging and metrics
    - Thread-safe operation
    """
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or self._get_default_config()
        self.logger = get_logger('retry_handler')
        
        # Health monitor will be imported lazily to avoid circular imports
        self._health_monitor = None
        
        # Thread safety
        self._lock = Lock()
        
        # Metrics
        self.total_retries = 0
        self.total_attempts = 0
        self.success_on_retry = 0
        self.total_failures = 0
        
        # Error history for analysis
        self.error_history: List[ErrorRecord] = []
        self.max_history = 100
        
        # Performance tracking
        self.successful_retry_delays = []
        self.failed_retry_delays = []
        self.max_performance_history = 50

    def _get_default_config(self) -> RetryConfig:
        """Get default retry configuration for Mathpix API"""
        return RetryConfig(
            max_retries=5,
            base_delay=2.0,
            max_delay=30.0,
            jitter=True,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            retryable_exceptions=[
                ConnectionError,
                Timeout,
                HTTPError,
                RequestException
            ],
            retryable_status_codes=[429, 500, 502, 503, 504],
            exponential_multiplier=2.0,
            max_jitter_factor=0.3
        )

    def _get_health_monitor(self):
        """Lazy import of health monitor to avoid circular imports"""
        if self._health_monitor is None:
            try:
                from src.health_monitor import get_health_monitor
                self._health_monitor = get_health_monitor()
            except ImportError:
                self.logger.warning("Failed to import health monitor - continuing without health integration")
                self._health_monitor = None
        return self._health_monitor

    def execute_with_retry(self, func: Callable[[], Any], context: str = "") -> Any:
        """
        Execute a function with intelligent retry logic
        
        Args:
            func: The function to execute
            context: Context description for logging and error analysis
            
        Returns:
            Function result
            
        Raises:
            Exception: If all retry attempts fail or if non-retryable error occurs
        """
        with self._lock:
            self.total_attempts += 1
            
        last_exception = None
        last_error_type = ErrorType.UNKNOWN_ERROR
        
        for attempt in range(self.config.max_retries + 1):
            try:
                start_time = time.time()
                result = func()
                execution_time = time.time() - start_time
                
                if attempt > 0:
                    with self._lock:
                        self.success_on_retry += 1
                        self.successful_retry_delays.append(execution_time)
                        if len(self.successful_retry_delays) > self.max_performance_history:
                            self.successful_retry_delays.pop(0)
                    
                    self.logger.info(
                        f"✅ Success on retry attempt {attempt}/{self.config.max_retries} for {context} "
                        f"(execution time: {execution_time:.2f}s)"
                    )
                    
                    # Record successful retry
                    self._record_error(
                        error_type=None,
                        exception=None,
                        context=context,
                        retry_attempt=attempt,
                        retry_delay=execution_time,
                        was_success=True
                    )
                    
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                last_exception = e
                error_type = self._classify_error(e)
                last_error_type = error_type
                
                # Record the error
                self._record_error(
                    error_type=error_type,
                    exception=e,
                    context=context,
                    retry_attempt=attempt,
                    retry_delay=execution_time,
                    was_success=False
                )
                
                # Check if we should retry this exception
                if not self._should_retry_exception(e, error_type):
                    self.logger.error(
                        f"[ERROR] Non-retryable exception for {context} on attempt {attempt}: "
                        f"{type(e).__name__}: {str(e)[:100]}"
                    )
                    with self._lock:
                        self.total_failures += 1
                    raise e
                
                # Check if we've exhausted retries
                if attempt >= self.config.max_retries:
                    self.logger.error(
                        f"[ERROR] Max retries ({self.config.max_retries}) exceeded for {context}: "
                        f"{type(e).__name__}: {str(e)[:100]}"
                    )
                    with self._lock:
                        self.total_failures += 1
                    raise e
                
                # Calculate delay
                delay = self._calculate_delay(attempt, error_type)
                
                with self._lock:
                    self.total_retries += 1
                    self.failed_retry_delays.append(delay)
                    if len(self.failed_retry_delays) > self.max_performance_history:
                        self.failed_retry_delays.pop(0)
                
                self.logger.warning(
                    f"⚠️  Attempt {attempt + 1}/{self.config.max_retries + 1} failed for {context}: "
                    f"{type(e).__name__}: {str(e)[:100]}. "
                    f"Error type: {error_type.value}. Retrying in {delay:.2f} seconds..."
                )
                
                # Check health monitor for system recommendations (lazy import)
                health_monitor = self._get_health_monitor()
                if health_monitor:
                    health_report = health_monitor.get_health_report()
                    if health_report.get('recommendations'):
                        for rec in health_report['recommendations'][:3]:
                            self.logger.info(f"💡 Health recommendation: {rec}")
                
                # Wait before retry
                time.sleep(delay)

        # This should never be reached, but just in case
        raise last_exception

    def _classify_error(self, exception: Exception) -> ErrorType:
        """Classify exception into error types for adaptive retry"""
        exception_type = type(exception)
        exception_str = str(exception).lower()

        # --- ADD THIS BLOCK ---
        # Check for explicit Mathpix internal errors in the exception message
        if "internal error" in exception_str or "sys_exception" in exception_str:
            return ErrorType.SERVER_ERROR
        # ----------------------

        # Check for rate limiting
        if any(keyword in exception_str for keyword in ['rate limit', 'quota exceeded', 'too many requests', '429']):
            return ErrorType.RATE_LIMIT_ERROR

        # Check for authentication errors
        if any(keyword in exception_str for keyword in ['auth', 'authentication', 'authorization', 'invalid key', '401', '403']):
            return ErrorType.AUTH_ERROR

        # Check for client errors
        if exception_type == HTTPError:
            if hasattr(exception, 'response') and exception.response is not None:
                status_code = exception.response.status_code
                if 400 <= status_code < 500 and status_code not in [429, 401, 403]:
                    return ErrorType.CLIENT_ERROR

        # Connection errors
        if issubclass(exception_type, ConnectionError):
            return ErrorType.CONNECTION_ERROR

        # Timeout errors
        if issubclass(exception_type, Timeout):
            return ErrorType.TIMEOUT_ERROR

        # Server errors
        if exception_type == HTTPError:
            if hasattr(exception, 'response') and exception.response is not None:
                status_code = exception.response.status_code
                if 500 <= status_code < 600:
                    return ErrorType.SERVER_ERROR

        # Generic request exceptions
        if issubclass(exception_type, RequestException):
            return ErrorType.CONNECTION_ERROR

        return ErrorType.UNKNOWN_ERROR

    def _should_retry_exception(self, exception: Exception, error_type: ErrorType) -> bool:
        """Determine if an exception should trigger a retry"""
        # Never retry auth errors or client errors (except rate limits)
        if error_type in [ErrorType.AUTH_ERROR, ErrorType.CLIENT_ERROR]:
            return False
            
        # Always retry rate limits, connection errors, timeouts, and server errors
        if error_type in [ErrorType.RATE_LIMIT_ERROR, ErrorType.CONNECTION_ERROR, 
                         ErrorType.TIMEOUT_ERROR, ErrorType.SERVER_ERROR]:
            return True
        
        # For other errors, check if they're in the retryable exceptions list
        exception_type = type(exception)
        return any(
            issubclass(exception_type, retryable_exception)
            for retryable_exception in self.config.retryable_exceptions
        )

    def _calculate_delay(self, attempt: int, error_type: ErrorType) -> float:
        """Calculate delay for the given attempt using configured strategy"""
        base_delay = self.config.base_delay
        
        # Adjust base delay based on error type
        if error_type == ErrorType.RATE_LIMIT_ERROR:
            base_delay = max(base_delay, 5.0)  # Minimum 5 seconds for rate limits
        elif error_type == ErrorType.SERVER_ERROR:
            base_delay = max(base_delay, 3.0)  # Minimum 3 seconds for server errors
        elif error_type == ErrorType.TIMEOUT_ERROR:
            base_delay = max(base_delay, 2.0)  # Minimum 2 seconds for timeouts
        
        # Apply strategy
        if self.config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = min(base_delay * (self.config.exponential_multiplier ** attempt), self.config.max_delay)
        elif self.config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = min(base_delay * (attempt + 1), self.config.max_delay)
        elif self.config.strategy == RetryStrategy.CONSTANT_DELAY:
            delay = base_delay
        elif self.config.strategy == RetryStrategy.FIBONACCI_BACKOFF:
            delay = min(self._fibonacci(attempt + 1) * base_delay, self.config.max_delay)
        elif self.config.strategy == RetryStrategy.ADAPTIVE:
            delay = self._calculate_adaptive_delay(attempt, error_type)
        else:
            delay = base_delay
        
        # Add jitter to prevent thundering herd
        if self.config.jitter and self.config.max_jitter_factor > 0:
            jitter = (random.random() * 2 - 1) * self.config.max_jitter_factor * delay
            delay += jitter
        
        # Ensure minimum delay of 100ms
        return max(delay, 0.1)

    def _calculate_adaptive_delay(self, attempt: int, error_type: ErrorType) -> float:
        """Calculate delay using adaptive strategy based on error history"""
        base_delay = self.config.base_delay
        
        # Get recent errors of the same type
        recent_errors = [
            err for err in self.error_history[-20:] 
            if err.error_type == error_type and not err.was_success
        ]
        
        if not recent_errors:
            return base_delay * (self.config.exponential_multiplier ** attempt)
        
        # Calculate average delay that led to success for this error type
        successful_delays = [
            err.retry_delay for err in self.error_history[-50:]
            if err.error_type == error_type and err.was_success
        ]
        
        if successful_delays:
            avg_successful_delay = sum(successful_delays) / len(successful_delays)
            # Use a fraction of the successful delay, but don't go below base delay
            return max(base_delay, avg_successful_delay * 0.7)
        
        # If no successful retries, be more conservative
        failure_count = len(recent_errors)
        return min(base_delay * (1.5 ** failure_count), self.config.max_delay)

    def _fibonacci(self, n: int) -> int:
        """Calculate nth Fibonacci number"""
        if n <= 1:
            return 1
        a, b = 1, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

    def _record_error(
        self, 
        error_type: Optional[ErrorType], 
        exception: Optional[Exception], 
        context: str,
        retry_attempt: int,
        retry_delay: float,
        was_success: bool
    ):
        """Record an error or success for analysis"""
        record = ErrorRecord(
            error_type=error_type or ErrorType.UNKNOWN_ERROR,
            exception_type=type(exception).__name__ if exception else "Success",
            message=str(exception)[:200] if exception else "Operation succeeded",
            context=context,
            timestamp=datetime.now(),
            retry_delay=retry_delay,
            retry_attempt=retry_attempt,
            was_success=was_success
        )
        
        with self._lock:
            self.error_history.append(record)
            if len(self.error_history) > self.max_history:
                self.error_history.pop(0)

    def get_metrics(self) -> dict:
        """Get retry metrics"""
        with self._lock:
            retry_rate = self.total_retries / max(self.total_attempts, 1)
            success_rate = self.success_on_retry / max(self.total_retries, 1) if self.total_retries > 0 else 0.0
            
            avg_successful_delay = sum(self.successful_retry_delays) / len(self.successful_retry_delays) if self.successful_retry_delays else 0.0
            avg_failed_delay = sum(self.failed_retry_delays) / len(self.failed_retry_delays) if self.failed_retry_delays else 0.0
            
            return {
                'total_attempts': self.total_attempts,
                'total_retries': self.total_retries,
                'success_on_retry': self.success_on_retry,
                'total_failures': self.total_failures,
                'retry_rate': retry_rate,
                'success_rate_after_retry': success_rate,
                'average_successful_retry_delay': avg_successful_delay,
                'average_failed_retry_delay': avg_failed_delay,
                'config': {
                    'max_retries': self.config.max_retries,
                    'base_delay': self.config.base_delay,
                    'max_delay': self.config.max_delay,
                    'strategy': self.config.strategy.value,
                    'jitter': self.config.jitter,
                    'exponential_multiplier': self.config.exponential_multiplier
                }
            }

    def health_check(self) -> dict:
        """Check the health of the retry system"""
        metrics = self.get_metrics()
        healthy = (
            metrics['retry_rate'] < 0.3 and 
            metrics['success_rate_after_retry'] > 0.7 and
            metrics['total_failures'] / max(metrics['total_attempts'], 1) < 0.1
        )
        
        return {
            'healthy': healthy,
            'status': 'HEALTHY' if healthy else 'DEGRADED' if metrics['success_rate_after_retry'] > 0.3 else 'UNHEALTHY',
            'metrics': metrics,
            'recommendations': self._get_health_recommendations(metrics)
        }

    def _get_health_recommendations(self, metrics: dict) -> list:
        """Get recommendations based on retry health metrics"""
        recommendations = []
        
        if metrics['retry_rate'] > 0.5:
            recommendations.append("High retry rate detected - consider investigating root cause of failures")
        
        if metrics['success_rate_after_retry'] < 0.3:
            recommendations.append("Low success rate after retry - may need to adjust retry strategy or increase delays")
        
        if metrics['retry_rate'] < 0.05:
            recommendations.append("Very low retry rate - current configuration appears optimal for stability")
        
        if metrics['average_failed_retry_delay'] > 0 and metrics['average_successful_retry_delay'] > 0:
            ratio = metrics['average_failed_retry_delay'] / metrics['average_successful_retry_delay']
            if ratio > 2:
                recommendations.append("Successful retries take significantly less time than failed ones - consider reducing initial delay")
        
        if metrics['total_failures'] > 10 and metrics['success_rate_after_retry'] < 0.5:
            recommendations.append("Persistent failure pattern detected - check Mathpix API status and credentials")
        
        return recommendations

    def get_error_analysis(self) -> dict:
        """Get analysis of recent errors"""
        if not self.error_history:
            return {'error_count': 0, 'analysis': 'No errors recorded'}
        
        recent_errors = self.error_history[-20:]  # Last 20 errors
        total_errors = len(recent_errors)
        
        # Count error types
        error_counts = {}
        for error in recent_errors:
            if not error.was_success:
                error_type = error.error_type.value
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        # Calculate time distribution
        if len(recent_errors) > 1:
            time_span = (recent_errors[-1].timestamp - recent_errors[0].timestamp).total_seconds()
            errors_per_minute = (total_errors / time_span) * 60 if time_span > 0 else 0
        else:
            time_span = 0
            errors_per_minute = 0
        
        # Analyze success patterns
        successful_retries = [err for err in recent_errors if err.was_success]
        failed_retries = [err for err in recent_errors if not err.was_success]
        
        avg_retry_attempts = sum(err.retry_attempt for err in failed_retries) / len(failed_retries) if failed_retries else 0
        
        return {
            'total_errors': total_errors,
            'error_distribution': error_counts,
            'time_span_seconds': time_span,
            'errors_per_minute': errors_per_minute,
            'successful_retries': len(successful_retries),
            'failed_retries': len(failed_retries),
            'average_retry_attempts': avg_retry_attempts,
            'most_common_contexts': self._get_most_common_contexts(recent_errors),
            'recommendations': self._analyze_error_pattern(error_counts)
        }

    def _get_most_common_contexts(self, errors: List[ErrorRecord]) -> Dict[str, int]:
        """Get the most common contexts where errors occur"""
        context_counts = {}
        for error in errors:
            if not error.was_success:
                context_counts[error.context] = context_counts.get(error.context, 0) + 1
        
        # Sort by count and return top 5
        return dict(sorted(context_counts.items(), key=lambda x: x[1], reverse=True)[:5])

    def _analyze_error_pattern(self, error_counts: dict) -> list:
        """Analyze error patterns and provide recommendations"""
        recommendations = []
        
        if error_counts.get(ErrorType.CONNECTION_ERROR.value, 0) > 5:
            recommendations.append("High connection errors detected - check network stability and Mathpix API availability")
        
        if error_counts.get(ErrorType.TIMEOUT_ERROR.value, 0) > 3:
            recommendations.append("High timeout errors - consider increasing timeout values or reducing request size")
        
        if error_counts.get(ErrorType.RATE_LIMIT_ERROR.value, 0) > 2:
            recommendations.append("Rate limit errors detected - reduce request frequency or contact Mathpix for quota increase")
        
        if error_counts.get(ErrorType.SERVER_ERROR.value, 0) > 3:
            recommendations.append("Persistent server errors - check Mathpix API status page and consider temporary backoff")
        
        if error_counts.get(ErrorType.AUTH_ERROR.value, 0) > 0:
            recommendations.append("Authentication errors detected - verify Mathpix API credentials and permissions")
        
        return recommendations

class SmartRetryHandler:
    """
    Smart retry handler that adapts based on error types and historical performance
    """
    def __init__(self):
        self.handlers: Dict[ErrorType, MathpixRetryHandler] = {}
        self.default_handler = MathpixRetryHandler()
        self.logger = get_logger('smart_retry_handler')
        self._initialize_handlers()

    def _initialize_handlers(self):
        """Initialize specialized handlers for different error types"""
        # Connection error handler - more aggressive retries
        connection_config = RetryConfig(
            max_retries=7,
            base_delay=1.0,
            max_delay=45.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            exponential_multiplier=2.5,
            jitter=True
        )
        self.handlers[ErrorType.CONNECTION_ERROR] = MathpixRetryHandler(connection_config)
        
        # Timeout error handler - longer delays
        timeout_config = RetryConfig(
            max_retries=4,
            base_delay=3.0,
            max_delay=60.0,
            strategy=RetryStrategy.LINEAR_BACKOFF,
            jitter=True
        )
        self.handlers[ErrorType.TIMEOUT_ERROR] = MathpixRetryHandler(timeout_config)
        
        # Rate limit handler - conservative with longer delays
        rate_limit_config = RetryConfig(
            max_retries=3,
            base_delay=5.0,
            max_delay=120.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            exponential_multiplier=1.8,
            retryable_status_codes=[429]
        )
        self.handlers[ErrorType.RATE_LIMIT_ERROR] = MathpixRetryHandler(rate_limit_config)
        
        # Server error handler - moderate retries
        server_config = RetryConfig(
            max_retries=5,
            base_delay=2.0,
            max_delay=40.0,
            strategy=RetryStrategy.FIBONACCI_BACKOFF,
            jitter=True
        )
        self.handlers[ErrorType.SERVER_ERROR] = MathpixRetryHandler(server_config)

    def execute_with_adaptive_retry(self, func: Callable[[], Any], context: str = "") -> Any:
        """
        Execute function with adaptive retry based on error patterns
        
        Args:
            func: The function to execute
            context: Context description for logging and error analysis
            
        Returns:
            Function result
            
        Raises:
            Exception: If all retry attempts fail
        """
        try:
            # Start with default handler
            return self.default_handler.execute_with_retry(func, context)
        except Exception as e:
            # Classify the error and try with specialized handler
            error_type = self.default_handler._classify_error(e)
            
            if error_type in self.handlers:
                self.logger.info(f"🔄 Switching to specialized handler for {error_type.value}")
                handler = self.handlers[error_type]
                return handler.execute_with_retry(func, context)
            else:
                # No specialized handler, re-raise
                raise

    def get_error_analysis(self) -> dict:
        """Get comprehensive error analysis from all handlers"""
        analyses = {}
        
        # Default handler analysis
        analyses['default'] = self.default_handler.get_error_analysis()
        
        # Specialized handler analyses
        for error_type, handler in self.handlers.items():
            analyses[error_type.value] = handler.get_error_analysis()
        
        # Overall statistics
        total_errors = sum(analysis.get('total_errors', 0) for analysis in analyses.values())
        total_successful_retries = sum(analysis.get('successful_retries', 0) for analysis in analyses.values())
        
        return {
            'total_errors': total_errors,
            'total_successful_retries': total_successful_retries,
            'success_rate': total_successful_retries / max(total_errors, 1),
            'handler_analyses': analyses,
            'recommendations': self._get_comprehensive_recommendations(analyses)
        }

    def _get_comprehensive_recommendations(self, analyses: dict) -> list:
        """Get comprehensive recommendations from all handler analyses"""
        all_recommendations = []
        
        for handler_name, analysis in analyses.items():
            recs = analysis.get('recommendations', [])
            if recs:
                all_recommendations.extend([f"[{handler_name}] {rec}" for rec in recs])
        
        # Deduplicate and prioritize
        unique_recommendations = list(dict.fromkeys(all_recommendations))
        
        # Add system-level recommendations
        total_errors = sum(analysis.get('total_errors', 0) for analysis in analyses.values())
        if total_errors > 50:
            unique_recommendations.insert(0, "CRITICAL: High error volume detected - consider pausing pipeline and investigating root cause")
        
        return unique_recommendations[:10]  # Return top 10 recommendations

# Global retry handlers
_mathpix_retry_handler = None
_smart_retry_handler = None

def get_mathpix_retry_handler() -> MathpixRetryHandler:
    """Get the global Mathpix retry handler (singleton)"""
    global _mathpix_retry_handler
    if _mathpix_retry_handler is None:
        _mathpix_retry_handler = MathpixRetryHandler()
    return _mathpix_retry_handler

def get_smart_retry_handler() -> SmartRetryHandler:
    """Get the smart adaptive retry handler (singleton)"""
    global _smart_retry_handler
    if _smart_retry_handler is None:
        _smart_retry_handler = SmartRetryHandler()
    return _smart_retry_handler

if __name__ == '__main__':
    # Test the retry handler
    logger = get_logger('retry_test')
    handler = get_mathpix_retry_handler()
    
    print("🧪 Testing retry handler with simulated failures...")
    
    # Test function that fails a few times then succeeds
    attempt_count = 0
    def flaky_function():
        global attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ConnectionError(f"Connection failed on attempt {attempt_count}")
        return f"Success on attempt {attempt_count}"
    
    try:
        result = handler.execute_with_retry(flaky_function, context="test_api_call")
        print(f"✅ Test succeeded: {result}")
        
        # Get metrics
        metrics = handler.get_metrics()
        print(f"📊 Retry metrics: {metrics}")
        
        # Get health check
        health = handler.health_check()
        print(f"🏥 Health check: {health['status']}")
        if health['recommendations']:
            print("💡 Recommendations:")
            for rec in health['recommendations']:
                print(f"  - {rec}")
                
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
    
    # Test rate limiting scenario
    def rate_limit_function():
        raise HTTPError("429 Client Error: Too Many Requests")
    
    try:
        handler.execute_with_retry(rate_limit_function, context="rate_limit_test")
    except Exception as e:
        print(f"✅ Rate limit test correctly failed after retries: {e}")