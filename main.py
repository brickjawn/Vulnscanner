#!/usr/bin/env python3
"""
VulnScanner v2.0 - Web Application Vulnerability Scanner
For authorized penetration testing only.
"""

import argparse
import sys
import time
import json
from scanner.crawler import crawl_site
from scanner.xss import test_xss
from scanner.sqli import test_sqli
from scanner.parallel import parallel_scan
from scanner.report import generate_report
from colorama import Fore, Style, init

init()


def print_banner():
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════╗
║                          VulnScanner v2.0                        ║
║                   Web Vulnerability Scanner                       ║
║                   For authorized testing only                     ║
╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
""")


def parse_cookies(cookie_string):
    """Parse cookie string into dict: 'key1=val1; key2=val2' -> {key1: val1, key2: val2}"""
    if not cookie_string:
        return {}
    cookies = {}
    for cookie in cookie_string.split(';'):
        cookie = cookie.strip()
        if '=' in cookie:
            name, value = cookie.split('=', 1)
            cookies[name.strip()] = value.strip()
    return cookies


def parse_headers(header_list):
    """Parse header list into dict: ['Key: Value'] -> {Key: Value}"""
    if not header_list:
        return {}
    headers = {}
    for header in header_list:
        if ':' in header:
            name, value = header.split(':', 1)
            headers[name.strip()] = value.strip()
    return headers


def main():
    parser = argparse.ArgumentParser(
        prog='vulnscanner',
        description='VulnScanner - Web Application Vulnerability Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic scan
  %(prog)s --url https://example.com

  # Authenticated scan with cookies
  %(prog)s --url https://app.com --cookie "session=abc123; token=xyz"

  # Deep scan with JSON output
  %(prog)s --url https://site.com --max-pages 100 --output json

  # With rate limiting
  %(prog)s --url https://site.com --delay 1 --threads 3

  # Save results to file
  %(prog)s --url https://site.com --output json > results.json
        """
    )

    # Required
    parser.add_argument('--url', required=True, help='Target URL to scan')

    # Scan options
    parser.add_argument('--threads', type=int, default=5, help='Concurrent threads (default: 5)')
    parser.add_argument('--max-pages', type=int, default=10, help='Max pages to crawl (default: 10)')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds (default: 10)')
    parser.add_argument('--delay', type=float, default=0.2, help='Delay between requests (default: 0.2)')

    # Authentication
    parser.add_argument('--cookie', '-c', help="Cookies: 'PHPSESSID=abc; security=low'")
    parser.add_argument('--header', '-H', action='append', help="Custom header (repeatable): -H 'Auth: Bearer token'")
    parser.add_argument('--user-agent', default='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0')

    # Network
    parser.add_argument('--proxy', '-p', help='Proxy URL: http://127.0.0.1:8080')
    parser.add_argument('--insecure', '-k', action='store_true', help='Ignore SSL certificate errors')

    # Scope
    parser.add_argument('--exclude', action='append', help='Exclude paths (repeatable)')
    parser.add_argument('--only', choices=['xss', 'sqli'], help='Run only specified test')
    parser.add_argument('--skip', action='append', choices=['xss', 'sqli'], help='Skip test types')

    # Output
    parser.add_argument('--output', '-o', choices=['cli', 'json', 'csv'], default='cli', help='Output format')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress banner and progress')

    args = parser.parse_args()

    # Normalize URL
    if not args.url.startswith(('http://', 'https://')):
        args.url = 'https://' + args.url

    # Parse auth options
    cookies = parse_cookies(args.cookie)
    headers = parse_headers(args.header)
    headers['User-Agent'] = args.user_agent

    proxies = {'http': args.proxy, 'https': args.proxy} if args.proxy else None

    scan_config = {
        'cookies': cookies,
        'headers': headers,
        'proxies': proxies,
        'verify_ssl': not args.insecure,
        'timeout': args.timeout,
        'delay': args.delay,
        'verbose': 0 if args.quiet else 1,
        'exclude': args.exclude or []
    }

    # Determine tests to run
    skip_tests = set(args.skip) if args.skip else set()
    if args.only:
        skip_tests = {'xss', 'sqli'} - {args.only}

    # Output mode
    quiet = args.quiet or args.output != 'cli'

    if not quiet:
        print_banner()
        print(f"{Fore.GREEN}[+] Target: {args.url}")
        print(f"[+] Threads: {args.threads}")
        print(f"[+] Max Pages: {args.max_pages}")
        if cookies:
            print(f"[+] Cookies: {len(cookies)} configured")
        if args.proxy:
            print(f"[+] Proxy: {args.proxy}")
        print(f"{Style.RESET_ALL}")

    findings = []
    start_time = time.time()

    try:
        # Crawl
        if not quiet:
            print(f"{Fore.CYAN}[*] Crawling {args.url}...{Style.RESET_ALL}")

        links, forms = crawl_site(
            args.url,
            max_pages=args.max_pages,
            timeout=args.timeout,
            scan_config=scan_config
        )

        if not forms:
            if not quiet:
                print(f"{Fore.YELLOW}[!] No forms found{Style.RESET_ALL}")
        else:
            if not quiet:
                print(f"{Fore.GREEN}[+] Found {len(forms)} forms{Style.RESET_ALL}")

            # XSS Testing
            if 'xss' not in skip_tests:
                if not quiet:
                    print(f"{Fore.CYAN}[*] Testing for XSS...{Style.RESET_ALL}")
                xss_findings = parallel_scan(
                    lambda f: test_xss([f[0]], [f], scan_config=scan_config),
                    forms,
                    threads=args.threads
                )
                findings.extend(xss_findings)

            # SQLi Testing
            if 'sqli' not in skip_tests:
                if not quiet:
                    print(f"{Fore.CYAN}[*] Testing for SQL Injection...{Style.RESET_ALL}")
                sqli_findings = parallel_scan(
                    lambda f: test_sqli([f[0]], [f], scan_config=scan_config),
                    forms,
                    threads=args.threads
                )
                findings.extend(sqli_findings)

        scan_time = time.time() - start_time

        if not quiet:
            print(f"\n{Fore.CYAN}[*] Scan completed in {scan_time:.2f}s{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[+] Found {len(findings)} vulnerabilities{Style.RESET_ALL}\n")

        # Generate report
        generate_report(findings, output=args.output, scan_time=scan_time, target=args.url)

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Scan interrupted{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == '__main__':
    main()
