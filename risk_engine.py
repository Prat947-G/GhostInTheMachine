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
        delta: float = 0.15,  # Weight on checkpointing cost (calibrated: ckpt is background, low priority)
        eta: float = 1.2,     # Weight on failure risk & restart loss
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
        Calculates checkpointing cost:
        Serialization CPU time + network upload time over worker uplink U_k.
        """
        p_ik = task.w_i / worker.speed
        num_ckpts = max(1, int(round(p_ik / self.ckpt_interval)))
        t_ser = self.ckpt_mgr.get_serialization_time(task.delta_q_i)
        t_upload = (task.delta_q_i * 8.0) / min(worker.upload_mbps, self.store_up)
        t_ver = self.ckpt_mgr.get_verification_time(task.delta_q_i)
        t_ack = 0.015
        return num_ckpts * (t_ser + t_upload + t_ver + t_ack)

    def compute_restart_loss(self, task: Task, worker: Worker) -> float:
        """
        Calculates expected restart loss on preemption:
        P_fail * (lost compute + state recovery latency over asymmetric uplink).
        """
        p_ik = task.w_i / worker.speed
        p_fail = worker.get_failure_probability(p_ik)
        lost_compute = min(p_ik * 0.5, self.ckpt_interval * 0.5)
        # Recovery is from durable peer store -> replacement worker (not failed worker).
        # Bottleneck is min(store upload capacity, any replacement worker download).
        # Use the durable store's upload (self.store_up) as the source bandwidth.
        t_recover = (
            (task.delta_q_i * 8.0) / min(self.store_up, worker.download_mbps)
            + self.ckpt_mgr.get_restoration_time(task.delta_q_i)
            + self.ckpt_mgr.get_verification_time(task.delta_q_i)
        )
        return p_fail * (lost_compute + t_recover)

    def compute_verification_overhead(self, worker: Worker) -> float:
        """Attestation tax and output verification."""
        return worker.attestation_cpu_tax_sec + 0.02

    def compute_objective_score(
        self,
        task: Task,
        worker: Worker,
        dag: WorkflowDAG,
        allocations: Dict[str, str],
        task_finish_times: Dict[str, float],
        worker_avail_time: Dict[str, float],
        workers_map: Optional[Dict[str, Worker]] = None,
    ) -> float:
        """
        Calculates J(i, k) = EFT(i, k) + delta*E[ckpt] + eta*E[restart_loss] + rho*E[ver]
        Incorporates real sender upload capacity from workers_map.
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
        e_ckpt = self.compute_checkpoint_cost(task, worker)
        e_restart = self.compute_restart_loss(task, worker)
        e_ver = self.compute_verification_overhead(worker)

        # J(i,k) = EFT(i,k) + delta * E[ckpt_cost] + eta * E[restart_loss] + rho * E[ver_overhead]
        # delta=0.15 reflects that ckpt transfer is async/background; only ser+ver time blocks CPU.
        return eft + self.delta * e_ckpt + self.eta * e_restart + self.rho * e_ver
