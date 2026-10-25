"""
GhostInTheMachine: Experiment Logger & Telemetry Pipeline
Captures:
- Makespan, Deadline Miss Rate
- Goodput-to-Overhead Ratio (GOR)
- State & Network Footprint (Checkpoint bytes vs Recovery Latency)
- Remote Attestation Tax
- Provenance Tracking (seed, network profile, churn, algorithm, timestamp)
Exports to structured CSV and JSON formats.
"""

import csv
import json
import os
import time
from dataclasses import asdict
from typing import List, Dict, Any, Optional
from network_fault_injector import SimulationMetrics, FailureEvent


class ExperimentLogger:
    def __init__(self, output_dir: str = "telemetry_logs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.summary_csv_path = os.path.join(output_dir, "telemetry_summary.csv")
        self.events_csv_path = os.path.join(output_dir, "telemetry_events.csv")
        self.provenance_json_path = os.path.join(output_dir, "experiment_provenance.json")

        self.runs: List[Dict[str, Any]] = []
        self.failure_events: List[Dict[str, Any]] = []

        self._init_csv_files()

    def _init_csv_files(self) -> None:
        if not os.path.exists(self.summary_csv_path):
            with open(self.summary_csv_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "run_id",
                    "timestamp",
                    "seed",
                    "algorithm",
                    "churn_rate",
                    "network_profile",
                    "num_tasks",
                    "makespan",
                    "deadline",
                    "deadline_missed",
                    "useful_compute_time_sec",
                    "lost_compute_time_sec",
                    "checkpoint_ser_time_sec",
                    "checkpoint_net_time_sec",
                    "checkpoint_ver_time_sec",
                    "verification_tax_sec",
                    "scheduler_overhead_sec",
                    "goodput_to_overhead_ratio",
                    "total_checkpoint_bytes_mb",
                    "failure_count",
                ])

        if not os.path.exists(self.events_csv_path):
            with open(self.events_csv_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "run_id",
                    "seed",
                    "algorithm",
                    "churn_rate",
                    "network_profile",
                    "task_id",
                    "worker_id",
                    "event_time",
                    "compute_lost_sec",
                    "delta_size_mb",
                    "recovery_latency_sec",
                    "uplink_mbps",
                ])

    def log_run(
        self,
        run_id: str,
        seed: int,
        algorithm: str,
        churn_rate: float,
        network_profile: str,
        num_tasks: int,
        metrics: SimulationMetrics,
    ) -> None:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        record = {
            "run_id": run_id,
            "timestamp": ts,
            "seed": seed,
            "algorithm": algorithm,
            "churn_rate": churn_rate,
            "network_profile": network_profile,
            "num_tasks": num_tasks,
            "makespan": round(metrics.makespan, 3),
            "deadline": round(metrics.deadline, 3),
            "deadline_missed": 1 if metrics.deadline_missed else 0,
            "useful_compute_time_sec": round(metrics.useful_compute_time_sec, 3),
            "lost_compute_time_sec": round(metrics.lost_compute_time_sec, 3),
            "checkpoint_ser_time_sec": round(metrics.checkpoint_ser_time_sec, 3),
            "checkpoint_net_time_sec": round(metrics.checkpoint_net_time_sec, 3),
            "checkpoint_ver_time_sec": round(metrics.checkpoint_ver_time_sec, 3),
            "verification_tax_sec": round(metrics.verification_tax_sec, 3),
            "scheduler_overhead_sec": round(metrics.scheduler_overhead_sec, 4),
            "goodput_to_overhead_ratio": round(metrics.goodput_to_overhead_ratio, 4),
            "total_checkpoint_bytes_mb": round(metrics.total_checkpoint_bytes_mb, 2),
            "failure_count": len(metrics.failure_events),
        }
        self.runs.append(record)

        # Append to summary CSV
        with open(self.summary_csv_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                record["run_id"],
                record["timestamp"],
                record["seed"],
                record["algorithm"],
                record["churn_rate"],
                record["network_profile"],
                record["num_tasks"],
                record["makespan"],
                record["deadline"],
                record["deadline_missed"],
                record["useful_compute_time_sec"],
                record["lost_compute_time_sec"],
                record["checkpoint_ser_time_sec"],
                record["checkpoint_net_time_sec"],
                record["checkpoint_ver_time_sec"],
                record["verification_tax_sec"],
                record["scheduler_overhead_sec"],
                record["goodput_to_overhead_ratio"],
                record["total_checkpoint_bytes_mb"],
                record["failure_count"],
            ])

        # Append failure events
        for ev in metrics.failure_events:
            ev_record = {
                "run_id": run_id,
                "seed": seed,
                "algorithm": algorithm,
                "churn_rate": churn_rate,
                "network_profile": network_profile,
                "task_id": ev.task_id,
                "worker_id": ev.worker_id,
                "event_time": ev.event_time,
                "compute_lost_sec": ev.compute_lost_sec,
                "delta_size_mb": ev.delta_size_mb,
                "recovery_latency_sec": ev.recovery_latency_sec,
                "uplink_mbps": ev.uplink_mbps,
            }
            self.failure_events.append(ev_record)
            with open(self.events_csv_path, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    ev_record["run_id"],
                    ev_record["seed"],
                    ev_record["algorithm"],
                    ev_record["churn_rate"],
                    ev_record["network_profile"],
                    ev_record["task_id"],
                    ev_record["worker_id"],
                    ev_record["event_time"],
                    ev_record["compute_lost_sec"],
                    ev_record["delta_size_mb"],
                    ev_record["recovery_latency_sec"],
                    ev_record["uplink_mbps"],
                ])

        # Write provenance JSON (MLflow tracking compatible schema)
        provenance = {
            "mlflow_schema_version": "1.0",
            "experiment_name": "GhostInTheMachine_Benchmark",
            "total_runs": len(self.runs),
            "latest_run": record,
        }
        with open(self.provenance_json_path, mode="w", encoding="utf-8") as f:
            json.dump(provenance, f, indent=2)
