import requests

def fingerprint(url):
    resp = requests.get(url)
    headers = resp.headers
    tech = []
    if 'X-Powered-By' in headers:
        tech.append(headers['X-Powered-By'])
    if 'Server' in headers:
        tech.append(headers['Server'])
    # Add more heuristics as needed
    return tech