"""
GhostInTheMachine: Large-Scale DAG Scalability Benchmark (|V| >= 100)
Validates scheduler scalability and execution overhead across:
|V| in [20, 50, 100, 150] tasks.
Compares Proposed-RiskAware, HEFT, Bounded-ACO, and Greedy-EFT.
Outputs scalability telemetry and runtime analysis for publication rigor.
"""

import os
import sys
import time
import json
from collections import defaultdict

from dag_engine import generate_synthetic_dag
from worker import create_heterogeneous_cluster
from risk_engine import RiskEngine
from schedulers import (
    GreedyEFTScheduler,
    HEFTScheduler,
    BoundedACOScheduler,
    ProposedRiskAwareScheduler,
)

def run_scalability_sweep():
    print("=" * 80)
    print("GhostInTheMachine: Large-DAG Scalability Benchmark (|V| in [20, 50, 100, 150])")
    print("=" * 80)

    task_counts = [20, 50, 100, 150]
    seeds = [42, 101, 777]
    risk_engine = RiskEngine()

    schedulers = [
        ("Proposed-RiskAware", lambda: ProposedRiskAwareScheduler(risk_engine)),
        ("HEFT", lambda: HEFTScheduler()),
        ("Bounded-ACO", lambda: BoundedACOScheduler(colony_size=20, max_iterations=25)),
        ("Greedy-EFT", lambda: GreedyEFTScheduler()),
    ]

    results = []

    for n_tasks in task_counts:
        print(f"\n--- Benchmarking Graph Size |V| = {n_tasks} Tasks ---")
        for seed in seeds:
            dag = generate_synthetic_dag(
                num_tasks=n_tasks,
                seed=seed,
                avg_compute_sec=12.0,
                avg_state_size_mb=35.0,
                state_delta_ratio=0.20,
            )
            workers = create_heterogeneous_cluster(
                num_workers=16 if n_tasks >= 100 else 8,
                uplink_profile="asymmetric",
                churn_rate=0.15,
                seed=seed,
            )

            for name, factory in schedulers:
                sched = factory()
                if hasattr(sched, "set_seed"):
                    sched.set_seed(seed)

                t0 = time.perf_counter()
                allocations = sched.schedule(dag, workers, risk_engine)
                elapsed_sec = time.perf_counter() - t0

                # Compute scheduled makespan (EFT)
                w_clock = {w.id: 0.0 for w in workers}
                w_map = {w.id: w for w in workers}
                t_finish = {}
                order = dag.topological_sort()
                for t_id in order:
                    task = dag.tasks[t_id]
                    w_id = allocations[t_id]
                    w = w_map[w_id]
                    eft = sched.compute_task_eft(
                        task, w, dag, allocations, t_finish, w_clock, w_map
                    )
                    t_finish[t_id] = eft
                    w_clock[w_id] = eft

                makespan = max(t_finish.values()) if t_finish else 0.0

                results.append({
                    "num_tasks": n_tasks,
                    "seed": seed,
                    "algorithm": name,
                    "scheduling_time_ms": round(elapsed_sec * 1000.0, 3),
                    "makespan_sec": round(makespan, 2),
                })
                print(f"  |V|={n_tasks:3d} | Seed={seed:4d} | {name:<18} | Time: {elapsed_sec*1000.0:7.2f} ms | MS: {makespan:6.1f}s")

    # Aggregate by (num_tasks, algorithm)
    agg = defaultdict(lambda: {"time": [], "ms": []})
    for r in results:
        key = (r["num_tasks"], r["algorithm"])
        agg[key]["time"].append(r["scheduling_time_ms"])
        agg[key]["ms"].append(r["makespan_sec"])

    print("\n" + "=" * 80)
    print("SCALABILITY BENCHMARK AGGREGATE SUMMARY:")
    print("=" * 80)
    print(f"{'Tasks (|V|)':<12} | {'Algorithm':<20} | {'Mean Time (ms)':<16} | {'Mean Makespan (s)':<18}")
    print("-" * 80)

    summary_rows = []
    for (n_tasks, alg), vals in sorted(agg.items()):
        mean_time = sum(vals["time"]) / len(vals["time"])
        mean_ms = sum(vals["ms"]) / len(vals["ms"])
        summary_rows.append({
            "num_tasks": n_tasks,
            "algorithm": alg,
            "mean_scheduling_time_ms": round(mean_time, 2),
            "mean_makespan_sec": round(mean_ms, 2),
        })
        print(f"{n_tasks:<12} | {alg:<20} | {mean_time:12.2f} ms  | {mean_ms:14.2f} s")

    out_json = os.path.join("telemetry_logs", "large_dag_scalability_summary.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({"raw_runs": results, "summary": summary_rows}, f, indent=2)
    print(f"\nSaved scalability telemetry to: {out_json}")

if __name__ == "__main__":
    run_scalability_sweep()

