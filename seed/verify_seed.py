"""Check what actually landed after seeding."""

import argparse
import collections

import opik
from opik.rest_api.core.api_error import ApiError


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="odsc-analytics")
    args = parser.parse_args()

    client = opik.Opik()
    try:
        traces = client.search_traces(project_name=args.project, max_results=10000)
    except ApiError as exc:
        if exc.status_code != 404:  # 404: the project doesn't exist until its first trace lands
            raise
        traces = []
    if not traces:
        print(f"no traces in '{args.project}'")
        return

    durations = sorted(t.duration for t in traces if t.duration)
    errors = sum(1 for t in traces if t.error_info)
    costs = [t.total_estimated_cost for t in traces if t.total_estimated_cost]
    span_counts = collections.Counter(t.span_count for t in traces)

    def pct(p):
        return durations[min(int(len(durations) * p / 100), len(durations) - 1)]

    oldest = min(t.start_time for t in traces)
    newest = max(t.start_time for t in traces)

    print(f"project      : {args.project}")
    print(f"traces       : {len(traces)}")
    print(f"time span    : {oldest} -> {newest}")
    print(f"errors       : {errors} ({errors / len(traces) * 100:.1f}%)")
    print(f"latency p50  : {pct(50):.0f} ms")
    print(f"latency p95  : {pct(95):.0f} ms")
    print(f"latency p99  : {pct(99):.0f} ms")
    print(f"cost total   : ${sum(costs):.6f} across {len(costs)} priced traces")
    print(f"spans/trace  : {dict(sorted(span_counts.items()))}")


if __name__ == "__main__":
    main()
