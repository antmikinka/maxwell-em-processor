"""Health Monitoring System for Mathpix API Reliability
This module provides comprehensive health monitoring for the Maxwell EM Processor
including Mathpix API status, circuit breaker health, and system performance metrics."""
import time
import threading
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
# Add missing import for psutil
import psutil 
from src.logger_config import get_logger
from src.circuit_breaker import get_mathpix_circuit_breaker
from src.retry_handler import get_mathpix_retry_handler, get_smart_retry_handler
# Add import for getting paths
from config.config import get_paths # Import get_paths

@dataclass
class HealthStatus:
    service: str
    status: str  # HEALTHY, DEGRADED, UNHEALTHY
    healthy: bool
    timestamp: str
    details: Dict[str, Any]
    recommendations: List[str] = None

    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


@dataclass
class SystemMetrics:
    timestamp: str
    uptime_seconds: float
    successful_requests: int
    failed_requests: int
    retry_count: int
    retry_success_rate: float
    memory_usage_mb: float
    disk_usage_percent: float
    cpu_usage_percent: float = 0.0  # Added CPU usage metric
    circuit_breaker_state: str = "unknown"
    circuit_breaker_failures: int = 0
    process_memory_mb: float = 0.0 # Added process memory metric


class HealthMonitor:
    def __init__(self, monitoring_interval: int = 60, history_limit: int = 100):
        self.logger = get_logger('health_monitor')
        self.monitoring_interval = monitoring_interval
        self.history_limit = history_limit
        self.start_time = time.time()
        self.stop_event = threading.Event()
        self.monitoring_thread = None
        self.health_history: List[HealthStatus] = []
        self.metrics_history: List[SystemMetrics] = []

        # Initialize circuit breaker and retry handler
        self.circuit_breaker = get_mathpix_circuit_breaker()
        self.retry_handler = get_mathpix_retry_handler()
        # Initialize paths
        self.paths = get_paths() # Initialize paths

        self.logger.info("Health monitor initialized")

    def start_monitoring(self):
        """Start the health monitoring loop in a separate thread."""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.logger.warning("Monitoring thread already running")
            return

        self.stop_event.clear()
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("Health monitoring started")

    def stop_monitoring(self):
        """Stop the health monitoring loop."""
        self.stop_event.set()
        if self.monitoring_thread:
            self.monitoring_thread.join()
        self.logger.info("Health monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop running in a separate thread."""
        while not self.stop_event.is_set():
            try:
                # Perform health check
                health_status = self.perform_health_check()
                self._record_health_status(health_status)

                # Collect system metrics
                metrics = self._collect_system_metrics()
                self._record_metrics(metrics)

                # Log summary
                self._log_health_summary(health_status, metrics)

                # Wait for next interval
                self.stop_event.wait(timeout=self.monitoring_interval)

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                # Consider adding a brief sleep to prevent rapid retries on error
                time.sleep(min(5, self.monitoring_interval)) # Sleep briefly on error

    def get_current_health(self) -> Optional[HealthStatus]:
        """Get the most recent health status."""
        if self.health_history:
            return self.health_history[-1]
        return None

    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """Get the most recent system metrics."""
        if self.metrics_history:
            return self.metrics_history[-1]
        return None

    def get_health_report(self) -> Dict[str, Any]:
        """Generate a comprehensive health report."""
        current_health = self.get_current_health()
        recent_metrics = self.metrics_history[-10:] if self.metrics_history else []
        
        # Calculate trends
        if len(recent_metrics) >= 2:
            uptime_trend = recent_metrics[-1].uptime_seconds - recent_metrics[0].uptime_seconds
            failure_trend = recent_metrics[-1].failed_requests - recent_metrics[0].failed_requests
        else:
            uptime_trend = 0
            failure_trend = 0

        return {
            'current_status': asdict(current_health) if current_health else None,
            'recent_metrics': [asdict(m) for m in recent_metrics],
            'trends': {
                'uptime_seconds': uptime_trend,
                'failure_trend': failure_trend,
            },
            'alerts': self._generate_alerts(current_health, recent_metrics),
            'recommendations': current_health.recommendations if current_health else []
        }

    def _generate_alerts(self, health_status: Optional[HealthStatus], metrics: List[SystemMetrics]) -> List[Dict[str, Any]]:
        """Generate alerts based on health status and metrics."""
        alerts = []

        if health_status and not health_status.healthy:
            alerts.append({
                'level': 'CRITICAL',
                'message': f"System health degraded: {health_status.status}",
                'timestamp': health_status.timestamp
            })

        if metrics:
            latest = metrics[-1]
            # Check process memory specifically
            if latest.process_memory_mb > 1500: # Example threshold for process memory
                alerts.append({
                    'level': 'WARNING',
                    'message': f"High process memory usage: {latest.process_memory_mb:.1f}MB",
                    'timestamp': latest.timestamp
                })
            # Check system memory
            if latest.memory_usage_mb > 1000: # > 1GB system memory used
                alerts.append({
                    'level': 'WARNING',
                    'message': f"High system memory usage: {latest.memory_usage_mb:.1f}MB",
                    'timestamp': latest.timestamp
                })
            if latest.disk_usage_percent > 90:
                alerts.append({
                    'level': 'CRITICAL',
                    'message': f"Disk space critically low: {latest.disk_usage_percent:.1f}%",
                    'timestamp': latest.timestamp
                })
            # Check CPU usage
            if latest.cpu_usage_percent > 95:
                 alerts.append({
                    'level': 'WARNING',
                    'message': f"High CPU usage: {latest.cpu_usage_percent:.1f}%",
                    'timestamp': latest.timestamp
                })
            if latest.circuit_breaker_state == 'open':
                alerts.append({
                    'level': 'CRITICAL',
                    'message': "Mathpix circuit breaker is OPEN - API may be unavailable",
                    'timestamp': latest.timestamp
                })

        return alerts

    def get_service_availability(self) -> Dict[str, Any]:
        """Get service availability report."""
        availability_data = {}
        # Example: Check if output directories exist and are writable
        critical_dirs = [self.paths.output_dir, self.paths.logs_dir, self.paths.cache_dir]
        dir_status = {}
        for dir_path in critical_dirs:
             dir_status[str(dir_path)] = {
                 'exists': dir_path.exists(),
                 'writable': dir_path.exists() and os.access(dir_path, os.W_OK)
             }
        availability_data['critical_directories'] = dir_status
        # Add other service checks here if needed (e.g., Mathpix API ping)
        return availability_data

    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect comprehensive system metrics."""
        # Basic metrics
        current_time = time.time()
        uptime = current_time - self.start_time

        # Circuit breaker metrics
        cb_stats = self.circuit_breaker.circuit_breaker.get_stats()
        circuit_state = cb_stats['state']
        circuit_failures = cb_stats['total_failures']

        # Retry metrics
        retry_metrics = self.retry_handler.get_metrics()
        total_requests = retry_metrics.get('total_requests', 0)
        successful_requests = retry_metrics.get('successful_requests', 0)
        failed_requests = retry_metrics.get('failed_requests', 0)
        retry_count = retry_metrics.get('retry_attempts', 0)
        retry_success_rate = (retry_count / total_requests * 100) if total_requests > 0 else 0.0

        # System metrics
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        # CPU usage (1-second average) - Note: psutil.cpu_percent() should ideally be called with an interval
        # For continuous monitoring in a loop, calling it without an interval uses the difference since the last call
        cpu_percent = psutil.cpu_percent(interval=None) # Use difference since last call
        
        # Process-specific metrics
        process = psutil.Process()
        memory_info = process.memory_info()
        process_memory_mb = memory_info.rss / 1024 / 1024 # Resident Set Size in MB

        return SystemMetrics(
            timestamp=datetime.now().isoformat(),
            uptime_seconds=uptime,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            retry_count=retry_count,
            retry_success_rate=retry_success_rate,
            memory_usage_mb=memory.used / 1024 / 1024, # Total system memory used in MB
            disk_usage_percent=(disk.used / disk.total) * 100,
            cpu_usage_percent=cpu_percent, # Add CPU usage
            circuit_breaker_state=circuit_state,
            circuit_breaker_failures=circuit_failures,
            process_memory_mb=process_memory_mb # Add process memory
        )

    def _record_health_status(self, health_status: HealthStatus):
        """Record health status to history."""
        self.health_history.append(health_status)
        # Keep only recent history
        if len(self.health_history) > self.history_limit:
            self.health_history.pop(0) # Remove oldest entry

    def _record_metrics(self, metrics: SystemMetrics):
        """Record system metrics to history."""
        self.metrics_history.append(metrics)
        # Keep only recent history
        if len(self.metrics_history) > self.history_limit:
            self.metrics_history.pop(0) # Remove oldest entry

    def _log_health_summary(self, health_status: HealthStatus, metrics: SystemMetrics):
        """Log a summary of current health and metrics."""
        status_str = "HEALTHY" if health_status.healthy else "UNHEALTHY"
        if not health_status.healthy and "DEGRADED" in [d.get('status', '') for d in health_status.details.values()]:
             status_str = "DEGRADED" # Refine status based on details if needed

        self.logger.info(
            f"Health: {status_str} | "
            f"Circuit: {metrics.circuit_breaker_state} | "
            f"Uptime: {metrics.uptime_seconds:.1f}s | "
            f"Memory: {metrics.memory_usage_mb:.1f}MB | "
            f"CPU: {metrics.cpu_usage_percent:.1f}% | "
            f"Disk: {metrics.disk_usage_percent:.1f}% | "
            f"Retries: {metrics.retry_count} ({metrics.retry_success_rate:.1f}%)"
        )
        # Log recommendations if any
        if health_status.recommendations:
            for rec in health_status.recommendations:
                self.logger.info(f"Recommendation: {rec}")


    def perform_health_check(self) -> HealthStatus:
        """Perform comprehensive health check."""
        checks = {}

        # Mathpix Circuit Breaker Health
        try:
            cb_health = self.circuit_breaker.get_health_report()
            checks['circuit_breaker'] = cb_health
        except Exception as e:
            checks['circuit_breaker'] = {'healthy': False, 'error': str(e)}

        # Retry Handler Health
        try:
            retry_health = self.retry_handler.health_check() # Placeholder - check actual method name
            checks['retry_handler'] = retry_health
        except Exception as e:
            checks['retry_handler'] = {'healthy': False, 'error': str(e)}

        # System-level Health
        try:
            sys_health = self._check_system_health()
            checks['system'] = sys_health
        except Exception as e:
            checks['system'] = {'healthy': False, 'error': str(e)}

        # Overall health determination
        healthy_components = sum(1 for check in checks.values() if check.get('healthy', False))
        total_components = len(checks)
        overall_healthy = healthy_components == total_components

        if overall_healthy:
            status = "HEALTHY"
        elif healthy_components >= (total_components * 0.4): # Threshold for degraded
            status = "DEGRADED"
        else:
            status = "UNHEALTHY"

        # Collect recommendations
        recommendations = []
        for component, check in checks.items():
            if 'recommendations' in check:
                for rec in check['recommendations']:
                    recommendations.append(f"{component}: {rec}")

        return HealthStatus(
            service="maxwell_em_processor",
            status=status,
            healthy=overall_healthy,
            timestamp=datetime.now().isoformat(),
            details=checks,
            recommendations=recommendations
        )

    def _check_system_health(self) -> Dict[str, Any]:
        """Check system-level health indicators."""
        try:
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage_percent = memory.percent

            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100

            # CPU usage (Note: psutil.cpu_percent() behavior in a loop - see _collect_system_metrics)
            cpu_usage = psutil.cpu_percent(interval=None) # Uses difference since last call

            # Process info (already collected in _collect_system_metrics, but can be repeated here if needed)
            # process = psutil.Process()
            # memory_info = process.memory_info()
            # memory_mb = memory_info.rss / 1024 / 1024

            # Service availability (directories checked in get_service_availability)
            services_healthy = all(
                v['writable'] for v in self.get_service_availability().get('critical_directories', {}).values()
            )

            system_healthy = (
                memory_usage_percent < 90 and
                disk_usage_percent < 90 and
                cpu_usage < 95 and # Adjust threshold as needed
                services_healthy
            )

            return {
                'healthy': system_healthy,
                'memory_usage_percent': memory_usage_percent,
                'disk_usage_percent': disk_usage_percent,
                'cpu_usage_percent': cpu_usage, # Include CPU in system check
                'services_available': services_healthy,
                'recommendations': self._get_system_recommendations(memory_usage_percent, disk_usage_percent, cpu_usage)
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'recommendations': ['System monitoring unavailable']
            }

    def _get_system_recommendations(self, memory_percent: float, disk_percent: float, cpu_percent: float) -> List[str]:
        """Generate system-level recommendations."""
        recommendations = []
        if memory_percent > 80:
            recommendations.append("High memory usage detected - consider optimizing memory usage or increasing resources")
        if disk_percent > 80:
            recommendations.append("High disk usage detected - clean up temporary files or increase storage")
        if cpu_percent > 80:
            recommendations.append("High CPU usage detected - check for resource-intensive processes")
        return recommendations


# Global instance
_health_monitor = None


def get_health_monitor() -> HealthMonitor:
    """Get the global health monitor instance."""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor


if __name__ == '__main__':
    monitor = get_health_monitor()
    print("Health monitor initialized")
    print("Starting monitoring...")
    monitor.start_monitoring()
    try:
        while True:
            time.sleep(10) # Keep the main thread alive to observe logs
            # Example: Print current health occasionally
            # current_health = monitor.get_current_health()
            # if current_health:
            #     print(f"Current Health: {current_health.status}")
    except KeyboardInterrupt:
        print("\nStopping monitoring...")
        monitor.stop_monitoring()
        print("Monitoring stopped.")
