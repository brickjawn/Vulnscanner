import json
import csv
import datetime
from colorama import Fore, Style

def generate_report(findings, output="cli", scan_time=0, target=""):
    """
    Generate vulnerability report in various formats
    Args:
        findings: List of vulnerability findings
        output: Output format ("cli", "json", "csv")
        scan_time: Total scan time in seconds  
        target: Target URL that was scanned
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if output == "cli":
        print(f"{Fore.CYAN}╔══════════════════════════════════════════════════════════════════╗")
        print(f"║                        VULNERABILITY REPORT                     ║")
        print(f"╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        print(f"\n{Fore.BLUE}Scan Details:{Style.RESET_ALL}")
        print(f"  Target:     {target}")
        print(f"  Timestamp:  {timestamp}")
        print(f"  Duration:   {scan_time:.2f} seconds")
        print(f"  Findings:   {len(findings)} total")
        
        if not findings:
            print(f"\n{Fore.GREEN}✓ No vulnerabilities found.{Style.RESET_ALL}")
            print(f"{Fore.BLUE}[i] This is a preliminary scan. Consider manual testing for comprehensive security assessment.{Style.RESET_ALL}")
            return
        
        # Categorize findings by severity
        critical = [f for f in findings if f.get('severity') == 'critical']
        high = [f for f in findings if f.get('severity') == 'high']
        medium = [f for f in findings if f.get('severity') == 'medium']
        low = [f for f in findings if f.get('severity') == 'low']
        info = [f for f in findings if f.get('severity') == 'info']
        
        print(f"\n{Fore.BLUE}Severity Breakdown:{Style.RESET_ALL}")
        if critical:
            print(f"  {Fore.RED}Critical: {len(critical)}{Style.RESET_ALL}")
        if high:
            print(f"  {Fore.RED}High:     {len(high)}{Style.RESET_ALL}")
        if medium:
            print(f"  {Fore.YELLOW}Medium:   {len(medium)}{Style.RESET_ALL}")
        if low:
            print(f"  {Fore.YELLOW}Low:      {len(low)}{Style.RESET_ALL}")
        if info:
            print(f"  {Fore.CYAN}Info:     {len(info)}{Style.RESET_ALL}")
        
        print(f"\n{Fore.BLUE}Detailed Findings:{Style.RESET_ALL}")
        
        for i, finding in enumerate(findings, 1):
            severity = finding.get('severity', 'unknown')
            
            # Color based on severity
            if severity in ['critical', 'high']:
                color = Fore.RED
            elif severity in ['medium', 'low']:
                color = Fore.YELLOW
            else:
                color = Fore.CYAN
            
            print(f"\n{color}[{i}] {finding['type']}{Style.RESET_ALL}")
            print(f"    URL:        {finding['url']}")
            print(f"    Details:    {finding['details']}")
            print(f"    Severity:   {severity.upper()}")
            
            # Additional details based on vulnerability type
            if 'payload' in finding:
                print(f"    Payload:    {finding['payload'][:100]}...")
            if 'method' in finding:
                print(f"    Method:     {finding['method']}")
            if 'error_signature' in finding:
                print(f"    Error:      {finding['error_signature']}")
            if 'subtype' in finding:
                print(f"    Subtype:    {finding['subtype']}")
            
            # Remediation advice
            if finding['type'] == "XSS":
                print(f"    {Fore.GREEN}Remediation: Use proper output encoding and input sanitization. Implement CSP headers.{Style.RESET_ALL}")
            elif finding['type'] == "SQL Injection":
                print(f"    {Fore.GREEN}Remediation: Use parameterized queries/prepared statements. Validate input data.{Style.RESET_ALL}")
            elif finding['type'] == "Open Port":
                print(f"    {Fore.GREEN}Remediation: Restrict access with firewall rules or close unnecessary services.{Style.RESET_ALL}")
            
            print("    " + "-" * 60)
        
        print(f"\n{Fore.YELLOW}⚠️  Disclaimer: This is an automated scan. Manual verification is recommended.{Style.RESET_ALL}")
        print(f"{Fore.BLUE}🔒 For authorized testing only. Ensure you have permission to test the target.{Style.RESET_ALL}")
        
    elif output == "json":
        report_data = {
            "scan_info": {
                "target": target,
                "timestamp": timestamp,
                "duration_seconds": scan_time,
                "total_findings": len(findings)
            },
            "findings": findings,
            "summary": {
                "critical": len([f for f in findings if f.get('severity') == 'critical']),
                "high": len([f for f in findings if f.get('severity') == 'high']),
                "medium": len([f for f in findings if f.get('severity') == 'medium']),
                "low": len([f for f in findings if f.get('severity') == 'low']),
                "info": len([f for f in findings if f.get('severity') == 'info'])
            }
        }
        print(json.dumps(report_data, indent=2))
        
    elif output == "csv":
        filename = f"vulnscan_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if findings:
            # Flatten findings for CSV export
            csv_data = []
            for finding in findings:
                row = {
                    'timestamp': timestamp,
                    'target': target,
                    'scan_duration': scan_time,
                    'type': finding['type'],
                    'url': finding['url'],
                    'details': finding['details'],
                    'severity': finding.get('severity', 'unknown'),
                    'payload': finding.get('payload', ''),
                    'method': finding.get('method', ''),
                    'error_signature': finding.get('error_signature', ''),
                    'subtype': finding.get('subtype', '')
                }
                csv_data.append(row)
            
            fieldnames = ['timestamp', 'target', 'scan_duration', 'type', 'url', 'details', 
                         'severity', 'payload', 'method', 'error_signature', 'subtype']
            
            with open(filename, "w", newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
            
            print(f"{Fore.GREEN}✓ CSV report saved as {filename}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}No vulnerabilities found - CSV report not generated{Style.RESET_ALL}")

def print_scan_statistics(findings):
    """Print quick scan statistics"""
    if not findings:
        return
        
    vuln_types = {}
    for finding in findings:
        vuln_type = finding['type']
        vuln_types[vuln_type] = vuln_types.get(vuln_type, 0) + 1
    
    print(f"\n{Fore.BLUE}Quick Stats:{Style.RESET_ALL}")
    for vuln_type, count in vuln_types.items():
        print(f"  {vuln_type}: {count}")