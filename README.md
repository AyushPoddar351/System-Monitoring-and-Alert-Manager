# System Monitoring with Alerting

Complete Windows system monitoring solution using Prometheus, Alertmanager, and real-time HTML dashboard.

## 🚀 Quick Start

1. **Run the monitoring system:**
   ```cmd
   python monitoring-automation.py
   ```

2. **Access the dashboard:**
   - HTML Dashboard opens automatically
   - Shows real-time metrics and alerts

## 📁 Project Structure

```
Prj-with-alert/
├── monitoring-automation.py    # Main launcher script
├── dashboard.html             # Real-time monitoring dashboard
├── prometheus.yml            # Prometheus configuration
├── alert_rules.yml          # Alert rules definition
├── prometheus-3.7.2.windows-amd64/
│   └── prometheus.exe       # Prometheus server
├── alertmanager-0.28.1.windows-amd64/
│   ├── alertmanager.exe     # Alertmanager server
│   └── alertmanager.yml     # Alert routing config
└── requirements.txt         # Python dependencies
```

## 🔧 Components

- **Windows Exporter**: Collects system metrics (CPU, Memory, Disk, Network)
- **Prometheus**: Time-series database and monitoring server
- **Alertmanager**: Handles alerts and notifications
- **HTML Dashboard**: Real-time visualization with charts and alerts

## 🚨 Alert Rules

- **HighCPUUsage**: CPU > 85% for 1 minute
- **LowMemory**: Memory > 90% for 2 minutes  
- **DiskAlmostFull**: Free space < 20% for 10 seconds

## 📊 Features

- Real-time system metrics
- Interactive charts and gauges
- Alert notifications in dashboard
- Auto-refresh every second
- Historical data tracking

## 🔗 Service URLs

- **HTML Dashboard**: Opens automatically
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093
- **Windows Exporter**: http://localhost:9182/metrics

## ⚙️ Requirements

- Windows OS
- Python 3.x
- Administrator privileges (for Windows Exporter service)
- Windows Exporter service installed

## 🛠️ Installation

1. Install Windows Exporter as a service
2. Extract Prometheus and Alertmanager to project folder
3. Install Python dependencies: `pip install requests`
4. Run: `python monitoring-automation.py`

## 📧 Email Alerts (Optional)

Edit `alertmanager-0.28.1.windows-amd64/alertmanager.yml`:
- Change `receiver: 'console'` to `receiver: 'email-alert'`
- Configure SMTP settings with your email credentials

## 🔄 Auto-Start

The script automatically:
1. Starts Windows Exporter service
2. Launches Alertmanager
3. Starts Prometheus with alert rules
4. Opens HTML dashboard
5. Monitors system continuously

Press `Ctrl+C` to stop all services.