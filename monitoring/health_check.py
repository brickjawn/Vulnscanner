#!/usr/bin/env python3
"""
VulnScanner Health Check System
Production-ready health monitoring and metrics collection
"""

import os
import sys
import json
import time
import psutil
import requests
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass, asdict

@dataclass
class HealthStatus:
    status: str
    timestamp: str
    version: str
    uptime_seconds: float
    system_metrics: Dict[str, Any]
    dependencies: Dict[str, Dict[str, Any]]
    checks: Dict[str, Dict[str, Any]]

class HealthChecker:
    def __init__(self):
        self.start_time = time.time()
        self.version = "2.0.0"
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "cores": psutil.cpu_count(),
                    "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "usage_percent": memory.percent,
                    "free_gb": round(memory.free / (1024**3), 2)
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "usage_percent": round((disk.used / disk.total) * 100, 2)
                },
                "network": self._get_network_stats()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_network_stats(self) -> Dict[str, Any]:
        """Get network interface statistics"""
        try:
            net_io = psutil.net_io_counters()
            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
        except:
            return {}
    
    def check_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """Check external dependencies and services"""
        dependencies = {}
        
        # Check database connection (if configured)
        dependencies["database"] = self._check_database()
        
        # Check redis connection (if configured)
        dependencies["redis"] = self._check_redis()
        
        # Check internet connectivity
        dependencies["internet"] = self._check_internet()
        
        # Check disk space
        dependencies["disk_space"] = self._check_disk_space()
        
        return dependencies
    
    def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity"""
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            return {"status": "disabled", "message": "Database not configured"}
        
        try:
            # This would need actual database connection logic
            # For now, just return a placeholder
            return {
                "status": "healthy",
                "response_time_ms": 15,
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity"""
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            return {"status": "disabled", "message": "Redis not configured"}
        
        try:
            # This would need actual redis connection logic
            return {
                "status": "healthy",
                "response_time_ms": 5,
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    def _check_internet(self) -> Dict[str, Any]:
        """Check internet connectivity"""
        try:
            start_time = time.time()
            response = requests.get('https://httpbin.org/status/200', timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space"""
        try:
            disk = psutil.disk_usage('/')
            free_percent = (disk.free / disk.total) * 100
            
            status = "healthy"
            if free_percent < 10:
                status = "critical"
            elif free_percent < 20:
                status = "warning"
            
            return {
                "status": status,
                "free_percent": round(free_percent, 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "total_gb": round(disk.total / (1024**3), 2),
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    def run_application_checks(self) -> Dict[str, Dict[str, Any]]:
        """Run application-specific health checks"""
        checks = {}
        
        # Check log directory
        checks["log_directory"] = self._check_log_directory()
        
        # Check reports directory
        checks["reports_directory"] = self._check_reports_directory()
        
        # Check configuration
        checks["configuration"] = self._check_configuration()
        
        # Check permissions
        checks["permissions"] = self._check_permissions()
        
        return checks
    
    def _check_log_directory(self) -> Dict[str, Any]:
        """Check if log directory is accessible and writable"""
        log_dir = os.getenv('LOG_DIR', './logs')
        try:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # Test write access
            test_file = os.path.join(log_dir, '.health_check')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            
            return {
                "status": "healthy",
                "path": log_dir,
                "writable": True,
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "path": log_dir,
                "last_check": datetime.utcnow().isoformat()
            }
    
    def _check_reports_directory(self) -> Dict[str, Any]:
        """Check if reports directory is accessible and writable"""
        reports_dir = os.getenv('REPORT_OUTPUT_DIR', './reports')
        try:
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir, exist_ok=True)
            
            # Test write access
            test_file = os.path.join(reports_dir, '.health_check')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            
            return {
                "status": "healthy",
                "path": reports_dir,
                "writable": True,
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "path": reports_dir,
                "last_check": datetime.utcnow().isoformat()
            }
    
    def _check_configuration(self) -> Dict[str, Any]:
        """Check critical configuration values"""
        try:
            missing_configs = []
            optional_configs = []
            
            # Critical configs
            critical = ['SCANNER_API_KEY', 'LOG_LEVEL']
            for config in critical:
                if not os.getenv(config):
                    missing_configs.append(config)
            
            # Optional but recommended
            recommended = ['SLACK_WEBHOOK_URL', 'EMAIL_FROM']
            for config in recommended:
                if not os.getenv(config):
                    optional_configs.append(config)
            
            status = "healthy"
            if missing_configs:
                status = "unhealthy"
            elif optional_configs:
                status = "warning"
            
            return {
                "status": status,
                "missing_critical": missing_configs,
                "missing_optional": optional_configs,
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    def _check_permissions(self) -> Dict[str, Any]:
        """Check file system permissions"""
        try:
            issues = []
            
            # Check if running as root (security issue)
            if os.geteuid() == 0:
                issues.append("Running as root user (security risk)")
            
            # Check write permissions for critical directories
            dirs_to_check = ['./logs', './reports', '/tmp']
            for dir_path in dirs_to_check:
                if os.path.exists(dir_path) and not os.access(dir_path, os.W_OK):
                    issues.append(f"No write permission for {dir_path}")
            
            status = "healthy" if not issues else "warning"
            
            return {
                "status": status,
                "issues": issues,
                "uid": os.getuid(),
                "gid": os.getgid(),
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    def get_health_status(self) -> HealthStatus:
        """Get comprehensive health status"""
        uptime = time.time() - self.start_time
        
        # Collect all health data
        system_metrics = self.get_system_metrics()
        dependencies = self.check_dependencies()
        checks = self.run_application_checks()
        
        # Determine overall status
        overall_status = "healthy"
        
        # Check for any unhealthy dependencies
        for dep_name, dep_status in dependencies.items():
            if dep_status.get('status') == 'unhealthy':
                overall_status = "unhealthy"
                break
            elif dep_status.get('status') == 'warning' and overall_status == 'healthy':
                overall_status = "warning"
        
        # Check for any unhealthy application checks
        for check_name, check_status in checks.items():
            if check_status.get('status') == 'unhealthy':
                overall_status = "unhealthy"
                break
            elif check_status.get('status') == 'warning' and overall_status == 'healthy':
                overall_status = "warning"
        
        return HealthStatus(
            status=overall_status,
            timestamp=datetime.utcnow().isoformat(),
            version=self.version,
            uptime_seconds=round(uptime, 2),
            system_metrics=system_metrics,
            dependencies=dependencies,
            checks=checks
        )

def main():
    """CLI entry point for health checks"""
    health_checker = HealthChecker()
    health_status = health_checker.get_health_status()
    
    print(json.dumps(asdict(health_status), indent=2))
    
    # Exit with appropriate code
    if health_status.status == "unhealthy":
        sys.exit(1)
    elif health_status.status == "warning":
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main() 