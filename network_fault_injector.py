"""
GhostInTheMachine: Discrete-Event Network & Fault Injection Engine
Simulates:
1. Asymmetric residential bandwidth (D_k >> U_k) and latency
2. Preemption & node churn under Exponential (constant hazard) and Weibull distributions
3. Checkpoint commit acknowledgments, post-failure recovery, and wasted compute tracking
"""

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from dag_engine import WorkflowDAG, Task
from worker import Worker
from checkpoint import CheckpointManager, CheckpointMetadata


@dataclass
class FailureEvent:
    task_id: str
    worker_id: str
    event_time: float
    compute_lost_sec: float
    delta_size_mb: float
    recovery_latency_sec: float
    uplink_mbps: float


@dataclass
class SimulationMetrics:
    makespan: float = 0.0
    deadline: float = 0.0
    deadline_missed: bool = False
    useful_compute_time_sec: float = 0.0
    lost_compute_time_sec: float = 0.0
    checkpoint_ser_time_sec: float = 0.0
    checkpoint_net_time_sec: float = 0.0
    checkpoint_ver_time_sec: float = 0.0
    verification_tax_sec: float = 0.0
    scheduler_overhead_sec: float = 0.0
    total_checkpoint_bytes_mb: float = 0.0
    failure_events: List[FailureEvent] = field(default_factory=list)

    @property
    def total_overhead_sec(self) -> float:
        return (
            self.checkpoint_ser_time_sec
            + self.checkpoint_net_time_sec
            + self.checkpoint_ver_time_sec
            + self.verification_tax_sec
            + self.scheduler_overhead_sec
            + self.lost_compute_time_sec
        )

    @property
    def goodput_to_overhead_ratio(self) -> float:
        """
        GOR = Useful CPU time / (Overhead + Lost Compute)
        """
        overhead = self.total_overhead_sec
        if overhead == 0:
            return 1.0
        return self.useful_compute_time_sec / (self.useful_compute_time_sec + overhead)


