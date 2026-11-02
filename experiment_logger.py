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

from collections import defaultdict
import csv
import json
import os
import time
from dataclasses import asdict
from typing import List, Dict, Any, Optional
from network_fault_injector import SimulationMetrics, FailureEvent


class ExperimentLogger:
    def __init__(self, output_dir: str = "telemetry_logs", overwrite: bool = False):
        self.output_dir = output_dir
        self.overwrite = overwrite
        os.makedirs(output_dir, exist_ok=True)
        self.summary_csv_path = os.path.join(output_dir, "telemetry_summary.csv")
        self.events_csv_path = os.path.join(output_dir, "telemetry_events.csv")
        self.provenance_json_path = os.path.join(output_dir, "experiment_provenance.json")

        self.runs: List[Dict[str, Any]] = []
        self.failure_events: List[Dict[str, Any]] = []

        self._init_csv_files()

    def _init_csv_files(self) -> None:
        if self.overwrite or not os.path.exists(self.summary_csv_path):
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
                    "recovery_stall_time_sec",
                    "checkpoint_ser_time_sec",
                    "checkpoint_net_time_sec",
                    "checkpoint_ver_time_sec",
                    "verification_tax_sec",
                    "scheduler_overhead_sec",
                    "goodput_to_overhead_ratio",
                    "total_checkpoint_bytes_mb",
                    "failure_count",
                ])

        if self.overwrite or not os.path.exists(self.events_csv_path):
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
            "recovery_stall_time_sec": round(getattr(metrics, "recovery_stall_time_sec", 0.0), 3),
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
                record["recovery_stall_time_sec"],
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


    def generate_statistical_report(self) -> Dict[str, Any]:
        """
        Compiles rigorous statistical analysis across all telemetry runs:
        - 95% Confidence Intervals (CI_95)
        - Standard Deviations (SD) and Standard Error of Mean (SEM)
        - P50, P95, P99 tail percentiles
        - Pairwise Welch's t-test hypothesis validation against baselines
        Outputs to 'telemetry_statistical_summary.csv' and 'telemetry_hypothesis_tests.csv'.
        """
        if not os.path.exists(self.summary_csv_path):
            return {}

        with open(self.summary_csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            return {}

        import math

        def calc_pct(data, pct):
            if not data: return 0.0
            s = sorted(data)
            k = (len(s) - 1) * (pct / 100.0)
            f = math.floor(k)
            c = math.ceil(k)
            if f == c: return s[int(k)]
            return s[int(f)] * (c - k) + s[int(c)] * (k - f)

        # Group data: (profile, churn, algorithm)
        grouped = defaultdict(lambda: {
            "makespan": [], "gor": [], "lost": [], "miss": [], "fail": []
        })

        for r in rows:
            key = (r["network_profile"], float(r["churn_rate"]), r["algorithm"])
            grouped[key]["makespan"].append(float(r["makespan"]))
            grouped[key]["gor"].append(float(r["goodput_to_overhead_ratio"]))
            grouped[key]["lost"].append(float(r["lost_compute_time_sec"]))
            grouped[key]["miss"].append(float(r["deadline_missed"]))
            grouped[key]["fail"].append(float(r["failure_count"]))

        stat_summary_path = os.path.join(self.output_dir, "telemetry_statistical_summary.csv")
        stat_rows = []

        with open(stat_summary_path, mode="w", newline="", encoding="utf-8") as f_out:
            writer = csv.writer(f_out)
            writer.writerow([
                "network_profile", "churn_rate", "algorithm", "sample_size_N",
                "makespan_mean", "makespan_std", "makespan_sem", "makespan_ci95",
                "makespan_p50", "makespan_p95", "makespan_p99",
                "gor_mean", "gor_std", "gor_ci95",
                "deadline_miss_rate_pct", "avg_lost_compute_sec", "total_failures"
            ])

            for (prof, churn, alg), vals in sorted(grouped.items()):
                n = len(vals["makespan"])
                m_ms = sum(vals["makespan"]) / n
                s_ms = math.sqrt(sum((x - m_ms)**2 for x in vals["makespan"]) / (n - 1)) if n > 1 else 0.0
                sem_ms = s_ms / math.sqrt(n) if n > 0 else 0.0
                ci_ms = 1.96 * sem_ms

                p50_ms = calc_pct(vals["makespan"], 50)
                p95_ms = calc_pct(vals["makespan"], 95)
                p99_ms = calc_pct(vals["makespan"], 99)

                m_gor = sum(vals["gor"]) / n
                s_gor = math.sqrt(sum((x - m_gor)**2 for x in vals["gor"]) / (n - 1)) if n > 1 else 0.0
                ci_gor = 1.96 * (s_gor / math.sqrt(n)) if n > 0 else 0.0

                miss_rate = (sum(vals["miss"]) / n) * 100.0
                lost_sec = sum(vals["lost"]) / n
                tot_fails = sum(vals["fail"])

                row_data = [
                    prof, f"{churn:.2f}", alg, n,
                    round(m_ms, 2), round(s_ms, 2), round(sem_ms, 2), round(ci_ms, 2),
                    round(p50_ms, 2), round(p95_ms, 2), round(p99_ms, 2),
                    round(m_gor, 4), round(s_gor, 4), round(ci_gor, 4),
                    round(miss_rate, 2), round(lost_sec, 2), int(tot_fails)
                ]
                writer.writerow(row_data)
                stat_rows.append(row_data)

        # Hypothesis testing: Proposed-RiskAware vs HEFT & others
        hyp_path = os.path.join(self.output_dir, "telemetry_hypothesis_tests.csv")
        with open(hyp_path, mode="w", newline="", encoding="utf-8") as f_hyp:
            w_hyp = csv.writer(f_hyp)
            w_hyp.writerow([
                "network_profile", "churn_rate", "baseline_compared",
                "proposed_makespan_mean", "baseline_makespan_mean",
                "delta_seconds", "pct_improvement", "welch_t_stat", "df", "p_value", "statistically_significant_p05"
            ])

            profiles = sorted(set(k[0] for k in grouped.keys()))
            churns = sorted(set(k[1] for k in grouped.keys()))

            for prof in profiles:
                for churn in churns:
                    prop_key = (prof, churn, "Proposed-RiskAware")
                    if prop_key not in grouped:
                        continue
                    prop_ms = grouped[prop_key]["makespan"]
                    m_prop = sum(prop_ms) / len(prop_ms)

                    for base_alg in ["HEFT", "Greedy-EFT", "Bounded-ACO"]:
                        base_key = (prof, churn, base_alg)
                        if base_key not in grouped:
                            continue
                        base_ms = grouped[base_key]["makespan"]
                        m_base = sum(base_ms) / len(base_ms)
                        delta = m_base - m_prop
                        pct_imp = (delta / m_base) * 100.0 if m_base > 0 else 0.0

                        # Welch t-test
                        n1, n2 = len(prop_ms), len(base_ms)
                        v1 = sum((x - m_prop)**2 for x in prop_ms) / (n1 - 1) if n1 > 1 else 0.0
                        v2 = sum((x - m_base)**2 for x in base_ms) / (n2 - 1) if n2 > 1 else 0.0
                        se = math.sqrt(v1/n1 + v2/n2)
                        t_stat = (m_prop - m_base) / se if se > 0 else 0.0
                        df = ((v1/n1 + v2/n2)**2) / (max(1e-9, ((v1/n1)**2)/(n1-1) + ((v2/n2)**2)/(n2-1))) if se > 0 else 1.0

                        z = abs(t_stat)
                        t = 1.0 / (1.0 + 0.2316419 * z)
                        poly = t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))))
                        p_val = 2.0 * (1.0 / math.sqrt(2.0 * math.pi)) * math.exp(-0.5 * z * z) * poly
                        p_val = max(1e-6, min(1.0, p_val))

                        w_hyp.writerow([
                            prof, f"{churn:.2f}", base_alg,
                            round(m_prop, 2), round(m_base, 2),
                            round(delta, 2), round(pct_imp, 2),
                            round(t_stat, 3), round(df, 1), round(p_val, 4),
                            "YES" if p_val < 0.05 else "NO"
                        ])

        print(f"Generated Statistical Variance Dossier: {stat_summary_path} and {hyp_path}")
        return {"statistical_summary_path": stat_summary_path, "hypothesis_tests_path": hyp_path}
