# LoadTest Enterprise

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

**Enterprise Web Load Testing & Performance Analysis Suite**

Professional tool for authorized security testing and performance analysis.

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Supported Tools](#-supported-tools)
- [Reports](#-reports)
- [Web Panel](#-web-panel)
- [Examples](#-examples)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)
- [Disclaimer](#-disclaimer)

---

## 🎯 Overview

**LoadTest Enterprise** is a comprehensive web load testing and performance analysis suite designed for security professionals and DevOps teams. It provides advanced capabilities for stress testing, performance analysis, and security assessment of web applications and services.

### Key Capabilities

- **Multi-Tool Integration**: Supports 40+ industry-standard load testing tools
- **Intelligent Monitoring**: Real-time resource monitoring with automatic throttling
- **Advanced Reporting**: Comprehensive HTML reports with detailed metrics and recommendations
- **Web Interface**: Modern web panel for easy configuration and monitoring
- **Auto-Installation**: Automatic installation of required testing tools
- **Enterprise-Ready**: Professional design suitable for corporate environments

---

## ✨ Features

### Core Features

- 🔄 **Multiple Attack Modes**: MIXED, CONSTANT, BURST, RAMP_UP
- 📊 **Real-Time Monitoring**: CPU, memory, and network metrics
- 🎯 **Smart Resource Management**: Automatic throttling based on system resources
- 📈 **Comprehensive Reporting**: Detailed HTML reports with charts and recommendations
- 🌐 **Web Panel**: Modern web interface for configuration and monitoring
- 🔧 **Tool Auto-Installation**: Automatically installs missing testing tools
- 🛡️ **Security Features**: WAF bypass, stealth mode, proxy support
- ⚡ **High Performance**: Optimized for maximum throughput
- 📱 **Multi-Protocol**: HTTP/1.1, HTTP/2, WebSocket support
- 🎨 **Professional UI**: Corporate-ready design and branding

### Advanced Features

- **Connection Pooling**: Reusable connections for better performance
- **TCP Optimization**: Advanced TCP stack optimizations
- **HTTP/2 Multiplexing**: Support for HTTP/2 protocol
- **Rate Adaptive**: Dynamic rate adjustment based on server response
- **Memory Management**: Intelligent memory monitoring and throttling
- **Distributed Testing**: Support for multi-node distributed testing
- **Fingerprinting**: Automatic target fingerprinting and analysis
- **Vulnerability Detection**: Security header analysis and vulnerability detection

---

## 📦 Requirements

### System Requirements

- **Python**: 3.7 or higher
- **Operating System**: Windows, Linux, or macOS
- **RAM**: Minimum 2GB (4GB+ recommended)
- **Network**: Internet connection for target testing

### Python Dependencies

- Flask
- Flask-Cors
- requests
- urllib3
- psutil

### Optional Tools

The tool supports 40+ external testing tools. See [Supported Tools](#-supported-tools) for the complete list. Tools can be installed automatically using:

```bash
python loadtest.py --install-tools
```

---

## 🚀 Installation

### Quick Installation

#### Linux/macOS

```bash
# Clone the repository
git clone <repository-url>
cd loadtest-enterprise

# Run installation script
chmod +x install.sh
./install.sh
```

#### Windows

```bash
# Clone the repository
git clone <repository-url>
cd loadtest-enterprise

# Run installation script
install.bat
```

### Manual Installation

1. **Install Python dependencies:**

```bash
pip install -r requirements.txt
```

2. **Verify installation:**

```bash
python loadtest.py --show-tools
```

3. **Install testing tools (optional):**

```bash
python loadtest.py --install-tools
```

### Installation with Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

For detailed installation instructions, see [INSTALL.md](INSTALL.md).

---

## 🏃 Quick Start

### Basic Usage

```bash
# Run a basic load test
python loadtest.py -t https://example.com -d 60 -p MODERATE

# Start web panel
python loadtest.py --web

# Check available tools
python loadtest.py --show-tools

# Install missing tools
python loadtest.py --install-tools
```

### Web Panel

Start the web interface:

```bash
python loadtest.py --web
```

Then open your browser at: `http://localhost:5000`

---

## 📖 Usage

### Command Line Interface

#### Basic Syntax

```bash
python loadtest.py -t <target> [options]
```

#### Required Arguments

- `-t, --target`: Target URL or IP address

#### Common Options

```bash
# Duration and power level
-d, --duration <seconds>     Test duration (default: 60)
-p, --power <level>          Power level: TEST, LIGHT, MODERATE, MEDIUM, 
                             HEAVY, EXTREME, DEVASTATOR, APOCALYPSE, GODMODE

# Connections and threads
-c, --connections <num>      Maximum connections (default: 10000)
--threads <num>              Maximum threads (default: 400)

# Attack mode
-m, --mode <mode>            Attack mode: MIXED, CONSTANT, BURST, RAMP_UP

# Advanced options
--bypass-waf                 Enable WAF bypass techniques
--stealth                    Enable stealth mode
--large-payloads             Use large payloads
--no-auto-throttle           Disable automatic throttling
--no-memory-monitoring       Disable memory monitoring

# Other options
--web                        Start web panel
--web-port <port>            Web panel port (default: 5000)
--show-tools                 Show available tools status
--install-tools              Install missing tools
--show-params                Show all configurable parameters
--debug                      Enable debug mode
--dry-run                    Dry run (simulate without executing)
```

#### Examples

```bash
# Light test for 30 seconds
python loadtest.py -t https://example.com -d 30 -p LIGHT

# Heavy load test with custom connections
python loadtest.py -t https://example.com -d 120 -p HEAVY -c 20000 --threads 500

# Stealth mode with WAF bypass
python loadtest.py -t https://example.com -d 60 -p MODERATE --stealth --bypass-waf

# Burst attack mode
python loadtest.py -t https://example.com -d 60 -p MEDIUM -m BURST

# Web panel on custom port
python loadtest.py --web --web-port 8080
```

---

## ⚙️ Configuration

### Power Levels

| Level | Multiplier | Description |
|-------|-----------|-------------|
| TEST | 1x | Minimal load for testing |
| LIGHT | 3x | Light load |
| MODERATE | 8x | Moderate load (default) |
| MEDIUM | 16x | Medium load |
| HEAVY | 30x | Heavy load |
| EXTREME | 60x | Extreme load |
| DEVASTATOR | 120x | Very high load |
| APOCALYPSE | 250x | Maximum load |
| GODMODE | 500x | Extreme maximum load |

### Attack Modes

- **MIXED**: Combines multiple attack techniques
- **CONSTANT**: Constant rate of requests
- **BURST**: Burst pattern with intervals
- **RAMP_UP**: Gradually increasing load

### Memory Thresholds

- **Warning**: 60% - Early warning
- **Critical**: 75% - Immediate action
- **OOM**: 85% - Stop to prevent system restart
- **Emergency**: 90% - Aggressive process termination

---

## 🛠️ Supported Tools

LoadTest Enterprise supports 40+ industry-standard testing tools across multiple categories:

### HTTP Load Testing
- wrk, vegeta, bombardier, hey, ab, siege
- h2load, locust, k6, artillery, tsung, jmeter

### Layer 4 Testing
- hping3, nping, slowhttptest, masscan, zmap

### WebSocket Testing
- websocat, wscat

### Advanced Tools
- gatling, tsung, wrk2, drill, http2bench, weighttp, httperf, autocannon

### Specialized Tools
- goldeneye, hulk, slowloris, and more

### Tool Status

Check which tools are installed:

```bash
python loadtest.py --show-tools
```

Install missing tools automatically:

```bash
python loadtest.py --install-tools
```

---

## 📊 Reports

### Report Generation

Reports are automatically generated after each test run and saved in the `loadtest_output/reports/` directory.

### Report Contents

- **General Information**: Target, duration, power level
- **Statistics**: Requests sent, responses received, error rates
- **HTTP Codes**: Distribution of HTTP status codes
- **Latency Analysis**: P50, P75, P90, P95, P99 percentiles
- **Performance Metrics**: RPS, throughput, response times
- **Error Analysis**: Detailed error breakdown
- **Recommendations**: Actionable recommendations based on results
- **Charts**: Visual representation of metrics

### Viewing Reports

Reports are saved as HTML files. Open them in any web browser:

```bash
# Reports are saved in:
loadtest_output/reports/report_YYYYMMDD_HHMMSS.html
```

---

## 🌐 Web Panel

The web panel provides a modern interface for:

- **Configuration**: Easy setup of test parameters
- **Real-Time Monitoring**: Live statistics and metrics
- **Tool Management**: View and install testing tools
- **Report Viewing**: Browse and view generated reports
- **Fingerprinting**: Target analysis and recommendations
- **Attack Control**: Start/stop tests from the interface

### Starting the Web Panel

```bash
python loadtest.py --web
```

Access at: `http://localhost:5000`

---

## 💡 Examples

### Example 1: Basic Load Test

```bash
python loadtest.py -t https://api.example.com -d 60 -p MODERATE
```

### Example 2: Stress Test with Custom Settings

```bash
python loadtest.py -t https://example.com \
  -d 300 \
  -p HEAVY \
  -c 50000 \
  --threads 1000 \
  -m RAMP_UP
```

### Example 3: Security Testing

```bash
python loadtest.py -t https://example.com \
  -d 120 \
  -p MEDIUM \
  --stealth \
  --bypass-waf \
  --large-payloads
```

### Example 4: Web Panel Usage

```bash
# Start web panel
python loadtest.py --web

# Access in browser
# http://localhost:5000
```

---

## 🔧 Troubleshooting

### Common Issues

#### Issue: "No module named 'flask'"

**Solution:**
```bash
pip install Flask Flask-Cors
```

#### Issue: "Tool not found"

**Solution:**
```bash
# Install missing tools
python loadtest.py --install-tools

# Or install manually
# Linux: sudo apt install <tool-name>
# macOS: brew install <tool-name>
# Windows: choco install <tool-name>
```

#### Issue: "Permission denied"

**Solution:**
- On Linux/macOS, some tools may require sudo for installation
- Use virtual environment to avoid permission issues

#### Issue: "Memory errors"

**Solution:**
- Reduce power level: `-p LIGHT` or `-p MODERATE`
- Reduce connections: `-c 5000`
- Enable auto-throttle (default): Memory monitoring is enabled by default

#### Issue: "Web panel not starting"

**Solution:**
```bash
# Check if port is available
# Try different port
python loadtest.py --web --web-port 8080

# Check if loadtest_web.py exists
ls loadtest_web.py
```

For more troubleshooting help, see [INSTALL.md](INSTALL.md).

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contribution Guidelines

- Follow PEP 8 style guidelines
- Add comments for complex code
- Update documentation as needed
- Test your changes thoroughly
- Ensure backward compatibility

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

**IMPORTANT**: This tool is designed for **authorized security testing and performance analysis only**. 

- Only use on systems you own or have explicit written permission to test
- Unauthorized use of this tool may violate laws and regulations
- The authors and contributors are not responsible for misuse of this software
- Always comply with applicable laws and regulations
- Use responsibly and ethically

**By using this tool, you agree to use it only for legitimate purposes and accept full responsibility for your actions.**

---

## 📞 Support

- **Documentation**: See [INSTALL.md](INSTALL.md) for detailed installation instructions
- **Issues**: Report issues on the GitHub Issues page
- **Questions**: Open a discussion on GitHub Discussions

---

## 🙏 Acknowledgments

- All the developers of the supported testing tools
- The open-source community
- Security professionals who provided feedback

---

<div align="center">

**LoadTest Enterprise** - Professional Web Load Testing & Performance Analysis

Made with ❤️ for the security and DevOps community

</div>

