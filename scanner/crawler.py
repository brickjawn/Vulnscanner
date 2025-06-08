import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from colorama import Fore, Style

def crawl_site(url, max_pages=10, timeout=5, progress_callback=None):
    """
    Crawl a website to find forms and links
    Args:
        url: Target URL to crawl
        max_pages: Maximum number of pages to crawl
        timeout: Request timeout in seconds
        progress_callback: Optional callback for progress updates
    Returns: 
        (links, forms) where forms is a list of (url, form_element) tuples
    """
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    visited = set()
    to_visit = [url]
    links = []
    forms = []
    
    pages_crawled = 0
    
    while to_visit and pages_crawled < max_pages:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue
            
        try:
            response = session.get(current_url, timeout=timeout, allow_redirects=True)
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
                                len(to_visit) < max_pages * 2):  # Limit queue size
                                
                                links.append(full_url)
                                to_visit.append(full_url)
                        except Exception:
                            continue  # Skip malformed URLs
            else:
                print(f"{Fore.YELLOW}[!] Skipped non-HTML content: {current_url} (Status: {response.status_code}){Style.RESET_ALL}")
            
            # Small delay to be respectful to the server
            time.sleep(0.2)
            
        except requests.exceptions.Timeout:
            print(f"{Fore.YELLOW}[!] Timeout crawling {current_url}{Style.RESET_ALL}")
        except requests.exceptions.RequestException as e:
            print(f"{Fore.YELLOW}[!] Error crawling {current_url}: {str(e)[:100]}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[✗] Unexpected error crawling {current_url}: {str(e)[:100]}{Style.RESET_ALL}")
    
    print(f"{Fore.GREEN}[✓] Crawling complete: {len(forms)} forms found across {pages_crawled} pages{Style.RESET_ALL}")
    return links, forms 