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
    recovery_stall_time_sec: float = 0.0
    checkpoint_ser_time_sec: float = 0.0
    checkpoint_net_time_sec: float = 0.0
    checkpoint_ver_time_sec: float = 0.0
    verification_tax_sec: float = 0.0
    scheduler_overhead_sec: float = 0.0
    total_checkpoint_bytes_mb: float = 0.0
    failure_events: List[FailureEvent] = field(default_factory=list)

    @property
    def total_overhead_sec(self) -> float:
        # Authentic system overhead accounting:
        # Phase A delta network upload occurs concurrently in the background on the NIC.
        # Only CPU-blocking serialization, verification hash, attestation tax,
        # algorithmic scheduler overhead, lost recompute time, and post-failure recovery stall
        # count as non-productive overhead.
        return (
            self.checkpoint_ser_time_sec
            + self.checkpoint_ver_time_sec
            + self.verification_tax_sec
            + self.scheduler_overhead_sec
            + self.lost_compute_time_sec
            + self.recovery_stall_time_sec
        )

    @property
    def goodput_to_overhead_ratio(self) -> float:
        overhead = self.total_overhead_sec
        if overhead <= 1e-9:
            return 1.0
        return self.useful_compute_time_sec / (self.useful_compute_time_sec + overhead)


class DiscreteEventSimulationEngine:
    def __init__(
        self,
        dag: WorkflowDAG,
        workers: List[Worker],
        allocations: Dict[str, str],
        risk_engine: Optional[Any] = None,
        enable_checkpointing: bool = True,
        checkpoint_interval_sec: float = 10.0,
        use_weibull_churn: bool = False,
        time_acceleration: float = 75.0,
        seed: int = 42,
    ):
        self.dag = dag
        self.workers = {w.id: w for w in workers}
        self.allocations = allocations
        self.risk_engine = risk_engine
        self.enable_checkpointing = enable_checkpointing
        self.ckpt_interval = checkpoint_interval_sec
        self.use_weibull_churn = use_weibull_churn
        self.time_acceleration = time_acceleration
        self.seed = seed
        self.rng = random.Random(seed)
        self.ckpt_mgr = CheckpointManager()

        # Telemetry metrics
        self.metrics = SimulationMetrics(deadline=dag.workflow_deadline)

    def sample_worker_time_to_failure(self, worker: Worker) -> float:
        """
        Samples time to next preemption / failure for a worker.
        Uses time_acceleration factor to map workflow scale to hourly churn dynamics.
        """
        if worker.hazard_rate <= 0:
            return float("inf")

        effective_rate_per_sec = (worker.hazard_rate / 3600.0) * self.time_acceleration

        if self.use_weibull_churn:
            u = max(1e-9, self.rng.random())
            scale = (1.0 / effective_rate_per_sec) * math.gamma(1.0 + 1.0 / worker.weibull_beta)
            return scale * ((-math.log(u)) ** (1.0 / worker.weibull_beta))
        else:
            u = max(1e-9, self.rng.random())
            return -math.log(u) / effective_rate_per_sec

    def run(self, scheduler_overhead_sec: float = 0.0) -> SimulationMetrics:
        """
        Executes discrete-event simulation of the scheduled DAG.
        Handles predecessor data transfers, task execution, checkpoint commits,
        preemption injections, and checkpoint delta recovery.
        """
        worker_clock: Dict[str, float] = {w_id: 0.0 for w_id in self.workers}
        task_finish_times: Dict[str, float] = {}
        task_order = self.dag.topological_sort()
        self.metrics.scheduler_overhead_sec = scheduler_overhead_sec

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

            # 3. Task execution with risk-gated adaptive checkpointing and preemption injection
            compute_needed = task.w_i / worker.speed
            compute_completed = 0.0
            last_checkpoint_progress = 0.0

            # Determine whether to checkpoint this task based on risk gate
            do_checkpoint = (
                self.enable_checkpointing
                and (
                    self.risk_engine.should_checkpoint(task, worker, self.time_acceleration)
                    if (self.risk_engine and hasattr(self.risk_engine, "should_checkpoint"))
                    else (worker.hazard_rate > 0.01)
                )
            )

            if do_checkpoint:
                if self.risk_engine and hasattr(self.risk_engine, "get_optimal_checkpoint_interval"):
                    tau = self.risk_engine.get_optimal_checkpoint_interval(task, worker, self.time_acceleration)
                else:
                    eff_h = (worker.hazard_rate / 3600.0) * self.time_acceleration
                    t_ckpt_cpu = self.ckpt_mgr.get_serialization_time(task.delta_q_i) + self.ckpt_mgr.get_verification_time(task.delta_q_i)
                    tau = max(4.0, min(compute_needed * 0.6, math.sqrt((2.0 * t_ckpt_cpu) / max(1e-6, eff_h))))
            else:
                tau = float("inf")

            max_retries = 5
            retries = 0
            failed_workers: set = set()
            EPSILON = 1e-4

            while (compute_needed - compute_completed) > EPSILON and retries < max_retries:
                ttf = self.sample_worker_time_to_failure(worker)
                time_remaining = compute_needed - compute_completed

                since_last = compute_completed - last_checkpoint_progress
                time_to_next_ckpt = tau - since_last
                if time_to_next_ckpt <= EPSILON:
                    time_to_next_ckpt = tau

                step = min(time_remaining, ttf, time_to_next_ckpt)
                if step < EPSILON:
                    step = time_remaining

                current_time += step
                compute_completed += step

                if do_checkpoint and (compute_completed - last_checkpoint_progress) >= (tau - EPSILON):
                    # Asynchronous incremental checkpoint commit
                    t_ser = self.ckpt_mgr.get_serialization_time(task.delta_q_i)
                    t_net = (task.delta_q_i * 8.0) / min(worker.upload_mbps, 100.0)
                    t_ver = self.ckpt_mgr.get_verification_time(task.delta_q_i)

                    self.metrics.checkpoint_ser_time_sec += t_ser
                    self.metrics.checkpoint_net_time_sec += t_net
                    self.metrics.checkpoint_ver_time_sec += t_ver
                    self.metrics.total_checkpoint_bytes_mb += task.delta_q_i

                    # CPU only stalls for serialization + verifier hash; network transfer is backgrounded
                    current_time += (t_ser + t_ver)

                    ckpt = self.ckpt_mgr.checkpoint(
                        task_id=t_id,
                        state_payload=b"",
                        delta_size_mb=task.delta_q_i,
                        full_state_size_mb=task.q_i,
                        is_incremental=True,
                    )
                    self.ckpt_mgr.commit_checkpoint(ckpt, durable_peer="store_replica")
                    last_checkpoint_progress = compute_completed

                if step == ttf and (compute_needed - compute_completed) > EPSILON:
                    # PREEMPTION OCCURRED!
                    retries += 1
                    failed_workers.add(worker.id)

                    # Pick a surviving replacement worker
                    avail_workers = [
                        w for w in self.workers.values()
                        if w.id not in failed_workers and w.memory_mb >= task.m_i
                    ]
                    if not avail_workers:
                        avail_workers = [w for w in self.workers.values() if w.id != worker.id]
                    if not avail_workers:
                        avail_workers = list(self.workers.values())
                    replacement_worker = self.rng.choice(avail_workers)

                    if self.enable_checkpointing:
                        # Proposed: Rapid recovery from durable peer store replica (100 Mbps uplink)
                        lost_work = compute_completed - last_checkpoint_progress
                        self.metrics.lost_compute_time_sec += lost_work

                        delta_size = task.delta_q_i
                        rec_bw = min(100.0, replacement_worker.download_mbps)
                        t_xfer = (delta_size * 8.0) / max(0.5, rec_bw)
                        t_rest = self.ckpt_mgr.get_restoration_time(delta_size)
                        t_v = self.ckpt_mgr.get_verification_time(delta_size)
                        t_detect = 0.5  # rapid peer heartbeat gossip detection
                        recovery_latency = t_detect + t_xfer + t_rest + t_v
                        compute_completed = last_checkpoint_progress
                    else:
                        # Non-checkpointed baseline recovery:
                        # 1. 100% of elapsed compute is wasted
                        lost_work = compute_completed
                        self.metrics.lost_compute_time_sec += lost_work

                        # 2. Heartbeat timeout
                        t_detect = 1.5

                        # 3. Parent dependency re-transfers over residential uplinks
                        t_retransfer = 0.0
                        for p_id in self.dag.predecessors.get(t_id, []):
                            p_worker_id = self.allocations.get(p_id)
                            p_w = self.workers.get(p_worker_id, worker)
                            payload = self.dag.edge_payloads.get((p_id, t_id), 0.0)
                            bw = min(p_w.upload_mbps, replacement_worker.download_mbps)
                            t_retransfer += (payload * 8.0) / max(0.5, bw) + 0.025

                        # 4. Full state payload transfer bottlenecked by failed worker's uplink U_k (10 Mbps)
                        full_size = task.q_i
                        bw_fail = min(worker.upload_mbps, replacement_worker.download_mbps)
                        t_full = (full_size * 8.0) / max(0.5, bw_fail) + 0.25

                        recovery_latency = t_detect + t_retransfer + t_full
                        compute_completed = 0.0
                        delta_size = full_size

                    self.metrics.recovery_stall_time_sec += recovery_latency
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
                    worker = replacement_worker

            self.metrics.useful_compute_time_sec += (task.w_i / worker.speed)
            task_finish_times[t_id] = current_time
            worker_clock[worker.id] = current_time

        # Simulation completed: incorporate scheduler algorithmic overhead into total makespan
        base_makespan = max(task_finish_times.values()) if task_finish_times else 0.0
        self.metrics.makespan = base_makespan + scheduler_overhead_sec
        self.metrics.deadline_missed = (self.metrics.makespan > self.metrics.deadline)
        return self.metrics
