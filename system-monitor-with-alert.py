"""
System Monitoring - Automated Launcher
Manages Prometheus, Windows Exporter, Alertmanager, and Dashboard for real-time system monitoring
"""

import subprocess
import time
import webbrowser
import os
import sys
import requests
import json
from pathlib import Path
from datetime import datetime

class MonitoringSystem:
    def __init__(self):
        # Configuration - Update these paths based on your installation
        self.prometheus_path = self._find_prometheus_executable()
        self.alertmanager_path = self._find_alertmanager_executable()
        self.windows_exporter_service = "windows_exporter"
        self.dashboard_path = os.path.join(os.getcwd(), "dashboard.html")
        self.config_file = os.path.join(os.getcwd(), "prometheus.yml")
        
        # Service URLs
        self.prometheus_url = "http://localhost:9090"
        self.alertmanager_url = "http://localhost:9093"
        self.exporter_url = "http://localhost:9182/metrics"
        
        # Process handles
        self.prometheus_process = None
        self.alertmanager_process = None
        
        # Logging
        self.log_file = os.path.join(os.getcwd(), "monitoring.log")
    
    def _find_prometheus_executable(self):
        """Try to find Prometheus executable in common locations"""
        possible_paths = [
            os.path.join(os.getcwd(), "prometheus-3.7.2.windows-amd64", "prometheus.exe"),
            r"E:\data\dsatm\7th sem\Workshop\Workshop-Project\prometheus-3.7.2.windows-amd64\prometheus.exe",
            os.path.join(os.getcwd(), "prometheus.exe"),
            r"C:\prometheus\prometheus.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return possible_paths[0]
    
    def _find_alertmanager_executable(self):
        """Try to find Alertmanager executable in common locations"""
        possible_paths = [
            os.path.join(os.getcwd(), "alertmanager-0.28.1.windows-amd64", "alertmanager.exe"),
            os.path.join(os.getcwd(), "alertmanager.exe"),
            r"C:\alertmanager\alertmanager.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return possible_paths[0]
    
    def log_message(self, message, status="INFO"):
        """Log message to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {status}: {message}\n"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except:
            pass
        
        self.print_status(message, status)
    
    def print_status(self, message, status="INFO"):
        """Print colored status messages"""
        colors = {
            "INFO": "\033[94m",    # Blue
            "SUCCESS": "\033[92m", # Green
            "WARNING": "\033[93m", # Yellow
            "ERROR": "\033[91m",   # Red
            "RESET": "\033[0m"
        }
        print(f"{colors.get(status, '')}{status}: {message}{colors['RESET']}")
    
    def check_service_running(self, service_name):
        """Check if a Windows service is running"""
        try:
            result = subprocess.run(
                ['sc', 'query', service_name],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return 'RUNNING' in result.stdout
        except Exception as e:
            self.log_message(f"Error checking service {service_name}: {e}", "ERROR")
            return False
    
    def start_windows_exporter(self):
        """Start Windows Exporter service"""
        self.log_message("Checking Windows Exporter service...", "INFO")
        
        if self.check_service_running(self.windows_exporter_service):
            self.log_message("Windows Exporter is already running", "SUCCESS")
            return True
        
        self.log_message("Starting Windows Exporter service...", "INFO")
        try:
            result = subprocess.run(
                ['sc', 'start', self.windows_exporter_service],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if "START_PENDING" in result.stdout or "RUNNING" in result.stdout:
                time.sleep(3)
                self.log_message("Windows Exporter started successfully", "SUCCESS")
                return True
            else:
                self.log_message(f"Failed to start Windows Exporter: {result.stdout}", "ERROR")
                return False
        except Exception as e:
            self.log_message(f"Error starting Windows Exporter: {e}", "ERROR")
            self.log_message("Try running this script as Administrator", "WARNING")
            return False
    
    def check_url_accessible(self, url, timeout=5):
        """Check if a URL is accessible"""
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except:
            return False
    
    def start_alertmanager(self):
        """Start Alertmanager process"""
        self.log_message("Checking Alertmanager...", "INFO")
        
        # Check if already running
        if self.check_url_accessible(self.alertmanager_url):
            self.log_message("Alertmanager is already running", "SUCCESS")
            return True
        
        # Check if executable exists
        if not os.path.exists(self.alertmanager_path):
            self.log_message(f"Alertmanager not found at: {self.alertmanager_path}", "ERROR")
            return False
        
        self.log_message("Starting Alertmanager...", "INFO")
        try:
            alertmanager_dir = os.path.dirname(self.alertmanager_path)
            config_path = os.path.join(alertmanager_dir, "alertmanager.yml")
            
            cmd = [self.alertmanager_path, f'--config.file={config_path}']
            
            self.alertmanager_process = subprocess.Popen(
                cmd,
                cwd=alertmanager_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Wait for Alertmanager to start
            max_retries = 10
            for i in range(max_retries):
                time.sleep(2)
                if self.check_url_accessible(self.alertmanager_url):
                    self.log_message("Alertmanager started successfully", "SUCCESS")
                    return True
                self.log_message(f"Waiting for Alertmanager... ({i+1}/{max_retries})", "INFO")
            
            self.log_message("Alertmanager failed to start within timeout", "ERROR")
            return False
            
        except Exception as e:
            self.log_message(f"Error starting Alertmanager: {e}", "ERROR")
            return False
    
    def start_prometheus(self):
        """Start Prometheus process"""
        self.log_message("Checking Prometheus...", "INFO")
        
        # Check if already running
        if self.check_url_accessible(self.prometheus_url):
            self.log_message("Prometheus is already running", "SUCCESS")
            return True
        
        # Check if executable exists
        if not os.path.exists(self.prometheus_path):
            self.log_message(f"Prometheus not found at: {self.prometheus_path}", "ERROR")
            return False
        
        self.log_message("Starting Prometheus...", "INFO")
        try:
            prom_dir = os.path.dirname(self.prometheus_path)
            
            # Start Prometheus with config file
            cmd = [self.prometheus_path, f'--config.file={self.config_file}']
            
            self.prometheus_process = subprocess.Popen(
                cmd,
                cwd=prom_dir if prom_dir else os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Wait for Prometheus to start
            max_retries = 15
            for i in range(max_retries):
                time.sleep(2)
                if self.check_url_accessible(self.prometheus_url):
                    self.log_message("Prometheus started successfully", "SUCCESS")
                    return True
                self.log_message(f"Waiting for Prometheus... ({i+1}/{max_retries})", "INFO")
            
            self.log_message("Prometheus failed to start within timeout", "ERROR")
            return False
            
        except Exception as e:
            self.log_message(f"Error starting Prometheus: {e}", "ERROR")
            return False
    
    def verify_services(self):
        """Verify all services are accessible"""
        self.log_message("Verifying services...", "INFO")
        
        services = {
            "Windows Exporter": self.exporter_url,
            "Prometheus": self.prometheus_url,
            "Alertmanager": self.alertmanager_url
        }
        
        all_ok = True
        for name, url in services.items():
            if self.check_url_accessible(url):
                self.log_message(f"✓ {name} is accessible at {url}", "SUCCESS")
            else:
                self.log_message(f"✗ {name} is NOT accessible at {url}", "ERROR")
                all_ok = False
        
        return all_ok
    
    def get_system_metrics(self):
        """Fetch and display current system metrics"""
        self.log_message("Fetching system metrics...", "INFO")
        
        queries = {
            "CPU Usage": '100 - (avg(rate(windows_cpu_time_total{mode="idle"}[1m])) * 100)',
            "Memory Usage": '100 - ((windows_memory_available_bytes / windows_memory_physical_total_bytes) * 100)',
            "Disk Usage": '100 - ((windows_logical_disk_free_bytes{volume="C:"} / windows_logical_disk_size_bytes{volume="C:"}) * 100)'
        }
        
        print("\n" + "="*60)
        print("  CURRENT SYSTEM METRICS")
        print("="*60)
        
        for name, query in queries.items():
            try:
                response = requests.get(
                    f"{self.prometheus_url}/api/v1/query",
                    params={"query": query},
                    timeout=5
                )
                data = response.json()
                if data['status'] == 'success' and data['data']['result']:
                    value = float(data['data']['result'][0]['value'][1])
                    print(f"  {name}: {value:.1f}%")
            except:
                print(f"  {name}: Unable to fetch")
        
        print("="*60 + "\n")
    
    def check_alerts(self):
        """Check current alert status"""
        try:
            response = requests.get(f"{self.prometheus_url}/api/v1/alerts", timeout=5)
            if response.status_code == 200:
                alerts = response.json()['data']['alerts']
                
                print("\n" + "="*60)
                print("  ALERT STATUS")
                print("="*60)
                
                if not alerts:
                    print("  No active alerts")
                else:
                    for alert in alerts:
                        status = alert['state']
                        name = alert['labels']['alertname']
                        severity = alert['labels'].get('severity', 'unknown')
                        print(f"  {name:<20}: {status.upper()} ({severity})")
                
                print("="*60)
            else:
                self.log_message("Failed to fetch alerts", "ERROR")
        except Exception as e:
            self.log_message(f"Error checking alerts: {e}", "ERROR")
    
    def open_dashboards(self):
        """Open monitoring dashboards in browser"""
        self.log_message("Opening monitoring dashboards...", "INFO")
        
        # Only open HTML dashboard
        try:
            dashboard_url = f'file:///{os.path.abspath(self.dashboard_path)}'
            webbrowser.open(dashboard_url)
            self.log_message(f"Opened HTML Dashboard: {dashboard_url}", "SUCCESS")
        except Exception as e:
            self.log_message(f"Failed to open HTML dashboard: {e}", "ERROR")
    
    def start_all_services(self):
        """Start all monitoring services"""
        self.log_message("Starting monitoring system...", "INFO")
        
        # Start services in order
        if not self.start_windows_exporter():
            return False
        
        if not self.start_alertmanager():
            return False
        
        if not self.start_prometheus():
            return False
        
        # Verify all services
        if self.verify_services():
            self.log_message("All services started successfully!", "SUCCESS")
            return True
        else:
            self.log_message("Some services failed to start", "ERROR")
            return False
    
    def stop_services(self):
        """Stop monitoring services"""
        self.log_message("Stopping monitoring services...", "INFO")
        
        if self.prometheus_process:
            self.prometheus_process.terminate()
            self.log_message("Prometheus stopped", "INFO")
        
        if self.alertmanager_process:
            self.alertmanager_process.terminate()
            self.log_message("Alertmanager stopped", "INFO")

def main():
    monitor = MonitoringSystem()
    
    try:
        print("\n" + "="*60)
        print("  SYSTEM MONITORING - AUTOMATED LAUNCHER")
        print("="*60)
        
        # Start all services
        if monitor.start_all_services():
            # Show current metrics
            monitor.get_system_metrics()
            
            # Check alerts
            monitor.check_alerts()
            
            # Open HTML dashboard only
            monitor.open_dashboards()
            
            print("\nMonitoring system is running!")
            print("Press Ctrl+C to stop...")
            
            # Keep running
            while True:
                time.sleep(30)
                monitor.check_alerts()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
        monitor.stop_services()
    except Exception as e:
        monitor.log_message(f"Unexpected error: {e}", "ERROR")
        monitor.stop_services()

if __name__ == "__main__":
    main()