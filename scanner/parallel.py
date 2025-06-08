from concurrent.futures import ThreadPoolExecutor

def parallel_scan(scan_func, items, threads=5):
    results = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        for out in executor.map(scan_func, items):
            if isinstance(out, list):
                results.extend(out)
            elif out:
                results.append(out)
    return results