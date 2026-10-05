#!/usr/bin/env python3
"""Measure a deterministic SYNTHETIC cached-calculation workload."""
from __future__ import annotations

import argparse
from datetime import timedelta
import json
import math
import os
from pathlib import Path
import platform
import sys
from time import perf_counter_ns

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aioncrafter.economics import SaleFees, item_economics
from aioncrafter.models import ItemQuantity
from aioncrafter.price_cache import PriceCache
from tests.helpers import catalog, market
from tests.synthetic_prices import Clock, SyntheticProvider, sample


def percentile(values: list[int], fraction: float) -> int:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(len(ordered) * fraction) - 1)]


def cpu_model() -> str:
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.is_file():
        for line in cpuinfo.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lower().startswith("model name") and ":" in line:
                return line.split(":", 1)[1].strip()
    return platform.processor() or "unknown"


def run_benchmark(*, warmup: int, samples: int, target_p95_ms: float) -> dict[str, object]:
    if warmup < 0 or samples < 1 or target_p95_ms <= 0:
        raise ValueError("warmup must be >=0; samples and target must be >0")
    c = catalog()
    recipe = next(r for r in c.recipes if r.recipe_id == "synthetic-bar")
    output = recipe.outcomes[0].outputs[0]
    obs = sample()
    provider = SyntheticProvider((obs,))
    clock = Clock()
    cache = PriceCache(provider, clock=clock, ttl=timedelta(hours=1), max_source_age=timedelta(hours=2))
    identity = obs.identity
    primed = cache.get(identity)
    if primed.cache_hit:
        raise RuntimeError("benchmark cache did not perform its single priming fetch")
    target = ItemQuantity(output.item, output.quantity)
    fees = SaleFees("0.10", "0", "half_up", "SYNTHETIC benchmark assumption")

    def operation() -> None:
        view = cache.get(identity)
        if not view.cache_hit:
            raise RuntimeError("benchmark expected a cached price hit")
        result = item_economics(recipe, target, market(), view.entry.observations, "25.00", fees)
        if result.profit is None:
            raise RuntimeError("benchmark calculation unexpectedly incomplete")

    for _ in range(warmup):
        operation()
    timings: list[int] = []
    for _ in range(samples):
        start = perf_counter_ns()
        operation()
        timings.append(perf_counter_ns() - start)
    if len(provider.calls) != 1:
        raise RuntimeError(f"benchmark made {len(provider.calls)} provider calls; expected exactly 1")

    def ms(ns: int) -> float:
        return round(ns / 1_000_000, 6)

    p95_ms = ms(percentile(timings, 0.95))
    return {
        "schema_version": 1,
        "dataset_kind": "SYNTHETIC",
        "workload": "PriceCache cached hit + deterministic synthetic-bar item_economics",
        "warmup_iterations": warmup,
        "samples": samples,
        "provider_calls": len(provider.calls),
        "target_p95_ms": target_p95_ms,
        "target_met": p95_ms < target_p95_ms,
        "latency_ms": {
            "p50": ms(percentile(timings, 0.50)),
            "p95": p95_ms,
            "p99": ms(percentile(timings, 0.99)),
            "max": ms(max(timings)),
        },
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "cpu_model": cpu_model(),
            "logical_cpus": os.cpu_count(),
            "runner_os": os.environ.get("RUNNER_OS"),
            "runner_arch": os.environ.get("RUNNER_ARCH"),
            "runner_name": os.environ.get("RUNNER_NAME"),
            "github_actions": os.environ.get("GITHUB_ACTIONS") == "true",
            "github_run_id": os.environ.get("GITHUB_RUN_ID"),
            "github_sha": os.environ.get("GITHUB_SHA"),
        },
        "scope_note": "Local deterministic SYNTHETIC workload only; not real-game, provider, browser, or overlay performance.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--warmup", type=int, default=250)
    parser.add_argument("--samples", type=int, default=2000)
    parser.add_argument("--target-p95-ms", type=float, default=300.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_benchmark(warmup=args.warmup, samples=args.samples, target_p95_ms=args.target_p95_ms)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if result["target_met"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
