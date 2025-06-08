import requests
import time

SQLMAP_API_URL = "http://127.0.0.1:8775"

def run_sqlmap_scan(target_url, data=None):
    # Start task
    new_task = requests.get(f"{SQLMAP_API_URL}/task/new").json()
    taskid = new_task['taskid']
    # Set options
    options = {'url': target_url}
    if data:
        options['data'] = data
    requests.post(f"{SQLMAP_API_URL}/scan/{taskid}/start", json=options)
    # Poll status
    while True:
        status = requests.get(f"{SQLMAP_API_URL}/scan/{taskid}/status").json()
        if status['status'] == 'terminated':
            break
        time.sleep(2)
    # Fetch data
    result = requests.get(f"{SQLMAP_API_URL}/scan/{taskid}/data").json()
    return result.get('data', [])