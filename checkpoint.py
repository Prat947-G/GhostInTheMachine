"""
GhostInTheMachine: Checkpoint & State Delta Engine
Implements the task-level checkpoint API, state delta representation,
integrity verification, and serialization/restoration latency models.
"""

import hashlib
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class CheckpointMetadata:
    task_id: str
    version: int
    delta_size_mb: float
    full_state_size_mb: float
    is_incremental: bool
    timestamp: float
    content_hash: str
    is_committed: bool = False
    durability_ack_peer: Optional[str] = None


class CheckpointManager:
    """
    Manages task checkpoints, state deltas, serialization timing, and verification.
    """
    def __init__(
        self,
        serialization_rate_mb_per_sec: float = 120.0,  # ~120 MB/s CPU serialization speed
        verification_rate_mb_per_sec: float = 350.0,   # ~350 MB/s SHA256 / integrity check speed
    ):
        self.ser_rate = serialization_rate_mb_per_sec
        self.ver_rate = verification_rate_mb_per_sec
        self.checkpoints: Dict[str, Dict[int, CheckpointMetadata]] = {}

    def checkpoint(
        self,
        task_id: str,
        state_payload: bytes,
        delta_size_mb: float,
        full_state_size_mb: float,
        is_incremental: bool = True,
        version: Optional[int] = None,
    ) -> CheckpointMetadata:
        """
        Task-level checkpoint() API:
        Captures task state delta, computes cryptographic hash, returns metadata.
        """
        if task_id not in self.checkpoints:
            self.checkpoints[task_id] = {}

        v = version if version is not None else len(self.checkpoints[task_id]) + 1
        h = hashlib.sha256(state_payload if state_payload else f"{task_id}_{v}".encode()).hexdigest()

        ckpt = CheckpointMetadata(
            task_id=task_id,
            version=v,
            delta_size_mb=delta_size_mb,
            full_state_size_mb=full_state_size_mb,
            is_incremental=is_incremental,
            timestamp=time.time(),
            content_hash=h,
            is_committed=False,
        )
        self.checkpoints[task_id][v] = ckpt
        return ckpt

    def commit_checkpoint(self, ckpt: CheckpointMetadata, durable_peer: str) -> None:
        """
        Marks checkpoint as committed once durability acknowledgment is received.
        """
        ckpt.is_committed = True
        ckpt.durability_ack_peer = durable_peer

    def restore(self, task_id: str, version: Optional[int] = None) -> CheckpointMetadata:
        """
        Task-level restore() API:
        Retrieves the latest committed valid checkpoint for task recovery.
        """
        if task_id not in self.checkpoints or not self.checkpoints[task_id]:
            raise KeyError(f"No checkpoint available for task {task_id}")

        task_ckpts = self.checkpoints[task_id]
        if version is not None:
            ckpt = task_ckpts.get(version)
            if not ckpt or not ckpt.is_committed:
                raise ValueError(f"Checkpoint version {version} not committed or missing.")
            return ckpt

        # Find latest committed version
        committed = [c for c in task_ckpts.values() if c.is_committed]
        if not committed:
            raise ValueError(f"No committed checkpoint found for task {task_id}")
        return max(committed, key=lambda c: c.version)

    def get_serialization_time(self, size_mb: float) -> float:
        """T_serialize = size_mb / ser_rate"""
        return max(0.001, size_mb / self.ser_rate)

    def get_verification_time(self, size_mb: float) -> float:
        """T_verify = size_mb / ver_rate"""
        return max(0.001, size_mb / self.ver_rate)

    def get_restoration_time(self, size_mb: float) -> float:
        """T_restore = size_mb / ser_rate (deserialization)"""
        return max(0.001, size_mb / (self.ser_rate * 1.2))
