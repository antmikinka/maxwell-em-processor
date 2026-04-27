"""
Circuit Breaker Pattern for Mathpix API Reliability
This module implements a circuit breaker pattern to handle Mathpix API
intermittent failures and prevent cascading system failures.
"""
import time
import threading
from enum import Enum
from typing import Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from src.logger_config import get_logger

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service is back

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior"""
    failure_threshold: int = 5      # Number of failures to open circuit
    recovery_timeout: int = 60      # Seconds to wait before trying again
    success_threshold: int = 3      # Successes needed to close circuit
    monitoring_window: int = 300    # Time window for failure counting (seconds)

class CircuitBreaker:
    """
    Circuit breaker implementation for API reliability
    Based on the pattern described in "Release It!" by Michael T. Nygard
    """

    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()

        # State management
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None
        self.state_change_time: Optional[datetime] = None

        # Thread safety
        self._lock = threading.Lock()

        # Statistics
        self.total_requests = 0
        self.total_failures = 0
        self.total_successes = 0

        self.logger = get_logger('circuit_breaker')

    def call(self, func: Callable[[], Any]) -> Any:
        """
        Execute a function through the circuit breaker

        Args:
            func: The function to execute (typically an API call)

        Returns:
            The result of the function call

        Raises:
            Exception: If the circuit is open or the function fails
        """
        with self._lock:
            self.total_requests += 1

            # Check if circuit should transition from OPEN to HALF_OPEN
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    self.logger.warning(f"Circuit {self.name} is OPEN - failing fast")
                    raise Exception(f"Circuit breaker is OPEN for {self.name}")

        try:
            # Execute the function
            result = func()
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt a reset"""
        if self.last_failure_time is None:
            return True

        time_since_failure = datetime.now() - self.last_failure_time
        return time_since_failure.total_seconds() >= self.config.recovery_timeout

    def _transition_to_half_open(self):
        """Transition from OPEN to HALF_OPEN state"""
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0
        self.state_change_time = datetime.now()
        self.logger.info(f"Circuit {self.name} transitioning to HALF_OPEN")

    def _on_success(self):
        """Handle successful function execution"""
        with self._lock:
            self.total_successes += 1
            self.last_success_time = datetime.now()

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self._close_circuit()
            elif self.state == CircuitState.CLOSED:
                # Reset failure count on success
                self.failure_count = 0

    def _on_failure(self):
        """Handle failed function execution"""
        with self._lock:
            self.total_failures += 1
            self.last_failure_time = datetime.now()

            if self.state == CircuitState.CLOSED:
                self.failure_count += 1
                if self.failure_count >= self.config.failure_threshold:
                    self._open_circuit()
            elif self.state == CircuitState.HALF_OPEN:
                # Any failure in half-open state opens the circuit again
                self._open_circuit()

    def _open_circuit(self):
        """Open the circuit - stop making requests"""
        self.state = CircuitState.OPEN
        self.state_change_time = datetime.now()
        self.logger.error(f"Circuit {self.name} OPENED - {self.failure_count} consecutive failures")

    def _close_circuit(self):
        """Close the circuit - resume normal operation"""
        self.state = CircuitState.CLOSED
        self.state_change_time = datetime.now()
        self.failure_count = 0
        self.success_count = 0
        self.logger.info(f"Circuit {self.name} CLOSED - service recovered")

    def get_stats(self) -> dict:
        """Get circuit breaker statistics"""
        with self._lock:
            time_in_current_state = 0
            if self.state_change_time:
                time_in_current_state = (datetime.now() - self.state_change_time).total_seconds()

            return {
                'name': self.name,
                'state': self.state.value,
                'total_requests': self.total_requests,
                'total_successes': self.total_successes,
                'total_failures': self.total_failures,
                'failure_rate': self.total_failures / max(self.total_requests, 1),
                'current_failure_count': self.failure_count,
                'current_success_count': self.success_count,
                'time_in_current_state': time_in_current_state,
                'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
                'last_success_time': self.last_success_time.isoformat() if self.last_success_time else None
            }

    def health_check(self) -> dict:
        """Perform a health check on the circuit breaker"""
        stats = self.get_stats()
        is_healthy = stats['failure_rate'] < 0.1 and self.state == CircuitState.CLOSED

        return {
            'healthy': is_healthy,
            'status': 'HEALTHY' if is_healthy else 'UNHEALTHY',
            'details': stats
        }

