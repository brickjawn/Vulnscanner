import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from colorama import Fore, Style

def crawl_site(url, max_pages=10, timeout=5, progress_callback=None, scan_config=None):
    """
    Crawl a website to find forms and links
    Args:
        url: Target URL to crawl
        max_pages: Maximum number of pages to crawl
        timeout: Request timeout in seconds
        progress_callback: Optional callback for progress updates
        scan_config: Optional dict with authentication and request configuration:
            - cookies: dict of cookies to send
            - headers: dict of custom headers
            - proxies: dict of proxy configuration
            - verify_ssl: bool to verify SSL certificates
            - delay: float seconds between requests
            - basic_auth: tuple (username, password)
            - verbose: int verbosity level
            - exclude: list of paths to exclude
    Returns: 
        (links, forms) where forms is a list of (url, form_element) tuples
    """
    # Default scan config
    if scan_config is None:
        scan_config = {}
    
    cookies = scan_config.get('cookies', {})
    headers = scan_config.get('headers', {})
    proxies = scan_config.get('proxies', None)
    verify_ssl = scan_config.get('verify_ssl', True)
    delay = scan_config.get('delay', 0.2)
    basic_auth = scan_config.get('basic_auth', None)
    verbose = scan_config.get('verbose', 0)
    exclude_paths = scan_config.get('exclude', [])
    
    session = requests.Session()
    
    # Set default User-Agent if not provided
    if 'User-Agent' not in headers:
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    session.headers.update(headers)
    
    # Apply cookies
    if cookies:
        session.cookies.update(cookies)
    
    # Apply basic auth
    if basic_auth:
        session.auth = basic_auth
    
    visited = set()
    to_visit = [url]
    links = []
    forms = []
    
    pages_crawled = 0
    
    def should_exclude(check_url):
        """Check if URL should be excluded based on exclude paths"""
        parsed = urlparse(check_url)
        for exclude_path in exclude_paths:
            if exclude_path in parsed.path:
                return True
        return False
    
    while to_visit and pages_crawled < max_pages:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue
        
        # Check exclusions
        if should_exclude(current_url):
            if verbose >= 1:
                print(f"{Fore.YELLOW}[i] Excluded: {current_url}{Style.RESET_ALL}")
            continue
            
        try:
            # Make request with all configurations
            response = session.get(
                current_url, 
                timeout=timeout, 
                allow_redirects=True,
                proxies=proxies,
                verify=verify_ssl
            )
            visited.add(current_url)
            pages_crawled += 1
            
            if progress_callback:
                progress_callback(1)
            
            if response.status_code == 200 and 'text/html' in response.headers.get('content-type', '').lower():
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all forms
                page_forms = soup.find_all('form')
                for form in page_forms:
                    forms.append((current_url, form))
                
                print(f"{Fore.BLUE}[i] Crawled: {current_url} - Found {len(page_forms)} forms{Style.RESET_ALL}")
                
                if verbose >= 2:
                    print(f"{Fore.BLUE}    Response: {len(response.text)} bytes, {response.elapsed.total_seconds():.2f}s{Style.RESET_ALL}")
                
                # Find all links for further crawling (only if we haven't reached max pages)
                if pages_crawled < max_pages:
                    for link in soup.find_all('a', href=True):
                        try:
                            full_url = urljoin(current_url, link['href'])
                            parsed_url = urlparse(full_url)
                            base_parsed = urlparse(url)
                            
                            # Only crawl same domain and avoid common non-page URLs
                            if (parsed_url.netloc == base_parsed.netloc and 
                                not any(ext in parsed_url.path.lower() for ext in ['.js', '.css', '.jpg', '.png', '.gif', '.pdf', '.zip']) and
                                full_url not in visited and 
                                full_url not in to_visit and
                                len(to_visit) < max_pages * 2 and
                                not should_exclude(full_url)):  # Check exclusions
                                
                                links.append(full_url)
                                to_visit.append(full_url)
                        except Exception:
                            continue  # Skip malformed URLs
            else:
                print(f"{Fore.YELLOW}[!] Skipped non-HTML content: {current_url} (Status: {response.status_code}){Style.RESET_ALL}")
            
            # Configurable delay between requests
            time.sleep(delay)
            
        except requests.exceptions.SSLError as e:
            print(f"{Fore.YELLOW}[!] SSL error crawling {current_url}: {str(e)[:100]}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}[i] Try using --insecure flag to ignore SSL errors{Style.RESET_ALL}")
        except requests.exceptions.ProxyError as e:
            print(f"{Fore.YELLOW}[!] Proxy error crawling {current_url}: {str(e)[:100]}{Style.RESET_ALL}")
        except requests.exceptions.Timeout:
            print(f"{Fore.YELLOW}[!] Timeout crawling {current_url}{Style.RESET_ALL}")
        except requests.exceptions.RequestException as e:
            print(f"{Fore.YELLOW}[!] Error crawling {current_url}: {str(e)[:100]}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[✗] Unexpected error crawling {current_url}: {str(e)[:100]}{Style.RESET_ALL}")
    
    print(f"{Fore.GREEN}[✓] Crawling complete: {len(forms)} forms found across {pages_crawled} pages{Style.RESET_ALL}")
    return links, forms
