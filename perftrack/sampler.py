import datetime
import json
import os
import subprocess
import time

try:
    import psutil
except Exception:
    psutil = None


def _which_psutil_available():
    return psutil is not None


def _measure_process(proc, interval):
    samples = []
    max_rss = 0.0
    # psutil may not be available in some environments; handle gracefully
    if not _which_psutil_available():
        # wait for process to finish
        start = time.time()
        proc.wait()
        end = time.time()
        return {
            "project": os.getcwd().split(os.sep)[-1],
            "commit": os.getenv("GITHUB_SHA", "local"),
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "command": proc.args if isinstance(proc.args, str) else " ".join(proc.args),
            "metrics": {
                "wall_time_ms": int((end - start) * 1000),
                "cpu_time_ms": None,
                "max_rss_mb": None,
            },
            "samples": [],
        }

    p = psutil.Process(proc.pid)
    start = time.time()
    while proc.poll() is None:
        try:
            rss = p.memory_info().rss / (1024 * 1024)
            max_rss = max(max_rss, rss)
            samples.append(
                {"time_ms": int((time.time() - start) * 1000), "rss_mb": round(rss, 2)}
            )
        except psutil.NoSuchProcess:
            break
        time.sleep(interval)
    end = time.time()
    try:
        cpu = p.cpu_times()
        cpu_ms = int((cpu.user + cpu.system) * 1000)
    except Exception:
        cpu_ms = None

    return {
        "project": os.getcwd().split(os.sep)[-1],
        "commit": os.getenv("GITHUB_SHA", "local"),
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "command": proc.args if isinstance(proc.args, str) else " ".join(proc.args),
        "metrics": {
            "wall_time_ms": int((end - start) * 1000),
            "cpu_time_ms": cpu_ms,
            "max_rss_mb": round(max_rss, 2),
        },
        "samples": samples,
    }


def run_and_measure(command, interval=0.2):
    """Execute a command and sample resource usage over time."""
    # Spawn the command as a subprocess. Use shell for convenience.
    proc = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    result = _measure_process(proc, interval)
    # capture remaining stdout/stderr (not used right now, but saved for completeness)
    try:
        out, err = proc.communicate(timeout=1)
    except Exception:
        out, err = ("", "")
    result["stdout"] = out
    result["stderr"] = err
    return result


def save_run(result, path=".perftrack/latest.json"):
    """Save collected performance metrics to a JSON file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(result, f, indent=2)
