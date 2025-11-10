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

## CI Regression Example
PerfTrack guarantees that performance regressions are caught before merge.
Here is a [pull request]([url](https://github.com/p-r-a-v-i-n/perftrack-examples/pull/7)) where we intentionally slowed down code to demonstrate PerfTrack in CI.

<img width="741" height="209" alt="perftrack" src="https://github.com/user-attachments/assets/25eca2c6-0226-4608-9614-a2eb0102e67e" />


