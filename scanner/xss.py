import requests
from urllib.parse import urljoin
from colorama import Fore, Style

# Multiple XSS payloads for better detection
XSS_PAYLOADS = [
    "<script>alert('xss')</script>",
    "<img src=x onerror=alert('xss')>",
    "<svg onload=alert('xss')>",
    "javascript:alert('xss')",
    "<iframe src=javascript:alert('xss')>",
    "';alert('xss');//",
    "\"><script>alert('xss')</script>",
    "<script>alert(String.fromCharCode(88,83,83))</script>",
    "<img src=\"javascript:alert('xss')\">",
    "<div onmouseover=\"alert('xss')\">test</div>"
]

def test_xss(links, forms, progress_callback=None, finding_callback=None, scan_config=None):
    """
    Test forms for XSS vulnerabilities
    Args:
        links: List of URLs (unused but kept for compatibility)
        forms: List of (url, form_element) tuples
        progress_callback: Optional callback for progress updates
        finding_callback: Optional callback for reporting findings in real-time
        scan_config: Optional dict with authentication and request configuration:
            - cookies: dict of cookies to send
            - headers: dict of custom headers
            - proxies: dict of proxy configuration
            - verify_ssl: bool to verify SSL certificates
            - timeout: int seconds for request timeout
            - basic_auth: tuple (username, password)
            - verbose: int verbosity level
    Returns:
        List of vulnerability findings
    """
    # Default scan config
    if scan_config is None:
        scan_config = {}
    
    cookies = scan_config.get('cookies', {})
    headers = scan_config.get('headers', {})
    proxies = scan_config.get('proxies', None)
    verify_ssl = scan_config.get('verify_ssl', True)
    timeout = scan_config.get('timeout', 10)
    basic_auth = scan_config.get('basic_auth', None)
    verbose = scan_config.get('verbose', 0)
    
    findings = []
    
    for url, form in forms:
        try:
            # Get form action and method
            action = form.get("action")
            if action:
                action = urljoin(url, action)
            else:
                action = url
                
            method = form.get("method", "get").lower()
            
            # Get all input fields
            inputs = {}
            submit_inputs = {}  # Track submit buttons separately
            
            for input_field in form.find_all(["input", "textarea", "select"]):
                name = input_field.get("name")
                if name:
                    field_type = input_field.get("type", "text")
                    
                    # Track submit buttons but don't inject into them
                    if field_type.lower() == "submit":
                        submit_inputs[name] = input_field.get("value", "Submit")
                        continue
                    
                    # Skip other non-injectable input types
                    if field_type.lower() in ["button", "reset", "file", "image"]:
                        continue
                        
                    # Use appropriate default values
                    if field_type.lower() == "email":
                        inputs[name] = "test@example.com"
                    elif field_type.lower() == "password":
                        inputs[name] = "password123"
                    elif field_type.lower() == "number":
                        inputs[name] = "123"
                    elif field_type.lower() == "hidden":
                        # Preserve hidden field values (often CSRF tokens)
                        inputs[name] = input_field.get("value", "")
                    else:
                        inputs[name] = "test_value"
            
            if not inputs:
                continue
            
            # Merge submit button values into inputs (needed for form processing)
            inputs.update(submit_inputs)
                
            # Test each payload
            for payload in XSS_PAYLOADS:
                test_inputs = inputs.copy()
                
                # Inject payload into each field
                for field_name in test_inputs:
                    test_inputs[field_name] = payload
                    
                    try:
                        session = requests.Session()
                        
                        # Set default User-Agent if not provided
                        session_headers = headers.copy() if headers else {}
                        if 'User-Agent' not in session_headers:
                            session_headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        
                        session.headers.update(session_headers)
                        
                        # Apply cookies
                        if cookies:
                            session.cookies.update(cookies)
                        
                        # Apply basic auth
                        if basic_auth:
                            session.auth = basic_auth
                        
                        if method == "post":
                            response = session.post(
                                action, 
                                data=test_inputs, 
                                timeout=timeout, 
                                allow_redirects=True,
                                proxies=proxies,
                                verify=verify_ssl
                            )
                        else:
                            response = session.get(
                                action, 
                                params=test_inputs, 
                                timeout=timeout, 
                                allow_redirects=True,
                                proxies=proxies,
                                verify=verify_ssl
                            )
                        
                        if verbose >= 2:
                            print(f"{Fore.BLUE}    XSS Test: {action} [{method.upper()}] - {response.status_code}{Style.RESET_ALL}")
                        
                        # Check if payload is reflected in response
                        if payload in response.text or payload.lower() in response.text.lower():
                            finding = {
                                "type": "XSS",
                                "url": url,
                                "details": f"Possible XSS in field '{field_name}' at {action}",
                                "payload": payload,
                                "method": method.upper(),
                                "severity": "high"
                            }
                            
                            # Avoid duplicate findings
                            if not any(f['url'] == finding['url'] and f['details'] == finding['details'] for f in findings):
                                findings.append(finding)
                                if finding_callback:
                                    finding_callback(finding)
                                else:
                                    print(f"{Fore.RED}[!] XSS Found: {url} - Field: {field_name}{Style.RESET_ALL}")
                            break  # Found XSS in this field, try next field
                            
                    except requests.exceptions.SSLError as e:
                        if verbose >= 1:
                            print(f"{Fore.YELLOW}[!] SSL error testing XSS on {action}: {str(e)[:50]}{Style.RESET_ALL}")
                    except requests.exceptions.ProxyError as e:
                        if verbose >= 1:
                            print(f"{Fore.YELLOW}[!] Proxy error testing XSS on {action}: {str(e)[:50]}{Style.RESET_ALL}")
                    except requests.exceptions.Timeout:
                        print(f"{Fore.YELLOW}[!] Timeout testing XSS on {action}{Style.RESET_ALL}")
                    except requests.exceptions.RequestException:
                        pass  # Continue with next test
                    except Exception:
                        pass  # Continue with next test
                    
                    # Reset for next field test
                    test_inputs[field_name] = inputs[field_name]
                    
        except Exception as e:
            print(f"{Fore.YELLOW}[!] Error testing XSS on {url}: {str(e)[:100]}{Style.RESET_ALL}")
            
        if progress_callback:
            progress_callback()
    
    return findings
