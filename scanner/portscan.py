import nmap
import time
from colorama import Fore, Style

def scan_ports(target, ports="1-1000", progress_callback=None):
    """
    Scan ports on target host using nmap
    Args:
        target: IP address or hostname
        ports: Port range (default: "1-1000")
        progress_callback: Optional callback for progress updates
    Returns:
        List of open port dictionaries
    """
    try:
        nm = nmap.PortScanner()
        
        # Use faster scan options for speed
        scan_args = "-sS -T4 --max-retries 1 --host-timeout 30s"
        
        print(f"Scanning {target} ports {ports}...")
        nm.scan(target, ports, arguments=scan_args)
        
        if progress_callback:
            progress_callback(1)
            
    except nmap.PortScannerError as e:
        print(f"{Fore.RED}[✗] Nmap error: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] Make sure nmap is installed: sudo apt install nmap{Style.RESET_ALL}")
        return []
    except Exception as e:
        print(f"{Fore.RED}[✗] Error scanning ports: {e}{Style.RESET_ALL}")
        return []
    
    results = []
    if target in nm.all_hosts():
        host_info = nm[target]
        for proto in host_info.all_protocols():
            ports_dict = host_info[proto]
            for port in ports_dict:
                if ports_dict[port]['state'] == 'open':
                    service = ports_dict[port]['name']
                    version = ports_dict[port].get('version', '')
                    product = ports_dict[port].get('product', '')
                    
                    service_info = service
                    if product:
                        service_info += f" ({product}"
                        if version:
                            service_info += f" {version}"
                        service_info += ")"
                    
                    results.append({
                        'port': port, 
                        'protocol': proto, 
                        'service': service_info,
                        'state': ports_dict[port]['state']
                    })
                    
                    # Real-time feedback
                    print(f"{Fore.GREEN}[+] Found open port: {port}/{proto} ({service_info}){Style.RESET_ALL}")
    
    return results