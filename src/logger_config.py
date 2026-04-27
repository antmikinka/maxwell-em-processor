"""
Logging Configuration Module
Sets up comprehensive logging with multiple log files and verbosity levels
"""

import sys
from pathlib import Path
from loguru import logger
from typing import Optional
from datetime import datetime


class LoggerConfig:
    """Configure application-wide logging"""
    
    def __init__(self, logs_dir: Path, log_level: str = 'INFO'):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.log_level = log_level
        
        # Remove default handler
        logger.remove()
        
        # Setup all log handlers
        self._setup_console_logging()
        self._setup_main_pipeline_log()
        self._setup_mathpix_api_log()
        self._setup_openrouter_api_log()
        self._setup_error_log()
        self._setup_processing_stats_log()
    
    def _setup_console_logging(self):
        """Setup colored console output with proper encoding"""
        # Force UTF-8 encoding for console output on Windows
        import io
        if sys.stdout.encoding != 'utf-8':
            # Create a UTF-8 wrapper for stdout
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer,
                encoding='utf-8',
                errors='replace',
                line_buffering=sys.stdout.line_buffering
            )

        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            level=self.log_level,
            colorize=True
        )
    
    def _setup_main_pipeline_log(self):
        """Main pipeline log - all events"""
        logger.add(
            self.logs_dir / 'main_pipeline.log',
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level=self.log_level,
            rotation="50 MB",
            retention="10 days",
            compression="zip",
            enqueue=True,
        )
    
    def _setup_mathpix_api_log(self):
        """Mathpix API calls and responses"""
        logger.add(
            self.logs_dir / 'mathpix_api.log',
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            level="DEBUG",
            rotation="100 MB",
            retention="30 days",
            compression="zip",
            enqueue=True,
            filter=lambda record: 'mathpix' in record['name'].lower() or 
                                 'mathpix' in record.get('extra', {}).get('module', '').lower()
        )
    
    def _setup_openrouter_api_log(self):
        """OpenRouter API calls and responses"""
        logger.add(
            self.logs_dir / 'openrouter_api.log',
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            level="DEBUG",
            rotation="100 MB",
            retention="30 days",
            compression="zip",
            enqueue=True,
            filter=lambda record: 'openrouter' in record['name'].lower() or 
                                 'openrouter' in record.get('extra', {}).get('module', '').lower()
        )
    
    def _setup_error_log(self):
        """Error-only log for debugging"""
        logger.add(
            self.logs_dir / 'errors.log',
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}\n{exception}",
            level="ERROR",
            rotation="50 MB",
            retention="30 days",
            compression="zip",
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )
    
    def _setup_processing_stats_log(self):
        """Processing statistics and metrics"""
        logger.add(
            self.logs_dir / 'processing_stats.log',
            format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
            level="INFO",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            enqueue=True,
            filter=lambda record: record.get('extra', {}).get('stats', False)
        )


class APILogger:
    """Specialized logger for API calls with caching"""
    
    def __init__(self, cache_dir: Path, api_name: str):
        self.cache_dir = Path(cache_dir) / api_name
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.api_name = api_name
        self.logger = logger.bind(module=api_name)
    
    def log_request(self, endpoint: str, params: dict, request_id: Optional[str] = None):
        """Log an API request"""
        self.logger.debug(
            f"[{self.api_name}] REQUEST to {endpoint}",
            extra={
                'request_id': request_id,
                'endpoint': endpoint,
                'params': params,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    def log_response(self, endpoint: str, response_data: dict, request_id: Optional[str] = None):
        """Log an API response"""
        # Log basic response metadata
        self.logger.debug(
            f"[{self.api_name}] RESPONSE from {endpoint}",
            extra={
                'request_id': request_id,
                'endpoint': endpoint,
                'response_size': len(str(response_data)),
                'timestamp': datetime.now().isoformat()
            }
        )

        # For debugging, also log the actual response content for error cases
        if isinstance(response_data, dict) and ('error' in response_data or 'pdf_id' not in response_data):
            self.logger.warning(
                f"[{self.api_name}] RESPONSE content for {endpoint}: {response_data}"
            )
    
    def log_error(self, endpoint: str, error: Exception, request_id: Optional[str] = None):
        """Log an API error"""
        self.logger.error(
            f"[{self.api_name}] ERROR at {endpoint}: {str(error)}",
            extra={
                'request_id': request_id,
                'endpoint': endpoint,
                'error_type': type(error).__name__,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    def cache_response(self, cache_key: str, response_data: dict):
        """Cache API response to file"""
        import json
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'api': self.api_name,
            'data': response_data
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.debug(f"Cached response to {cache_file}")
    
    def load_cached_response(self, cache_key: str) -> Optional[dict]:
        """Load cached API response"""
        import json
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            self.logger.debug(f"Loaded cached response from {cache_file}")
            return cache_data.get('data')
        except Exception as e:
            self.logger.warning(f"Failed to load cache {cache_file}: {e}")
            return None


class StatsLogger:
    """Logger for processing statistics"""
    
    def __init__(self):
        self.logger = logger.bind(stats=True)
    
    def log_stage_start(self, stage_name: str):
        """Log the start of a processing stage"""
        self.logger.info(
            f"{'='*60}\n"
            f"STAGE START: {stage_name}\n"
            f"Time: {datetime.now().isoformat()}\n"
            f"{'='*60}"
        )
    
    def log_stage_complete(self, stage_name: str, duration_seconds: float, stats: dict):
        """Log stage completion with statistics"""
        self.logger.info(
            f"{'='*60}\n"
            f"STAGE COMPLETE: {stage_name}\n"
            f"Duration: {duration_seconds:.2f} seconds\n"
            f"Statistics:\n" +
            "\n".join(f"  {k}: {v}" for k, v in stats.items()) +
            f"\n{'='*60}"
        )
    
    def log_progress(self, current: int, total: int, description: str = ""):
        """Log progress update"""
        percentage = (current / total * 100) if total > 0 else 0
        self.logger.info(
            f"Progress: {current}/{total} ({percentage:.1f}%) {description}"
        )
    
    def log_metric(self, metric_name: str, value: any, unit: str = ""):
        """Log a single metric"""
        self.logger.info(f"Metric: {metric_name} = {value} {unit}")


def get_logger(name: str) -> logger:
    """Get a logger instance for a specific module"""
    return logger.bind(name=name)


def get_api_logger(cache_dir: Path, api_name: str) -> APILogger:
    """Get an API logger instance"""
    return APILogger(cache_dir, api_name)


def get_stats_logger() -> StatsLogger:
    """Get a statistics logger instance"""
    return StatsLogger()


# Initialize logging when module is imported
def init_logging(logs_dir: Path, log_level: str = 'INFO'):
    """Initialize logging system"""
    return LoggerConfig(logs_dir, log_level)


if __name__ == '__main__':
    # Test logging
    from pathlib import Path
    init_logging(Path('test_logs'), 'DEBUG')
    
    test_logger = get_logger('test')
    test_logger.info("Test info message")
    test_logger.debug("Test debug message")
    test_logger.warning("Test warning message")
    
    api_logger = get_api_logger(Path('test_cache'), 'test_api')
    api_logger.log_request('test/endpoint', {'param': 'value'})
    api_logger.cache_response('test_key', {'result': 'data'})
    
    stats_logger = get_stats_logger()
    stats_logger.log_stage_start('Test Stage')
    stats_logger.log_progress(5, 10, "processing items")
