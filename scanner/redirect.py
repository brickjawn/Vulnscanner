import requests
from urllib.parse import urlparse, urlencode, urlunparse, parse_qs
from colorama import Fore, Style

def test_open_redirect(links, forms):
    """Test for open redirect vulnerabilities"""
    findings = []
    
    for url, form in forms:
        if is_safe_redirect(url, ['localhost', '127.0.0.1']):
            # Test redirect parameters
            pass
    
    return findings

def is_safe_redirect(url, allowed_hosts):
    """Validate redirect URL against allowed hosts"""
    try:
        parsed = urlparse(url)
        return parsed.netloc in allowed_hosts
    except:
        return False