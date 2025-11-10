import json, sys, os

def _load(path):
    if not os.path.exists(path):
        print(f"File not found: {path}", file=sys.stderr)
        return None
    with open(path) as f:
        return json.load(f)

def compare(baseline_path, latest_path, threshold=0.10):
    baseline = _load(baseline_path)
    latest = _load(latest_path)
    if baseline is None or latest is None:
        print("Missing files for comparison", file=sys.stderr)
        return 2

    diffs = {}
    for key in baseline.get('metrics', {}):
        old = baseline['metrics'].get(key)
        new = latest['metrics'].get(key)
        if old is None or new is None:
            diffs[key] = None
            continue
        try:
            if new == old:
                change = None
            else:
                change = (new - old) / float(old) if float(old) != 0 else float('inf')
        except Exception:
            change = None
        diffs[key] = change

    regressed = {k:v for k,v in diffs.items() if v is not None and v > threshold}
    if regressed:
        print("Detected regressions:")
        for k,v in regressed.items():
            print(f" - {k}: +{v*100:.2f}% (baseline {baseline['metrics'].get(k)} -> latest {latest['metrics'].get(k)})")
        return 1
    else:
        print("No regressions detected.")
        return 0
