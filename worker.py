"""
GhostInTheMachine: Worker Node Representation
Defines worker resources, upload/download bandwidth, capability sets,
remote attestation quotes, and churn/preemption parameters.
"""

from dataclasses import dataclass, field
from typing import Set, Optional


@dataclass
class Worker:
    id: str
    speed: float                  # Speed factor relative to reference (e.g. 0.8x to 2.2x)
    memory_mb: float              # Available RAM in MB
    upload_mbps: float            # Upstream bandwidth U_k (asymmetric bottleneck!)
    download_mbps: float          # Downstream bandwidth D_k
    capabilities: Set[str] = field(default_factory=lambda: {"cpu"})
    hazard_rate: float = 0.05     # Hourly failure hazard rate lambda_k (e.g. 0.0 to 0.30)
    weibull_alpha: float = 3600.0 # Scale parameter in seconds (~1 hour)
    weibull_beta: float = 1.2     # Shape parameter (beta > 1 = wear-out/session timeout)
    is_attested: bool = True      # Passed RATS attestation appraisal
    attestation_cpu_tax_sec: float = 0.03  # CPU overhead for attestation nonce verification
    is_alive: bool = True         # Live status during execution simulation
    current_task: Optional[str] = None
    total_busy_time: float = 0.0

    @property
    def hazard_rate_per_sec(self) -> float:
        return self.hazard_rate / 3600.0

    def get_failure_probability(self, duration_sec: float) -> float:
        """
        Failure probability P_fail over interval t under constant hazard rate:
        1 - exp(-lambda * t)
        """
        import math
        return 1.0 - math.exp(-self.hazard_rate_per_sec * duration_sec)


def create_heterogeneous_cluster(
    num_workers: int = 8,
    uplink_profile: str = "asymmetric",  # "asymmetric" (10 Mbps) or "symmetric" (100 Mbps)
    churn_rate: float = 0.10,            # 10% hourly preemption
    seed: int = 42,
) -> list[Worker]:
    """
    Creates a realistic heterogeneous peer-to-peer compute pool.
    """
    import random
    rng = random.Random(seed)
    workers = []

    speeds = [0.8, 1.0, 1.25, 1.5, 1.8, 2.0, 2.2]
    memories = [2048.0, 4096.0, 8192.0, 16384.0]

    for i in range(num_workers):
        speed = rng.choice(speeds)
        mem = rng.choice(memories)
        caps = {"cpu"}
        if rng.random() < 0.4:
            caps.add("avx")

        # Residential asymmetric link profiles:
        # Downlink is fast (50 - 200 Mbps)
        download_mbps = rng.uniform(80.0, 150.0)

        if uplink_profile == "asymmetric":
            # Asymmetric uplink bottleneck: 5 to 15 Mbps (mean ~10 Mbps)
            upload_mbps = rng.uniform(8.0, 12.0)
        elif uplink_profile == "symmetric":
            # High-speed symmetric uplink: 80 to 120 Mbps (mean ~100 Mbps)
            upload_mbps = rng.uniform(80.0, 120.0)
        else:
            upload_mbps = 10.0

        # Churn rate with slight heterogeneity per node
        node_churn = max(0.0, rng.gauss(churn_rate, churn_rate * 0.15))

        w = Worker(
            id=f"worker_{i}",
            speed=speed,
            memory_mb=mem,
            upload_mbps=round(upload_mbps, 2),
            download_mbps=round(download_mbps, 2),
            capabilities=caps,
            hazard_rate=node_churn,
            is_attested=True,
            attestation_cpu_tax_sec=0.035,
        )
        workers.append(w)
    return workers
