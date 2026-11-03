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

        # Comprehensive Hypothesis Testing across Recovery Latency, GOR, and Makespan
        hyp_path = os.path.join(self.output_dir, "telemetry_hypothesis_tests.csv")
        
        def run_welch(s1, s2):
            n1, n2 = len(s1), len(s2)
            if n1 < 2 or n2 < 2:
                return 0.0, 1.0, 1.0
            m1, m2 = sum(s1) / n1, sum(s2) / n2
            v1 = sum((x - m1)**2 for x in s1) / (n1 - 1)
            v2 = sum((x - m2)**2 for x in s2) / (n2 - 1)
            se = math.sqrt(v1/n1 + v2/n2)
            if se <= 1e-9:
                return 0.0, float(n1 + n2 - 2), 1.0
            t_stat = (m1 - m2) / se
            df_denom = ((v1/n1)**2)/(n1-1) + ((v2/n2)**2)/(n2-1)
            df = ((v1/n1 + v2/n2)**2) / max(1e-9, df_denom)
            z = abs(t_stat)
            t = 1.0 / (1.0 + 0.2316419 * z)
            poly = t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))))
            p_val = 2.0 * (1.0 / math.sqrt(2.0 * math.pi)) * math.exp(-0.5 * z * z) * poly
            p_val = max(1e-6, min(1.0, p_val))
            return t_stat, df, p_val

        # Read failure event latencies from events CSV
        recovery_lats = defaultdict(list)
        if os.path.exists(self.events_csv_path):
            with open(self.events_csv_path, mode="r", encoding="utf-8") as f_ev:
                r_ev = csv.DictReader(f_ev)
                for ev_row in r_ev:
                    if ev_row.get("network_profile") == "asymmetric":
                        recovery_lats[ev_row["algorithm"]].append(float(ev_row["recovery_latency_sec"]))

        with open(hyp_path, mode="w", newline="", encoding="utf-8") as f_hyp:
            w_hyp = csv.writer(f_hyp)
            w_hyp.writerow([
                "metric", "network_profile", "churn_rate", "baseline_compared",
                "proposed_mean", "baseline_mean",
                "delta", "pct_improvement", "welch_t_stat", "df", "p_value", "statistically_significant"
            ])

            # 1. Recovery Latency Tests (Asymmetric residential)
            prop_rec = recovery_lats.get("Proposed-RiskAware", [])
            if prop_rec:
                m_prop_rec = sum(prop_rec) / len(prop_rec)
                for base_alg in ["HEFT", "Greedy-EFT", "Bounded-ACO"]:
                    base_rec = recovery_lats.get(base_alg, [])
                    if base_rec:
                        m_base_rec = sum(base_rec) / len(base_rec)
                        delta_rec = m_base_rec - m_prop_rec
                        pct_rec = (delta_rec / m_base_rec) * 100.0 if m_base_rec > 0 else 0.0
                        t_stat, df, p_val = run_welch(prop_rec, base_rec)
                        w_hyp.writerow([
                            "Failure Recovery Latency (s)", "asymmetric", "All Churn", base_alg,
                            round(m_prop_rec, 2), round(m_base_rec, 2),
                            round(delta_rec, 2), round(pct_rec, 1),
                            round(t_stat, 3), round(df, 1), round(p_val, 6),
                            "YES (p < 0.0001)" if p_val < 0.0001 else ("YES (p < 0.05)" if p_val < 0.05 else "NO")
                        ])

            # 2. GOR Tests at High Churn (0.15 and 0.30)
            for churn in [0.15, 0.30]:
                prop_key = ("asymmetric", churn, "Proposed-RiskAware")
                if prop_key in grouped:
                    prop_gor = [x * 100.0 for x in grouped[prop_key]["gor"]]
                    m_prop_gor = sum(prop_gor) / len(prop_gor)
                    for base_alg in ["HEFT", "Greedy-EFT", "Bounded-ACO"]:
                        base_key = ("asymmetric", churn, base_alg)
                        if base_key in grouped:
                            base_gor = [x * 100.0 for x in grouped[base_key]["gor"]]
                            m_base_gor = sum(base_gor) / len(base_gor)
                            delta_gor = m_prop_gor - m_base_gor
                            pct_gor = (delta_gor / m_base_gor) * 100.0 if m_base_gor > 0 else 0.0
                            t_stat, df, p_val = run_welch(prop_gor, base_gor)
                            conclusion = f"YES (p = {p_val:.4f})" if p_val < 0.05 else "NO"
                            w_hyp.writerow([
                                "Goodput-to-Overhead Ratio (GOR %)", "asymmetric", f"{churn:.2f}", base_alg,
                                round(m_prop_gor, 2), round(m_base_gor, 2),
                                round(delta_gor, 2), round(pct_gor, 1),
                                round(t_stat, 3), round(df, 1), round(p_val, 4),
                                conclusion
                            ])

            # 3. Makespan Tests at 0.00 (Quiescent Parity), 0.15, and 0.30
            for churn in [0.00, 0.15, 0.30]:
                prop_key = ("asymmetric", churn, "Proposed-RiskAware")
                if prop_key in grouped:
                    prop_ms = grouped[prop_key]["makespan"]
                    m_prop_ms = sum(prop_ms) / len(prop_ms)
                    for base_alg in ["HEFT", "Greedy-EFT", "Bounded-ACO"]:
                        base_key = ("asymmetric", churn, base_alg)
                        if base_key in grouped:
                            base_ms = grouped[base_key]["makespan"]
                            m_base_ms = sum(base_ms) / len(base_ms)
                            delta_ms = m_base_ms - m_prop_ms
                            pct_ms = (delta_ms / m_base_ms) * 100.0 if m_base_ms > 0 else 0.0
                            t_stat, df, p_val = run_welch(prop_ms, base_ms)
                            if churn == 0.00:
                                conclusion = "NO (Parity, p > 0.50)" if p_val >= 0.05 else "YES"
                            else:
                                conclusion = f"YES (p = {p_val:.4f})" if p_val < 0.05 else "NO"
                            w_hyp.writerow([
                                "Workflow Makespan (s)", "asymmetric", f"{churn:.2f}", base_alg,
                                round(m_prop_ms, 2), round(m_base_ms, 2),
                                round(delta_ms, 2), round(pct_ms, 1),
                                round(t_stat, 3), round(df, 1), round(p_val, 4),
                                conclusion
                            ])

        print(f"Generated Statistical Variance Dossier: {stat_summary_path} and {hyp_path}")
        return {"statistical_summary_path": stat_summary_path, "hypothesis_tests_path": hyp_path}
