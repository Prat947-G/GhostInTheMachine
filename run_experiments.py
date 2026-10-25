"""
GhostInTheMachine: End-to-End Experiment Harness
Executes the comprehensive evaluation scenario matrix across:
- Algorithms: Proposed-RiskAware, HEFT, Bounded-ACO, Greedy-EFT
- Hourly Churn Rates: 0.0 (0%) to 0.30 (30%)
- Network Profiles: Asymmetric Residential (10 Mbps upload) vs Fast Symmetric (100 Mbps upload)
- Independent Random Seeds: 42, 101, 2024, 777, 999
- Generates publication-ready figures upon completion.
"""

import sys
import os
import time
import argparse
from typing import List

from dag_engine import generate_synthetic_dag
from worker import create_heterogeneous_cluster
from risk_engine import RiskEngine
from schedulers import (
    GreedyEFTScheduler,
    HEFTScheduler,
    BoundedACOScheduler,
    ProposedRiskAwareScheduler,
)
from network_fault_injector import DiscreteEventSimulationEngine
from experiment_logger import ExperimentLogger
import generate_paper_artifacts


def run_experiment_matrix(
    seeds: List[int] = [42, 101, 2024, 777, 999],
    churn_rates: List[float] = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30],
    num_tasks: int = 25,
    output_dir: str = "telemetry_logs",
    figures_dir: str = "figures",
):
    print("=" * 75)
    print("GhostInTheMachine: Automated Execution Engine & Telemetry Pipeline")
    print("=" * 75)
    print(f"Random Seeds: {seeds}")
    print(f"Hourly Churn Rates: {[f'{c*100:.0f}%' for c in churn_rates]}")
    print(f"Tasks per Workflow: {num_tasks}")
    print(f"Output Telemetry Directory: {output_dir}")
    print("=" * 75)

    logger = ExperimentLogger(output_dir=output_dir)
    risk_engine = RiskEngine()

    schedulers = [
        ProposedRiskAwareScheduler(risk_engine),
        HEFTScheduler(),
        BoundedACOScheduler(colony_size=10, max_iterations=12),
        GreedyEFTScheduler(),
    ]

    total_runs = len(seeds) * len(churn_rates) * len(schedulers) * 2  # 2 network profiles
    current_run = 0
    start_time = time.time()

    for net_profile in ["asymmetric", "symmetric"]:
        for churn in churn_rates:
            for seed in seeds:
                # 1. Synthesize benchmark workflow DAG
                dag = generate_synthetic_dag(
                    num_tasks=num_tasks,
                    seed=seed,
                    avg_compute_sec=16.0,
                    avg_state_size_mb=40.0,
                    state_delta_ratio=0.20,
                    deadline_factor=1.20,
                )

                # 2. Instantiate heterogeneous P2P compute pool
                workers = create_heterogeneous_cluster(
                    num_workers=8,
                    uplink_profile=net_profile,
                    churn_rate=churn,
                    seed=seed,
                )

                # 3. Execute comparison across schedulers under identical conditions
                for sched in schedulers:
                    current_run += 1
                    t0 = time.time()
                    # Schedule workflow
                    allocations = sched.schedule(dag, workers, risk_engine)
                    sched_overhead = time.time() - t0

                    # Run discrete-event fault/network simulation
                    sim = DiscreteEventSimulationEngine(
                        dag=dag,
                        workers=workers,
                        allocations=allocations,
                        enable_checkpointing=(sched.name == "Proposed-RiskAware"),
                        checkpoint_interval_sec=10.0,
                        use_weibull_churn=(churn > 0.15),
                        seed=seed,
                    )
                    metrics = sim.run()
                    metrics.scheduler_overhead_sec = sched_overhead

                    run_id = f"run_{net_profile}_c{int(churn*100)}_s{seed}_{sched.name}"
                    logger.log_run(
                        run_id=run_id,
                        seed=seed,
                        algorithm=sched.name,
                        churn_rate=churn,
                        network_profile=net_profile,
                        num_tasks=num_tasks,
                        metrics=metrics,
                    )

                    if current_run % 20 == 0 or current_run == total_runs:
                        pct = (current_run / total_runs) * 100.0
                        elapsed = time.time() - start_time
                        print(
                            f"[{current_run:03d}/{total_runs:03d}] ({pct:5.1f}%) | "
                            f"Profile: {net_profile:<10} | Churn: {churn*100:4.1f}% | "
                            f"Alg: {sched.name:<18} | Makespan: {metrics.makespan:6.1f}s | "
                            f"Miss: {'YES' if metrics.deadline_missed else 'NO '} | "
                            f"GOR: {metrics.goodput_to_overhead_ratio:.2f}"
                        )

    print("\n" + "=" * 75)
    print("Telemetry generation complete! Generating publication-ready figures...")
    print("=" * 75)

    os.makedirs(figures_dir, exist_ok=True)
    generate_paper_artifacts.main()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GhostInTheMachine Benchmark Harness")
    parser.add_argument("--tasks", type=int, default=24, help="Number of tasks per DAG")
    parser.add_argument("--quick", action="store_true", help="Run a quick smoke test")
    args = parser.parse_args()

    if args.quick:
        run_experiment_matrix(seeds=[42, 101], churn_rates=[0.0, 0.15, 0.30], num_tasks=12)
    else:
        run_experiment_matrix(seeds=[42, 101, 2024, 777, 999], churn_rates=[0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30], num_tasks=args.tasks)
