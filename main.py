import argparse
import sys
import time
from scanner.portscan import scan_ports
from scanner.crawler import crawl_site
from scanner.xss import test_xss
from scanner.sqli import test_sqli
#from scanner.adv_sqli import run_sqlmap_scan # Uncomment and implement if using sqlmap-api
from scanner.parallel import parallel_scan
from scanner.report import generate_report
from colorama import Fore, Style, init
from tqdm import tqdm

# Initialize colorama for cross-platform color support
init()

def print_banner():
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════╗
║                          VulnScanner v2.0                       ║
║                Advanced Penetration Testing Toolkit             ║
║                   For authorized testing only                    ║
╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def validate_url(url):
    """Validate and normalize URL format"""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(
        description="VulnScanner - Advanced Penetration Testing Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --url https://example.com --threads 10
  python main.py --url example.com --enable-portscan --output json
  python main.py --url https://testsite.com --threads 5 --max-pages 20
        """
    )
    parser.add_argument("--url", required=True, help="Target URL (e.g., https://example.com)")
    parser.add_argument("--threads", type=int, default=5, help="Number of concurrent threads (default: 5)")
    parser.add_argument("--output", choices=["cli", "json", "csv"], default="cli", help="Output format (default: cli)")
    parser.add_argument("--enable-portscan", action="store_true", help="Enable Nmap port scanning")
    parser.add_argument("--max-pages", type=int, default=10, help="Maximum pages to crawl (default: 10)")
    parser.add_argument("--timeout", type=int, default=5, help="Request timeout in seconds (default: 5)")
    #parser.add_argument("--enable-adv-sqli", action="store_true", help="Enable advanced SQLi scan with sqlmap-api")
    
    args = parser.parse_args()
    
    # Validate and normalize URL
    args.url = validate_url(args.url)
    
    print(f"{Fore.GREEN}[✓] Target: {args.url}")
    print(f"[✓] Threads: {args.threads}")
    print(f"[✓] Max Pages: {args.max_pages}")
    print(f"[✓] Timeout: {args.timeout}s{Style.RESET_ALL}\n")

    findings = []
    start_time = time.time()

    try:
        # Network scanning
        if args.enable_portscan:
            host = args.url.split("//")[-1].split("/")[0]
            print(f"{Fore.CYAN}[*] Starting port scan for: {host}{Style.RESET_ALL}")
            
            with tqdm(desc="Port Scanning", unit="ports") as pbar:
                open_ports = scan_ports(host, progress_callback=pbar.update)
                
            if open_ports:
                print(f"{Fore.GREEN}[✓] Found {len(open_ports)} open ports{Style.RESET_ALL}")
                for port_info in open_ports:
                    findings.append({
                        'type': 'Open Port', 
                        'url': host, 
                        'details': f"{port_info['port']}/{port_info['protocol']} {port_info['service']}",
                        'severity': 'info'
                    })
            else:
                print(f"{Fore.YELLOW}[!] No open ports found in the scanned range{Style.RESET_ALL}")

        # Crawl web application
        print(f"\n{Fore.CYAN}[*] Crawling {args.url} for forms and links...{Style.RESET_ALL}")
        
        with tqdm(desc="Crawling", unit="pages") as pbar:
            links, forms = crawl_site(args.url, max_pages=args.max_pages, timeout=args.timeout, progress_callback=pbar.update)

        if not forms:
            print(f"{Fore.YELLOW}[!] No forms found for vulnerability testing{Style.RESET_ALL}")
            print(f"{Fore.BLUE}[i] Consider testing with a target that has forms{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}[✓] Found {len(forms)} forms across {len(set(url for url, _ in forms))} pages{Style.RESET_ALL}")

            # Multi-threaded XSS testing
            print(f"\n{Fore.CYAN}[*] Testing for XSS vulnerabilities...{Style.RESET_ALL}")
            with tqdm(total=len(forms), desc="XSS Testing", unit="forms") as pbar:
                xss_findings = parallel_scan(
                    lambda f: test_xss([f[0]], [f], progress_callback=pbar.update), 
                    forms, 
                    threads=args.threads
                )
                findings.extend(xss_findings)

            # Multi-threaded SQLi testing
            print(f"{Fore.CYAN}[*] Testing for SQL Injection vulnerabilities...{Style.RESET_ALL}")
            with tqdm(total=len(forms), desc="SQLi Testing", unit="forms") as pbar:
                sqli_findings = parallel_scan(
                    lambda f: test_sqli([f[0]], [f], progress_callback=pbar.update), 
                    forms, 
                    threads=args.threads
                )
                findings.extend(sqli_findings)

        # Optional: Advanced SQLi (requires sqlmap-api)
        #if args.enable_adv_sqli:
        #    print(f"{Fore.CYAN}[*] Advanced SQLi scan with sqlmap-api...{Style.RESET_ALL}")
        #    for url, form in forms:
        #        findings += run_sqlmap_scan(url)

        # Calculate scan time
        scan_time = time.time() - start_time
        
        print(f"\n{Fore.CYAN}[*] Scan completed in {scan_time:.2f} seconds{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[✓] Found {len(findings)} total findings{Style.RESET_ALL}\n")
        
        # Generate report
        generate_report(findings, output=args.output, scan_time=scan_time, target=args.url)

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Scan interrupted by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}[✗] Error during scan: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()