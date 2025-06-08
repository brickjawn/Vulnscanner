import requests
from urllib.parse import urlparse, urlencode, urlunparse, parse_qs

def test_open_redirect(links):
    findings = []
    payload = "https://attacker.com"
    for link in links:
        parsed = urlparse(link)
        qs = parse_qs(parsed.query)
        for k, v in qs.items():
            if "url" in k or "redirect" in k:
                new_qs = qs.copy()
                new_qs[k] = payload
                new_query = urlencode(new_qs, doseq=True)
                test_url = urlunparse(parsed._replace(query=new_query))
                try:
                    resp = requests.get(test_url, allow_redirects=False, timeout=5)
                    if "attacker.com" in resp.headers.get("Location", ""):
                        findings.append({
                            "type": "Open Redirect",
                            "url": test_url,
                            "details": f"Parameter '{k}' may be vulnerable to open redirect."
                        })
                except Exception:
                    pass
    return findings