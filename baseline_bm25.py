"""Backward-compatible entry point for the benchmark harness BM25 run."""

import sys

from benchmark_harness.run_retrieval_benchmark import main


if __name__ == "__main__":
    arguments = sys.argv[1:]
    if not arguments or arguments[0].startswith("-"):
        arguments = ["benchmark", *arguments]
    raise SystemExit(main(arguments))
