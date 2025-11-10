# PerfTrack

PerfTrack is a command-line tool that helps detect performance regressions in open-source projects and CI pipelines. It requires no external services and tracks performance locally.

Designed for Python projects (Django, Pandas, FastAPI, ML libraries), internal tooling, and personal benchmarking workflows

## Why PerfTrack?
Performance regressions often go unnoticed because:

- CI timing is noisy and unreliable for benchmarking
- Tools like ASV or pytest-benchmark require setup and maintenance
- There is no simple utility to store a baseline and fail CI when performance drops

PerfTrack stores local performance snapshots and compares them against future runs, both locally and in CI.

## What It Measures
- Wall-clock time
- CPU time
- Peak RSS memory usage

Baseline cached locally → regression check in CI.

## Installation

Since the project isn’t published yet, install from source:

```bash
git clone https://github.com/p-r-a-v-i-n/perftrack.git
cd perftrack
pip install -r requirements.txt
pip install -e .

```

## Quick start

```bash
# run a command and record performance
perftrack run "python script.py"

# set the latest run as baseline
perftrack baseline set-latest

# later compare new results with baseline
perftrack compare --fail-on-regression

# Generate Simple HTML report
perftrack report

```
Replace "python script.py" with whatever you want to benchmark (scripts, test suites, build steps, ML training, etc.)

## Directory
Perftrack store results under:

```bash
.perftrack/
  baseline.json
  latest.json

```

## CI Example (GitHub Actions)

```yml
name: PerfTrack
on: [push, pull_request]

jobs:
  perf:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - run: pip install -e .

      - run: perftrack run "pytest -q"

      - name: Save baseline on main
        if: github.ref == 'refs/heads/main'
        run: perftrack baseline set-latest

      - name: Compare against baseline
        run: perftrack compare --fail-on-regression
```
