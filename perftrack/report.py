import json
import math
import os


def _sparkline(samples, width=40):
    # create a simple ascii sparkline based on rss values
    vals = [s.get("rss_mb") for s in samples if s.get("rss_mb") is not None]
    if not vals:
        return ""
    mn, mx = min(vals), max(vals)
    if mx - mn == 0:
        return "▁" * min(len(vals), width)
    # normalize into 8 levels
    levels = "▁▂▃▄▅▆▇█"
    out = []
    step = max(1, int(math.ceil(len(vals) / width)))
    for i in range(0, len(vals), step):
        v = vals[i]
        idx = int((v - mn) / (mx - mn) * (len(levels) - 1))
        out.append(levels[idx])
    return "".join(out)


def render_html_report(runfile, outpath):
    """Generate an HTML performance report.

    Args:
        runfile (str): Path to JSON performance data.
        outpath (str): File path to write HTML report.

    """
    if not os.path.exists(runfile):
        raise FileNotFoundError(runfile)
    with open(runfile) as f:
        data = json.load(f)
    metrics = data.get("metrics", {})
    samples = data.get("samples", [])
    spark = _sparkline(samples)
    html = f"""<!doctype html>
<html>
<head><meta charset='utf-8'><title>PerfTrack Report</title>
<style>
body {{ font-family: sans-serif; margin: 20px; }}
.box {{ border:1px solid #ddd; padding: 12px; margin-bottom:10px; border-radius:6px; }}
.muted {{ color: #666; font-size: 0.9em; }}
</style>
</head><body>
<h1>PerfTrack Report</h1>
<div class='box'>
<div class='muted'>Command</div>
<div><pre>{data.get("command")}</pre></div>
<div class='muted'>Wall time (ms)</div>
<div>{metrics.get("wall_time_ms")}</div>
<div class='muted'>CPU time (ms)</div>
<div>{metrics.get("cpu_time_ms")}</div>
<div class='muted'>Peak RSS (MB)</div>
<div>{metrics.get("max_rss_mb")}</div>
</div>

<h3>Memory sparkline</h3>
<pre style='font-size:18px'>{spark}</pre>

<h3>Samples (time_ms, rss_mb)</h3>
<pre>{[(s.get("time_ms"), s.get("rss_mb")) for s in samples]}</pre>

</body></html>
"""
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    with open(outpath, "w") as f:
        f.write(html)
