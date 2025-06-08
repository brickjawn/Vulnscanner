# VulnScanner v2.0

**Advanced Penetration Testing Toolkit for Web Applications and Networks**

![VulnScanner](https://img.shields.io/badge/VulnScanner-v2.0-red?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.7+-blue?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker)
![License](https://img.shields.io/badge/License-Educational-green?style=for-the-badge)
[![Docker Pulls](https://img.shields.io/docker/pulls/vulnscanner/vulnscanner?style=for-the-badge)](https://hub.docker.com/r/vulnscanner/vulnscanner)
[![GitHub Stars](https://img.shields.io/github/stars/your-username/vulnscanner?style=for-the-badge)](https://github.com/your-username/vulnscanner/stargazers)

## 📚 Table of Contents

- [🚀 Features](#-features)
- [⚡ Quick Start](#-quick-start)
- [📋 Requirements](#-requirements)
- [🔧 Installation](#-quick-installation)
- [🎯 Usage](#-usage)
- [📊 Output Examples](#-output-examples)
- [⚙️ Configuration](#-configuration-options)
- [🐳 Docker Best Practices](#-docker-best-practices)
- [🛡️ Security Features](#️-security-features)
- [📁 Project Structure](#-project-structure)
- [🤝 Contributing](#-contributing)
- [🚨 Legal Disclaimer](#-legal-disclaimer)

## ⚡ Quick Start

**Get up and running in 30 seconds with Docker:**

```bash
# One-liner scan using Docker
docker run -it --rm vulnscanner/vulnscanner:latest --url https://example.com

# With custom options
docker run -it --rm vulnscanner/vulnscanner:latest \
  --url https://testsite.com --threads 10 --enable-portscan
```

**Traditional installation:**
```bash
git clone https://github.com/your-username/vulnscanner.git
cd vulnscanner && chmod +x install.sh && sudo ./install.sh
./vulnscan --url https://example.com
```

## 🚀 Features

### Core Capabilities
- **Multi-threaded Port Scanning** with Nmap integration
- **Intelligent Web Crawling** with form discovery
- **XSS Vulnerability Detection** with multiple payload variants
- **SQL Injection Testing** supporting multiple databases
- **Real-time Progress Tracking** with detailed output
- **Multiple Output Formats** (CLI, JSON, CSV)

### Enhanced User Experience
- **Modern GUI Interface** with progress bars and real-time updates
- **Comprehensive CLI** with colored output and progress indicators
- **Detailed Vulnerability Reporting** with remediation advice
- **Cross-platform Support** (Linux, macOS, Windows)
- **Easy Installation** with automated setup script

### Advanced Features
- **Intelligent Form Detection** and testing
- **Multiple Vulnerability Payloads** for better detection rates
- **Time-based and Error-based** SQL injection detection
- **Concurrent Testing** for improved speed
- **Respectful Crawling** with configurable delays
- **Export Capabilities** with timestamp and scan metadata

## 📋 Requirements

- **Python 3.7+**
- **Nmap** (for port scanning)
- **Internet Connection** (for target testing)
- **Linux/macOS/Windows** (tested on Ubuntu 20.04+)
- **Docker** (optional, for containerized deployment)

## 🔧 Quick Installation

### Docker Installation (Recommended)
```bash
# Pull and run the container
docker pull vulnscanner/vulnscanner:latest
docker run -it --rm vulnscanner/vulnscanner:latest --url https://example.com

# Or build from source
git clone https://github.com/your-username/vulnscanner.git
cd vulnscanner
docker build -t vulnscanner .
docker run -it --rm vulnscanner --url https://example.com

# Pull specific version
docker pull vulnscanner/vulnscanner:v2.0
```

### Automated Installation
```bash
git clone https://github.com/your-username/vulnscanner.git
cd vulnscanner
chmod +x install.sh
sudo ./install.sh  # Run with sudo for system dependencies
```

### Manual Installation
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install nmap python3-pip python3-venv

# Clone and setup
git clone https://github.com/your-username/vulnscanner.git
cd vulnscanner

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

## 🎯 Usage

### Docker Usage

#### Basic Docker Scan
```bash
docker run -it --rm vulnscanner/vulnscanner:latest --url https://example.com
```

#### Advanced Docker Scan with Volume Mounting
```bash
# Mount current directory to save reports
docker run -it --rm -v $(pwd):/app/reports vulnscanner/vulnscanner:latest \
  --url https://testsite.com \
  --threads 10 \
  --max-pages 20 \
  --timeout 10 \
  --enable-portscan \
  --output json > reports/scan-report.json
```

#### Docker with GUI (X11 forwarding on Linux)
```bash
docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix \
  vulnscanner/vulnscanner:latest python gui.py
```

### Command Line Interface (CLI)

#### Basic Scan
```bash
./vulnscan --url https://example.com
```

#### Advanced Scan with All Features
```bash
./vulnscan --url https://testsite.com \
          --threads 10 \
          --max-pages 20 \
          --timeout 10 \
          --enable-portscan \
          --output json
```

#### Quick Examples
```bash
# Scan with port scanning enabled
./vulnscan --url https://example.com --enable-portscan

# High-speed scan with 15 threads
./vulnscan --url https://target.com --threads 15 --max-pages 50

# Generate JSON report
./vulnscan --url https://example.com --output json > report.json

# CSV output for spreadsheet analysis
./vulnscan --url https://target.com --output csv
```

### Graphical User Interface (GUI)

```bash
./vulnscan-gui
```

The GUI provides:
- **Easy Configuration** with visual controls
- **Real-time Progress** monitoring
- **Live Output** with color-coded messages
- **Export Options** with save dialog
- **Scan Statistics** display

## 📊 Output Examples

### CLI Output
```
╔══════════════════════════════════════════════════════════════════╗
║                          VulnScanner v2.0                       ║
║                Advanced Penetration Testing Toolkit             ║
║                   For authorized testing only                    ║
╚══════════════════════════════════════════════════════════════════╝

[✓] Target: https://example.com
[✓] Threads: 10
[✓] Max Pages: 20
[✓] Timeout: 5s

[*] Starting port scan for: example.com
Port Scanning: 100%|████████████████████| 1000/1000 [00:30<00:00, 33.33ports/s]
[✓] Found 3 open ports

[*] Crawling https://example.com for forms and links...
Crawling: 100%|████████████████████████| 15/15 [00:45<00:00, 0.33pages/s]
[✓] Found 8 forms across 15 pages

[*] Testing for XSS vulnerabilities...
XSS Testing: 100%|███████████████████████| 8/8 [01:20<00:00, 10.0forms/s]
[!] XSS Found: https://example.com/search - Field: query

[*] Testing for SQL Injection vulnerabilities...
SQLi Testing: 100%|██████████████████████| 8/8 [02:15<00:00, 5.9forms/s]
[!] SQLi Found: https://example.com/login - Field: username - Type: Error-based SQLi

[*] Scan completed in 245.67 seconds
[✓] Found 5 total findings
```

### JSON Output Structure
```json
{
  "scan_info": {
    "target": "https://example.com",
    "timestamp": "2024-01-15 14:30:25",
    "duration_seconds": 245.67,
    "total_findings": 5
  },
  "findings": [
    {
      "type": "XSS",
      "url": "https://example.com/search",
      "details": "Possible XSS in field 'query' at https://example.com/search",
      "payload": "<script>alert('xss')</script>",
      "method": "GET",
      "severity": "high"
    }
  ],
  "summary": {
    "critical": 2,
    "high": 1,
    "medium": 0,
    "low": 0,
    "info": 2
  }
}
```

## ⚙️ Configuration Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--url` | Target URL to scan | Required | `https://example.com` |
| `--threads` | Number of concurrent threads | 5 | `--threads 10` |
| `--max-pages` | Maximum pages to crawl | 10 | `--max-pages 50` |
| `--timeout` | Request timeout (seconds) | 5 | `--timeout 15` |
| `--enable-portscan` | Enable Nmap port scanning | False | `--enable-portscan` |
| `--output` | Output format (cli/json/csv) | cli | `--output json` |

### Docker Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `SCANNER_THREADS` | Default number of threads | 5 | `-e SCANNER_THREADS=10` |
| `SCANNER_TIMEOUT` | Default request timeout | 5 | `-e SCANNER_TIMEOUT=15` |
| `SCANNER_MAX_PAGES` | Default max pages to crawl | 10 | `-e SCANNER_MAX_PAGES=50` |
| `SCANNER_OUTPUT_FORMAT` | Default output format | cli | `-e SCANNER_OUTPUT_FORMAT=json` |

```bash
# Example with environment variables
docker run -it --rm \
  -e SCANNER_THREADS=15 \
  -e SCANNER_TIMEOUT=10 \
  -e SCANNER_OUTPUT_FORMAT=json \
  vulnscanner/vulnscanner:latest --url https://example.com
```

## 🛡️ Security Features

### Vulnerability Detection
- **Cross-Site Scripting (XSS)**
  - Reflected XSS detection
  - Multiple payload variants
  - Context-aware testing
  
- **SQL Injection**
  - Error-based detection
  - Time-based blind testing
  - Multiple database support (MySQL, PostgreSQL, MSSQL, Oracle, SQLite)
  
- **Network Reconnaissance**
  - Fast port scanning with Nmap
  - Service version detection
  - Common port identification

### Smart Testing Approach
- **Intelligent Crawling**: Avoids non-HTML content and infinite loops
- **Form Analysis**: Identifies and tests all input fields appropriately
- **Payload Optimization**: Uses targeted payloads for different vulnerability types
- **Rate Limiting**: Respectful scanning with configurable delays

## 📁 Project Structure

```
vulnscanner/
├── main.py                 # CLI entry point
├── gui.py                  # GUI application
├── install.sh              # Installation script
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker container configuration
├── docker-compose.yml      # Docker Compose configuration
├── .dockerignore           # Docker ignore patterns
├── README.md              # Documentation
├── scanner/               # Core scanning modules
│   ├── __init__.py
│   ├── crawler.py         # Web crawling functionality
│   ├── portscan.py        # Port scanning with Nmap
│   ├── xss.py             # XSS vulnerability testing
│   ├── sqli.py            # SQL injection testing
│   ├── parallel.py        # Multi-threading support
│   └── report.py          # Report generation
├── reports/               # Output directory for scan reports
└── venv/                  # Virtual environment (created by installer)
```

## 🔍 Methodology

### Scanning Process
1. **Target Validation** - URL normalization and accessibility check
2. **Port Scanning** - Network reconnaissance with Nmap (optional)
3. **Web Crawling** - Systematic discovery of pages and forms
4. **Vulnerability Testing** - Parallel testing for XSS and SQLi
5. **Report Generation** - Comprehensive results with remediation advice

### Testing Approach
- **Non-destructive**: Read-only testing that doesn't modify target data
- **Efficient**: Multi-threaded execution for faster results
- **Comprehensive**: Multiple payload types for better coverage
- **Respectful**: Built-in delays to avoid overwhelming target servers

## 🐳 Docker Best Practices

### Security Considerations
- **Run as non-root user**: The container runs as a non-privileged user for security
- **Read-only filesystem**: Use `--read-only` flag for additional security
- **Resource limits**: Set memory and CPU limits in production

```bash
# Security-hardened Docker run
docker run -it --rm \
  --read-only \
  --tmpfs /tmp \
  --memory=512m \
  --cpus=1.0 \
  --security-opt=no-new-privileges \
  --user nobody \
  vulnscanner/vulnscanner:latest --url https://example.com
```

### Production Deployment
```bash
# Using Docker Compose for production
version: '3.8'
services:
  vulnscanner:
    image: vulnscanner/vulnscanner:latest
    read_only: true
    tmpfs:
      - /tmp
    mem_limit: 512m
    cpus: 1.0
    security_opt:
      - no-new-privileges
    environment:
      - SCANNER_THREADS=10
      - SCANNER_TIMEOUT=15
    volumes:
      - ./reports:/app/reports:rw
```

## 🚨 Legal Disclaimer

**⚠️ IMPORTANT: This tool is for authorized testing only!**

- Only test systems you own or have explicit permission to test
- Unauthorized access to computer systems is illegal
- Users are responsible for complying with applicable laws
- The authors assume no liability for misuse of this tool

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:

- Bug fixes and improvements
- New vulnerability detection modules
- Enhanced reporting features
- Documentation updates
- Docker image optimizations
- CI/CD pipeline improvements

### Development Setup

#### Traditional Setup
```bash
git clone https://github.com/your-username/vulnscanner.git
cd vulnscanner
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Docker Development Setup
```bash
git clone https://github.com/your-username/vulnscanner.git
cd vulnscanner

# Build development container
docker build -t vulnscanner-dev .

# Run with development volume mounting
docker run -it --rm -v $(pwd):/app vulnscanner-dev bash
```

#### Docker Compose for Development
```bash
# Start development environment
docker-compose up -d

# Execute scans through compose
docker-compose run scanner --url https://example.com

# Stop environment
docker-compose down
```

## 📄 License

This project is licensed for educational and authorized testing purposes only. See the repository for full license terms.

## 📞 Support

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: Comprehensive examples in this README
- **Community**: Join discussions in the Issues section

---

**Remember: Ethical hacking requires permission. Always ensure you have authorization before testing any system.**