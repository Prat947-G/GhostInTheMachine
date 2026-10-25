"""
GhostInTheMachine: Command Line Interface (CLI)
Provides commands to generate DAGs, run single schedules, or trigger full benchmark experiments.
"""

import argparse
import sys
import os
import json
from dag_engine import generate_synthetic_dag
from worker import create_heterogeneous_cluster
from risk_engine import RiskEngine
from schedulers import (
    GreedyEFTScheduler,
    HEFTScheduler,
    BoundedACOScheduler,
    ProposedRiskAwareScheduler,
    ExactSmallInstanceScheduler,
)
from network_fault_injector import DiscreteEventSimulationEngine
from experiment_logger import ExperimentLogger
import generate_paper_artifacts


def main():
    parser = argparse.ArgumentParser(
        prog="ghost_cli",
        description="GhostInTheMachine: Risk-Aware Heterogeneous DAG Execution Engine CLI",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Command to run")

    # Command: run-benchmark
    bench_parser = subparsers.add_parser("benchmark", help="Run full scenario matrix benchmark")
    bench_parser.add_argument("--seeds", nargs="+", type=int, default=[42, 101, 2024], help="Random seeds")
    bench_parser.add_argument("--tasks", type=int, default=20, help="Task count per DAG")
    bench_parser.add_argument("--quick", action="store_true", help="Quick smoke test mode")

    # Command: schedule-single
    single_parser = subparsers.add_parser("schedule", help="Schedule and simulate a single DAG run")
    single_parser.add_argument("--tasks", type=int, default=15, help="Number of tasks")
    single_parser.add_argument("--workers", type=int, default=6, help="Number of workers")
    single_parser.add_argument(
        "--algorithm",
        choices=["proposed", "heft", "greedy", "aco", "exact"],
        default="proposed",
        help="Scheduling algorithm",
    )
    single_parser.add_argument("--churn", type=float, default=0.15, help="Hourly churn rate")
    single_parser.add_argument(
        "--profile", choices=["asymmetric", "symmetric"], default="asymmetric", help="Uplink profile"
    )

    # Command: generate-figures
    fig_parser = subparsers.add_parser("figures", help="Generate publication figures from existing logs")
    fig_parser.add_argument("--output-dir", default="figures", help="Directory to save figures")

    args = parser.parse_args()

    if args.subcommand == "benchmark":
        from run_experiments import run_experiment_matrix
        if args.quick:
            run_experiment_matrix(seeds=[42, 101], churn_rates=[0.0, 0.15, 0.30], num_tasks=12)
        else:
            run_experiment_matrix(seeds=args.seeds, num_tasks=args.tasks)

    elif args.subcommand == "figures":
        generate_paper_artifacts.main()

    elif args.subcommand == "schedule":
        print(f"Generating synthetic DAG with {args.tasks} tasks...")
        dag = generate_synthetic_dag(num_tasks=args.tasks, seed=42)
        workers = create_heterogeneous_cluster(
            num_workers=args.workers, uplink_profile=args.profile, churn_rate=args.churn, seed=42
        )
        risk_engine = RiskEngine()

        sched_map = {
            "proposed": ProposedRiskAwareScheduler(risk_engine),
            "heft": HEFTScheduler(),
            "greedy": GreedyEFTScheduler(),
            "aco": BoundedACOScheduler(),
            "exact": ExactSmallInstanceScheduler(),
        }
        scheduler = sched_map[args.algorithm]

        print(f"Running scheduler: {scheduler.name}")
        allocations = scheduler.schedule(dag, workers, risk_engine)
        print("Task Allocations:")
        for t_id, w_id in sorted(allocations.items()):
            print(f"  {t_id} -> {w_id}")

        print("\nSimulating execution under discrete-event fault injector...")
        sim = DiscreteEventSimulationEngine(
            dag=dag,
            workers=workers,
            allocations=allocations,
            enable_checkpointing=(args.algorithm == "proposed"),
            checkpoint_interval_sec=10.0,
            use_weibull_churn=(args.churn > 0.15),
            seed=42,
        )
        metrics = sim.run()

        print("\nExecution Telemetry:")
        print(f"  Makespan:                  {metrics.makespan:.2f} s")
        print(f"  Workflow SLA Deadline:     {metrics.deadline:.2f} s")
        print(f"  Deadline Missed:           {'YES' if metrics.deadline_missed else 'NO'}")
        print(f"  Useful Compute Time:       {metrics.useful_compute_time_sec:.2f} s")
        print(f"  Wasted / Lost Compute:     {metrics.lost_compute_time_sec:.2f} s")
        print(f"  Checkpoint Net Overhead:   {metrics.checkpoint_net_time_sec:.2f} s")
        print(f"  Attestation Tax:           {metrics.verification_tax_sec:.2f} s")
        print(f"  Goodput-to-Overhead Ratio: {metrics.goodput_to_overhead_ratio:.3f}")
        print(f"  Total Failures Incurred:   {len(metrics.failure_events)}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