class MathpixCircuitBreaker:
    """
    Specialized circuit breaker for Mathpix API with enhanced error handling
    """
    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        self.config = config or self._get_default_config()
        self.circuit_breaker = CircuitBreaker("mathpix_api", self.config)
        self.logger = get_logger('mathpix_circuit_breaker')

    def _get_default_config(self) -> CircuitBreakerConfig:
        """Get default configuration for Mathpix API"""
        return CircuitBreakerConfig(
            failure_threshold=3,      # Be more aggressive with Mathpix
            recovery_timeout=30,      # Quick recovery attempts
            success_threshold=2,      # Fewer successes needed to close
            monitoring_window=180     # Shorter monitoring window
        )

    def is_healthy(self) -> bool:
        """Check if the Mathpix API circuit is healthy"""
        stats = self.circuit_breaker.get_stats()
        return stats['state'] == 'closed' and stats['failure_rate'] < 0.05

    def get_health_report(self) -> dict:
        """Get detailed health report"""
        circuit_health = self.circuit_breaker.health_check()
        stats = self.circuit_breaker.get_stats()

        return {
            'service': 'mathpix_api',
            'circuit_breaker_health': circuit_health,
            'detailed_stats': stats,
            'recommendations': self._get_recommendations(stats)
        }

    def _get_recommendations(self, stats: dict) -> list:
        """Get recommendations based on current stats"""
        recommendations = []

        if stats['state'] == 'open':
            recommendations.append("Circuit is OPEN - avoid making requests until service recovers")
        elif stats['failure_rate'] > 0.1:
            recommendations.append("High failure rate detected - consider reducing request frequency")
        elif stats['total_requests'] < 10:
            recommendations.append("Low request volume - circuit breaker may be overly sensitive")
        elif stats['failure_rate'] > 0.05:
            recommendations.append("Moderate failure rate - monitor closely and consider adjusting thresholds")

        return recommendations

    def call_with_circuit(self, api_call: Callable[[], Any]) -> Any:
        """
        Execute an API call through the circuit breaker

        Args:
            api_call: Function that makes the Mathpix API request

        Returns:
            API response

        Raises:
            Exception: If circuit is open or API call fails
        """
        try:
            return self.circuit_breaker.call(api_call)
        except Exception as e:
            self.logger.error(f"Mathpix API call failed through circuit breaker: {e}")
            raise

# Global Mathpix circuit breaker instance
mathpix_circuit_breaker = MathpixCircuitBreaker()

def get_mathpix_circuit_breaker() -> MathpixCircuitBreaker:
    """Get the global Mathpix circuit breaker instance"""
    return mathpix_circuit_breaker

if __name__ == '__main__':
    # Test the circuit breaker
    breaker = get_mathpix_circuit_breaker()
    print("Mathpix circuit breaker initialized successfully")
    
    # Test function that sometimes fails
    def test_api_call(success_rate=0.7):
        import random
        if random.random() < success_rate:
            return {"status": "success"}
        else:
            raise Exception("API call failed")
    
    print("\nTesting circuit breaker behavior:")
    for i in range(10):
        try:
            result = breaker.call_with_circuit(lambda: test_api_call(0.3))  # Low success rate to trigger failures
            print(f"Call {i+1}: SUCCESS - {result}")
        except Exception as e:
            print(f"Call {i+1}: FAILED - {e}")
        
        stats = breaker.circuit_breaker.get_stats()
        print(f"  State: {stats['state']}, Failures: {stats['current_failure_count']}, Total failures: {stats['total_failures']}")
        
        time.sleep(0.1)  # Small delay between calls
    
    print("\nFinal circuit breaker state:")
    health_report = breaker.get_health_report()
    print(f"Health: {health_report['circuit_breaker_health']['status']}")
    print(f"State: {health_report['detailed_stats']['state']}")
    print(f"Failure rate: {health_report['detailed_stats']['failure_rate']:.2%}")
    print(f"Recommendations: {health_report['recommendations']}")