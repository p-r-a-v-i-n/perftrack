import argparse
import sys
from perftrack import sampler, compare as cmp, report as rpt
import os

def main():
    parser = argparse.ArgumentParser(prog="perftrack", description="PerfTrack CLI")
    sub = parser.add_subparsers(dest="cmd")

    # run
    run_p = sub.add_parser("run", help="Run a command and collect metrics")
    run_p.add_argument("command", help="Command to run, e.g. 'pytest -q'")
    run_p.add_argument("--interval", type=float, default=0.2, help="Sampling interval in seconds")
    run_p.add_argument("--out", default=".perftrack/latest.json", help="Output metrics JSON path")

    # compare
    cmp_p = sub.add_parser("compare", help="Compare baseline and latest")
    cmp_p.add_argument("baseline", nargs="?", default=".perftrack/baseline.json")
    cmp_p.add_argument("latest", nargs="?", default=".perftrack/latest.json")
    cmp_p.add_argument("--threshold", type=float, default=0.10, help="Allowed fractional change (0.1 = 10%)")
    cmp_p.add_argument("--fail-on-regression", action="store_true")

    # report
    rep_p = sub.add_parser("report", help="Render an HTML report from a run JSON")
    rep_p.add_argument("runfile", nargs="?", default=".perftrack/latest.json")
    rep_p.add_argument("--out", default=".perftrack/report.html")

    # baseline
    base_p = sub.add_parser("baseline", help="Baseline operations")
    base_sub = base_p.add_subparsers(dest="action")
    base_sub.add_parser("set-latest", help="Save latest as baseline")
    base_sub.add_parser("path", help="Show current baseline path")

    args = parser.parse_args()

    os.makedirs(".perftrack", exist_ok=True)

    if args.cmd == "run":
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        result = sampler.run_and_measure(args.command, interval=args.interval)
        sampler.save_run(result, args.out)
        print(f"Saved metrics to {args.out}")
        sys.exit(0)

    elif args.cmd == "compare":
        if not os.path.exists(args.baseline):
            print("No baseline found — set one with: perftrack baseline set-latest")
            sys.exit(2)
        code = cmp.compare(args.baseline, args.latest, threshold=args.threshold)
        if args.fail_on_regression and code != 0:
            print("Failing due to regression.")
            sys.exit(1)
        sys.exit(code)

    elif args.cmd == "report":
        rpt.render_html_report(args.runfile, args.out)
        print(f"Report generated at {args.out}")
        sys.exit(0)

    elif args.cmd == "baseline":
        if args.action == "set-latest":
            src = ".perftrack/latest.json"
            dst = ".perftrack/baseline.json"
            if not os.path.exists(src):
                print("No latest run to save as baseline.", file=sys.stderr)
                sys.exit(2)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            import shutil
            shutil.copy2(src, dst)
            print(f"Saved baseline to {dst}")
            sys.exit(0)
        elif args.action == "path":
            path = ".perftrack/baseline.json"
            if os.path.exists(path):
                print(path)
            else:
                print("No baseline saved yet.")
            sys.exit(0)

    else:
        parser.print_help()
        sys.exit(2)

if __name__ == '__main__':
    main()
