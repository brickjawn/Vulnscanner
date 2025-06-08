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

def test_xss(links, forms, progress_callback=None):
    """
    Test forms for XSS vulnerabilities
    Args:
        links: List of URLs (unused but kept for compatibility)
        forms: List of (url, form_element) tuples
        progress_callback: Optional callback for progress updates
    Returns:
        List of vulnerability findings
    """
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
            for input_field in form.find_all(["input", "textarea", "select"]):
                name = input_field.get("name")
                if name:
                    field_type = input_field.get("type", "text")
                    
                    # Skip certain input types
                    if field_type.lower() in ["submit", "button", "reset", "file", "image"]:
                        continue
                        
                    # Use appropriate default values
                    if field_type.lower() == "email":
                        inputs[name] = "test@example.com"
                    elif field_type.lower() == "password":
                        inputs[name] = "password123"
                    elif field_type.lower() == "number":
                        inputs[name] = "123"
                    else:
                        inputs[name] = "test_value"
            
            if not inputs:
                continue
                
            # Test each payload
            for payload in XSS_PAYLOADS:
                test_inputs = inputs.copy()
                
                # Inject payload into each field
                for field_name in test_inputs:
                    test_inputs[field_name] = payload
                    
                    try:
                        session = requests.Session()
                        session.headers.update({
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        })
                        
                        if method == "post":
                            response = session.post(action, data=test_inputs, timeout=10, allow_redirects=True)
                        else:
                            response = session.get(action, params=test_inputs, timeout=10, allow_redirects=True)
                        
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
                                print(f"{Fore.RED}[!] XSS Found: {url} - Field: {field_name}{Style.RESET_ALL}")
                            break  # Found XSS in this field, try next field
                            
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
            progress_callback(1)
    
    return findings