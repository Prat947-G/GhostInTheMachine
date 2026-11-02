"""
GhostInTheMachine: Scheduler Risk & Objective Engine
Implements the Feasibility Gate and the objective score J(i,k)
balancing execution, asymmetric bandwidth bottlenecks, checkpoint cost,
failure risk exposure, and verification overhead.
"""

import math
from typing import Dict, List, Optional
from dag_engine import Task, WorkflowDAG
from worker import Worker
from checkpoint import CheckpointManager


class RiskEngine:
    def __init__(
        self,
        checkpoint_manager: Optional[CheckpointManager] = None,
        gamma: float = 1.0,   # Weight on dependency data transfer time
        delta: float = 0.05,  # Weight on CPU checkpointing tax (serialization + hash)
        eta: float = 1.6,     # Weight on failure risk & restart loss
        rho: float = 1.0,     # Weight on verification/attestation overhead
        checkpoint_interval_sec: float = 10.0,
        durable_store_upload_mbps: float = 100.0,
        durable_store_download_mbps: float = 100.0,
    ):
        self.ckpt_mgr = checkpoint_manager or CheckpointManager()
        self.gamma = gamma
        self.delta = delta
        self.eta = eta
        self.rho = rho
        self.ckpt_interval = checkpoint_interval_sec
        self.store_up = durable_store_upload_mbps
        self.store_down = durable_store_download_mbps

    def is_feasible(self, task: Task, worker: Worker) -> bool:
        """
        Feasibility Gate F(i,k):
        Evaluates memory constraints, capability sets, and attestation status.
        """
        # 1. Memory constraint
        if task.m_i > worker.memory_mb:
            return False
        # 2. Hardware / capability requirement
        if not task.required_capabilities.issubset(worker.capabilities):
            return False
        # 3. Platform trust / attestation appraisal
        if not worker.is_attested:
            return False
        return True

    def compute_checkpoint_cost(self, task: Task, worker: Worker) -> float:
        """
        Calculates CPU-blocking checkpointing cost:
        Serialization CPU time + cryptographic SHA-256 integrity hash + local bus ACK.
        Asynchronous network transmission to durable replica proceeds concurrently in background.
        """
        p_ik = task.w_i / worker.speed
        num_ckpts = max(1, int(round(p_ik / self.ckpt_interval)))
        t_ser = self.ckpt_mgr.get_serialization_time(task.delta_q_i)
        t_ver = self.ckpt_mgr.get_verification_time(task.delta_q_i)
        t_ack = 0.010
        return num_ckpts * (t_ser + t_ver + t_ack)

    def compute_restart_loss(self, task: Task, worker: Worker) -> float:
        """
        Calculates expected restart loss on preemption:
        P_fail * (lost compute + state recovery latency from durable peer replica).
        """
        p_ik = task.w_i / worker.speed
        p_fail = worker.get_failure_probability(p_ik)
        lost_compute = min(p_ik * 0.5, self.ckpt_interval * 0.5)
        # Recovery is from durable peer store -> replacement worker (not failed worker).
        # Bottleneck is min(store upload capacity, replacement worker download).
        t_recover = (
            (task.delta_q_i * 8.0) / min(self.store_up, worker.download_mbps)
            + self.ckpt_mgr.get_restoration_time(task.delta_q_i)
            + self.ckpt_mgr.get_verification_time(task.delta_q_i)
        )
        return p_fail * (lost_compute + t_recover)

    def compute_verification_overhead(self, worker: Worker) -> float:
        """Attestation tax and output verification."""
        return worker.attestation_cpu_tax_sec + 0.02

    def get_optimal_checkpoint_interval(self, task: Task, worker: Worker, time_accel: float = 75.0) -> float:
        """
        Dynamically calculates optimal checkpoint interval tau using Young/Daly relation:
        tau = sqrt(2 * T_ckpt / lambda_eff)
        Clamped to [4.0, task_duration * 0.6] to guarantee meaningful progress between checkpoints.
        """
        if worker.hazard_rate <= 0.005:
            return float("inf")
        eff_hazard_per_sec = (worker.hazard_rate / 3600.0) * time_accel
        t_ser = self.ckpt_mgr.get_serialization_time(task.delta_q_i)
        t_ver = self.ckpt_mgr.get_verification_time(task.delta_q_i)
        t_ckpt_cpu = t_ser + t_ver + 0.010
        tau = math.sqrt((2.0 * t_ckpt_cpu) / max(1e-6, eff_hazard_per_sec))
        task_duration = task.w_i / worker.speed
        return max(4.0, min(task_duration * 0.6, tau))

    def should_checkpoint(self, task: Task, worker: Worker, time_accel: float = 75.0) -> bool:
        """
        Adaptive Risk-Gated Checkpointing:
        Only schedules periodic checkpoints if worker hazard rate > 0.01 and expected preemption
        loss strictly exceeds CPU-blocking checkpoint overhead.
        When lambda_k -> 0, checkpointing overhead drops to 0, matching HEFT under zero churn.
        """
        if worker.hazard_rate <= 0.01:
            return False
        p_ik = task.w_i / worker.speed
        eff_hazard_per_sec = (worker.hazard_rate / 3600.0) * time_accel
        p_fail = 1.0 - math.exp(-eff_hazard_per_sec * p_ik)

        # Expected preemption loss without checkpoint: wasted compute + state recovery latency
        t_retransfer = (task.q_i * 8.0) / min(worker.upload_mbps, 100.0) + 1.5
        expected_loss = p_fail * (0.5 * p_ik + t_retransfer)

        # Checkpoint CPU tax
        tau = self.get_optimal_checkpoint_interval(task, worker, time_accel)
        if math.isinf(tau) or tau <= 0:
            return False
        num_ckpts = max(1, int(round(p_ik / tau)))
        t_ser = self.ckpt_mgr.get_serialization_time(task.delta_q_i)
        t_ver = self.ckpt_mgr.get_verification_time(task.delta_q_i)
        ckpt_tax = num_ckpts * (t_ser + t_ver + 0.010)

        return expected_loss > ckpt_tax

    def compute_objective_score(
        self,
        task: Task,
        worker: Worker,
        dag: WorkflowDAG,
        allocations: Dict[str, str],
        task_finish_times: Dict[str, float],
        worker_avail_time: Dict[str, float],
        workers_map: Optional[Dict[str, Worker]] = None,
        ranks: Optional[Dict[str, float]] = None,
    ) -> float:
        """
        Calculates J(i, k) = EFT(i, k) + eta * Crit(i) * E[restart_loss] + delta * E[ckpt_cpu] + rho * E[ver]
        Incorporates real sender upload capacity from workers_map and critical-path upward rank.
        """
        if not self.is_feasible(task, worker):
            return float("inf")

        # 1. Base Earliest Finish Time (EFT) respecting DAG precedence and transfer delays
        w_avail = worker_avail_time.get(worker.id, 0.0)
        max_pred_arrival = 0.0
        for p_id in dag.predecessors.get(task.id, []):
            p_finish = task_finish_times.get(p_id, 0.0)
            p_worker_id = allocations.get(p_id)
            if p_worker_id and p_worker_id != worker.id:
                p_worker = workers_map.get(p_worker_id) if workers_map else None
                p_worker_up = p_worker.upload_mbps if p_worker else 10.0
                payload = dag.edge_payloads.get((p_id, task.id), 0.0)
                comm_time = (payload * 8.0) / min(p_worker_up, worker.download_mbps) + 0.025
                p_arrival = p_finish + comm_time
            else:
                p_arrival = p_finish
            if p_arrival > max_pred_arrival:
                max_pred_arrival = p_arrival

        eft = max(w_avail, max_pred_arrival) + (task.w_i / worker.speed)

        # 2. Risk and checkpoint penalties
        e_ckpt_cpu = self.compute_checkpoint_cost(task, worker) if self.should_checkpoint(task, worker) else 0.0
        e_restart = self.compute_restart_loss(task, worker)
        e_ver = self.compute_verification_overhead(worker)

        # Criticality weighting: tasks on critical path receive higher preemption protection
        if ranks and max(ranks.values()) > 0:
            norm_rank = ranks.get(task.id, 0.0) / max(ranks.values())
            crit = 1.0 + (norm_rank * 1.5)
        else:
            crit = 1.0 + (len(dag.successors.get(task.id, [])) * 0.25)

        # J(i,k) balances pure EFT with critical path risk exposure and CPU-blocking checkpoint overhead
        return eft + (self.eta * crit * e_restart) + (self.delta * e_ckpt_cpu) + (self.rho * e_ver)
