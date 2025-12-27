# VulnScanner

Dockerized web vulnerability scanner for authorized penetration testing.

## Features

- **XSS Detection** - Cross-Site Scripting vulnerability testing
- **SQL Injection** - Error-based, time-based, and blind SQLi detection
- **Form Crawling** - Automatic discovery of forms and input fields
- **Authentication** - Cookie and header support for authenticated scanning
- **Flexible Output** - CLI, JSON, and CSV formats

## Installation

### Build from Source

```bash
git clone https://github.com/yourusername/vulnscanner
cd vulnscanner
docker build -t vulnscanner .
```

### Pull from Docker Hub

```bash
docker pull yourusername/vulnscanner:latest
```

## Usage

### Basic Scan

```bash
docker run --rm vulnscanner --url https://example.com
```

### Authenticated Scan

```bash
docker run --rm vulnscanner \
  --url https://example.com \
  --cookie "PHPSESSID=abc123; session=xyz789" \
  --max-pages 50
```

### With Custom Headers

```bash
docker run --rm vulnscanner \
  --url https://api.example.com \
  --header "Authorization: Bearer token123" \
  --output json
```

### Save Results to File

```bash
docker run --rm vulnscanner \
  --url https://example.com \
  --output json > results.json
```

### All Options

```bash
docker run --rm vulnscanner --help
```

```
Options:
  --url URL             Target URL to scan (required)
  --threads N           Concurrent threads (default: 5)
  --max-pages N         Max pages to crawl (default: 10)
  --timeout N           Request timeout in seconds (default: 10)
  --delay N             Delay between requests (default: 0.2)
  --cookie, -c          Cookies: 'key1=val1; key2=val2'
  --header, -H          Custom header (repeatable)
  --proxy, -p           Proxy URL: http://127.0.0.1:8080
  --insecure, -k        Ignore SSL certificate errors
  --exclude             Exclude paths (repeatable)
  --only                Run only: xss, sqli
  --skip                Skip tests: xss, sqli (repeatable)
  --output, -o          Output format: cli, json, csv
  --quiet, -q           Suppress banner and progress
```

## Testing with DVWA

For testing/demonstration, you can use DVWA (Damn Vulnerable Web App):

```bash
# 1. Start DVWA (not part of this repo)
docker run -d --name dvwa -p 8080:80 vulnerables/web-dvwa

# 2. Create a network for container communication
docker network create test-net
docker network connect test-net dvwa

# 3. Get session cookie (login at http://localhost:8080, admin/password)
#    Then grab PHPSESSID from browser DevTools > Application > Cookies

# 4. Run scanner
docker run --rm --network test-net vulnscanner \
  --url http://dvwa/vulnerabilities/sqli/ \
  --cookie "PHPSESSID=your-session-id; security=low"
```

## Output Examples

### CLI Output

```
╔══════════════════════════════════════════════════════════════════╗
║                          VulnScanner v2.0                        ║
╚══════════════════════════════════════════════════════════════════╝

[+] Target: http://example.com
[+] Found 3 forms
[*] Testing for XSS...
[!] XSS Found: http://example.com/search - Field: query
[*] Testing for SQL Injection...
[!] SQLi Found: http://example.com/login - Field: username

[+] Found 2 vulnerabilities
```

### JSON Output

```json
{
  "scan_info": {
    "target": "http://example.com",
    "timestamp": "2025-12-27 10:30:00",
    "duration_seconds": 45.2
  },
  "findings": [
    {
      "type": "XSS",
      "url": "http://example.com/search",
      "severity": "high",
      "details": "Reflected XSS in field 'query'"
    }
  ]
}
```

## Development

### Local Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py --url http://localhost:8080
```

### Run Tests

```bash
pytest tests/
```

### Project Structure

```
vulnscanner/
├── scanner/           # Core scanning modules
│   ├── crawler.py     # Web crawling
│   ├── xss.py         # XSS detection
│   ├── sqli.py        # SQL injection detection
│   ├── parallel.py    # Thread pool
│   └── report.py      # Output formatting
├── tests/             # Unit tests
├── main.py            # CLI entry point
├── Dockerfile
├── requirements.txt
└── README.md
```

## Security & Legal

**For authorized testing only.**

- Only scan systems you own or have explicit permission to test
- Unauthorized scanning is illegal
- Use responsibly and ethically

## License

MIT License - See LICENSE file for details.