class DiscreteEventSimulationEngine:
    def __init__(
        self,
        dag: WorkflowDAG,
        workers: List[Worker],
        allocations: Dict[str, str],
        enable_checkpointing: bool = True,
        checkpoint_interval_sec: float = 10.0,
        use_weibull_churn: bool = False,
        seed: int = 42,
    ):
        self.dag = dag
        self.workers = {w.id: w for w in workers}
        self.allocations = allocations
        self.enable_checkpointing = enable_checkpointing
        self.ckpt_interval = checkpoint_interval_sec
        self.use_weibull_churn = use_weibull_churn
        self.seed = seed
        self.rng = random.Random(seed)
        self.ckpt_mgr = CheckpointManager()

        # Telemetry metrics
        self.metrics = SimulationMetrics(deadline=dag.workflow_deadline)

    def sample_worker_time_to_failure(self, worker: Worker, time_acceleration: float = 35.0) -> float:
        """
        Samples time to next preemption / failure for a worker.
        Uses time_acceleration factor to map workflow scale to hourly churn dynamics.
        """
        if worker.hazard_rate <= 0:
            return float("inf")

        effective_rate_per_sec = (worker.hazard_rate / 3600.0) * time_acceleration

        if self.use_weibull_churn:
            u = max(1e-9, self.rng.random())
            scale = (1.0 / effective_rate_per_sec) * math.gamma(1.0 + 1.0 / worker.weibull_beta)
            return scale * ((-math.log(u)) ** (1.0 / worker.weibull_beta))
        else:
            u = max(1e-9, self.rng.random())
            return -math.log(u) / effective_rate_per_sec

    def run(self) -> SimulationMetrics:
        """
        Executes discrete-event simulation of the scheduled DAG.
        Handles predecessor data transfers, task execution, checkpoint commits,
        preemption injections, and checkpoint delta recovery.
        """
        worker_clock: Dict[str, float] = {w_id: 0.0 for w_id in self.workers}
        task_finish_times: Dict[str, float] = {}
        task_order = self.dag.topological_sort()

        for t_id in task_order:
            task = self.dag.tasks[t_id]
            w_id = self.allocations.get(t_id, list(self.workers.keys())[0])
            worker = self.workers[w_id]

            # 1. Dependency data transfers from all predecessors
            earliest_start = worker_clock[w_id]
            for p_id in self.dag.predecessors.get(t_id, []):
                p_finish = task_finish_times.get(p_id, 0.0)
                p_worker_id = self.allocations.get(p_id)
                if p_worker_id and p_worker_id != w_id:
                    p_worker = self.workers[p_worker_id]
                    payload_mb = self.dag.edge_payloads.get((p_id, t_id), 0.0)
                    # Bottleneck is min(p_worker.upload_mbps, worker.download_mbps)
                    eff_bandwidth = min(p_worker.upload_mbps, worker.download_mbps)
                    latency = max(0.005, self.rng.gauss(0.025, 0.005))
                    transfer_sec = (payload_mb * 8.0) / max(0.1, eff_bandwidth) + latency
                    arrival = p_finish + transfer_sec
                else:
                    arrival = p_finish

                if arrival > earliest_start:
                    earliest_start = arrival

            current_time = earliest_start

            # 2. Attestation tax before executing task
            attest_tax = worker.attestation_cpu_tax_sec
            self.metrics.verification_tax_sec += attest_tax
            current_time += attest_tax

            # 3. Task execution with possible preemption/churn injection
            compute_needed = task.w_i / worker.speed
            compute_completed = 0.0
            last_checkpoint_progress = 0.0

            # Simulate execution until completion (retrying if preempted)
            max_retries = 5
            retries = 0

            while compute_completed < compute_needed and retries < max_retries:
                # Sample preemption time for current worker
                ttf = self.sample_worker_time_to_failure(worker)
                time_remaining = compute_needed - compute_completed

                # Calculate when next checkpoint would occur
                time_to_next_ckpt = self.ckpt_interval - (compute_completed - last_checkpoint_progress)
                if time_to_next_ckpt <= 0:
                    time_to_next_ckpt = self.ckpt_interval

                step = min(time_remaining, ttf, time_to_next_ckpt)
                current_time += step
                compute_completed += step

                if self.enable_checkpointing and (compute_completed - last_checkpoint_progress) >= self.ckpt_interval:
                    # Asynchronous incremental checkpoint delta commit
                    t_ser = self.ckpt_mgr.get_serialization_time(task.delta_q_i)
                    t_net = (task.delta_q_i * 8.0) / min(worker.upload_mbps, 100.0)
                    t_ver = self.ckpt_mgr.get_verification_time(task.delta_q_i)
                    t_ack = 0.015

                    self.metrics.checkpoint_ser_time_sec += t_ser
                    self.metrics.checkpoint_net_time_sec += t_net
                    self.metrics.checkpoint_ver_time_sec += t_ver
                    self.metrics.total_checkpoint_bytes_mb += task.delta_q_i

                    # In asynchronous delta replication, CPU only stalls for serialization + verifier hash;
                    # the uplink transfer proceeds concurrently in the background.
                    current_time += (t_ser + t_ver)

                    # Commit checkpoint
                    ckpt = self.ckpt_mgr.checkpoint(
                        task_id=t_id,
                        state_payload=b"",
                        delta_size_mb=task.delta_q_i,
                        full_state_size_mb=task.q_i,
                        is_incremental=True,
                    )
                    self.ckpt_mgr.commit_checkpoint(ckpt, durable_peer="store_replica")
                    last_checkpoint_progress = compute_completed

                if step == ttf and compute_completed < compute_needed:
                    # PREEMPTION OCCURRED!
                    retries += 1
                    lost_work = compute_completed - last_checkpoint_progress if self.enable_checkpointing else compute_completed
                    self.metrics.lost_compute_time_sec += lost_work

                    # Pick a surviving replacement worker
                    avail_workers = [w for w in self.workers.values() if w.id != worker.id and w.memory_mb >= task.m_i]
                    if not avail_workers:
                        avail_workers = list(self.workers.values())
                    replacement_worker = self.rng.choice(avail_workers)

                    if self.enable_checkpointing:
                        # Restore from latest checkpoint delta transferred from peer replica
                        delta_size = task.delta_q_i
                        # Transfer state delta over peer uplink U_k to replacement worker download D_repl
                        peer_uplink = worker.upload_mbps
                        recovery_bandwidth = min(peer_uplink, replacement_worker.download_mbps)
                        t_xfer = (delta_size * 8.0) / max(0.5, recovery_bandwidth)
                        t_rest = self.ckpt_mgr.get_restoration_time(delta_size)
                        t_v = self.ckpt_mgr.get_verification_time(delta_size)
                        recovery_latency = t_xfer + t_rest + t_v
                        # Rollback progress to last checkpoint
                        compute_completed = last_checkpoint_progress
                    else:
                        # Baseline without checkpointing: must transfer full state and re-execute from scratch
                        full_size = task.q_i
                        peer_uplink = worker.upload_mbps
                        recovery_bandwidth = min(peer_uplink, replacement_worker.download_mbps)
                        t_xfer = (full_size * 8.0) / max(0.5, recovery_bandwidth)
                        recovery_latency = t_xfer + 0.25
                        compute_completed = 0.0
                        delta_size = full_size

                    current_time += recovery_latency

                    # Record failure event telemetry
                    ev = FailureEvent(
                        task_id=t_id,
                        worker_id=worker.id,
                        event_time=round(current_time, 2),
                        compute_lost_sec=round(lost_work, 3),
                        delta_size_mb=round(delta_size, 2),
                        recovery_latency_sec=round(recovery_latency, 3),
                        uplink_mbps=round(worker.upload_mbps, 1),
                    )
                    self.metrics.failure_events.append(ev)

                    # Migrate to replacement worker
                    worker = replacement_worker

            self.metrics.useful_compute_time_sec += (task.w_i / worker.speed)
            task_finish_times[t_id] = current_time
            worker_clock[worker.id] = current_time

        # Simulation completed
        self.metrics.makespan = max(task_finish_times.values()) if task_finish_times else 0.0
        self.metrics.deadline_missed = (self.metrics.makespan > self.metrics.deadline)
        return self.metrics
