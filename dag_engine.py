"""
GhostInTheMachine: DAG Workload Engine
Supports DAG generation, task representations with compute weights, memory constraints,
output payload sizes, state sizes/deltas, and upward rank calculation.
"""

import json
import random
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional


@dataclass
class Task:
    id: str
    name: str
    w_i: float               # Compute weight (seconds on reference 1.0x worker)
    m_i: float               # Memory requirement in MB
    q_i: float               # Full state size in MB
    delta_q_i: float         # Incremental checkpoint delta size in MB
    required_capabilities: Set[str] = field(default_factory=lambda: {"cpu"})
    deadline_slack: float = 1.5   # Relative deadline factor


@dataclass
class WorkflowDAG:
    id: str
    tasks: Dict[str, Task] = field(default_factory=dict)
    # Adjacency list: predecessor -> list of successors
    successors: Dict[str, List[str]] = field(default_factory=dict)
    # Adjacency list: successor -> list of predecessors
    predecessors: Dict[str, List[str]] = field(default_factory=dict)
    # Edge payloads: (src, dst) -> d_ij in MB
    edge_payloads: Dict[Tuple[str, str], float] = field(default_factory=dict)
    workflow_deadline: float = 0.0

    def add_task(self, task: Task) -> None:
        self.tasks[task.id] = task
        if task.id not in self.successors:
            self.successors[task.id] = []
        if task.id not in self.predecessors:
            self.predecessors[task.id] = []

    def add_edge(self, src: str, dst: str, payload_mb: float) -> None:
        if src not in self.tasks or dst not in self.tasks:
            raise ValueError(f"Both {src} and {dst} must exist in the DAG.")
        if dst not in self.successors[src]:
            self.successors[src].append(dst)
        if src not in self.predecessors[dst]:
            self.predecessors[dst].append(src)
        self.edge_payloads[(src, dst)] = payload_mb

    def topological_sort(self) -> List[str]:
        in_degree = {task_id: len(self.predecessors[task_id]) for task_id in self.tasks}
        queue = [task_id for task_id, deg in in_degree.items() if deg == 0]
        result = []
        while queue:
            node = queue.pop(0)
            result.append(node)
            for succ in self.successors.get(node, []):
                in_degree[succ] -= 1
                if in_degree[succ] == 0:
                    queue.append(succ)
        if len(result) != len(self.tasks):
            raise ValueError("Cycle detected in WorkflowDAG or disconnected graph!")
        return result

    def compute_upward_ranks(self, workers: List) -> Dict[str, float]:
        """
        HEFT upward rank:
        rank_u(i) = avg_comp(i) + max_{j in succ(i)} (avg_comm(i,j) + rank_u(j))
        """
        ranks: Dict[str, float] = {}
        order = self.topological_sort()
        order_reversed = list(reversed(order))

        # Average speeds and bandwidths across workers
        avg_speed = sum(w.speed for w in workers) / len(workers)
        # Average effective communication bandwidth across worker pairs
        avg_bandwidth = sum(
            min(w1.upload_mbps, w2.download_mbps)
            for w1 in workers for w2 in workers if w1.id != w2.id
        ) / max(1, len(workers) * (len(workers) - 1))

        for task_id in order_reversed:
            task = self.tasks[task_id]
            avg_comp = task.w_i / avg_speed
            succs = self.successors.get(task_id, [])
            if not succs:
                ranks[task_id] = avg_comp
            else:
                max_succ_term = 0.0
                for s in succs:
                    payload_mb = self.edge_payloads.get((task_id, s), 0.0)
                    avg_comm = (payload_mb * 8.0) / avg_bandwidth  # seconds
                    term = avg_comm + ranks[s]
                    if term > max_succ_term:
                        max_succ_term = term
                ranks[task_id] = avg_comp + max_succ_term
        return ranks

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "workflow_deadline": self.workflow_deadline,
            "tasks": [
                {
                    "id": t.id,
                    "name": t.name,
                    "w_i": t.w_i,
                    "m_i": t.m_i,
                    "q_i": t.q_i,
                    "delta_q_i": t.delta_q_i,
                    "capabilities": list(t.required_capabilities),
                    "deadline_slack": t.deadline_slack,
                }
                for t in self.tasks.values()
            ],
            "edges": [
                {"src": src, "dst": dst, "payload_mb": mb}
                for (src, dst), mb in self.edge_payloads.items()
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkflowDAG":
        dag = cls(id=data["id"], workflow_deadline=data.get("workflow_deadline", 0.0))
        for t_dict in data["tasks"]:
            task = Task(
                id=t_dict["id"],
                name=t_dict["name"],
                w_i=t_dict["w_i"],
                m_i=t_dict["m_i"],
                q_i=t_dict["q_i"],
                delta_q_i=t_dict["delta_q_i"],
                required_capabilities=set(t_dict.get("capabilities", ["cpu"])),
                deadline_slack=t_dict.get("deadline_slack", 1.5),
            )
            dag.add_task(task)
        for e_dict in data["edges"]:
            dag.add_edge(e_dict["src"], e_dict["dst"], e_dict["payload_mb"])
        return dag


def generate_synthetic_dag(
    num_tasks: int = 20,
    seed: int = 42,
    density: float = 0.3,
    avg_compute_sec: float = 15.0,
    state_delta_ratio: float = 0.2,
    avg_state_size_mb: float = 40.0,
    deadline_factor: float = 1.35,
) -> WorkflowDAG:
    """
    Synthesizes a realistic heterogeneous scientific workflow DAG
    (layered diamond/fork-join topology with varying payload and checkpoint sizes).
    """
    rng = random.Random(seed)
    dag = WorkflowDAG(id=f"dag_synth_{num_tasks}_seed{seed}")

    # Generate tasks
    for i in range(num_tasks):
        w_i = rng.uniform(avg_compute_sec * 0.5, avg_compute_sec * 1.5)
        m_i = rng.choice([512.0, 1024.0, 2048.0, 4096.0])
        q_i = rng.uniform(avg_state_size_mb * 0.6, avg_state_size_mb * 1.4)
        delta_q_i = q_i * rng.uniform(state_delta_ratio * 0.8, state_delta_ratio * 1.2)
        caps = {"cpu"}
        if rng.random() < 0.25:
            caps.add("avx")

        task = Task(
            id=f"task_{i}",
            name=f"T{i}",
            w_i=round(w_i, 2),
            m_i=m_i,
            q_i=round(q_i, 2),
            delta_q_i=round(delta_q_i, 2),
            required_capabilities=caps,
        )
        dag.add_task(task)

    # Layered DAG construction to avoid cycles
    # Divide into ~4 to 5 layers
    num_layers = max(3, num_tasks // 4)
    layers: List[List[str]] = [[] for _ in range(num_layers)]
    for idx in range(num_tasks):
        layer_idx = min(num_layers - 1, int((idx / num_tasks) * num_layers))
        layers[layer_idx].append(f"task_{idx}")

    # Ensure every layer has at least one task
    for l_idx in range(num_layers - 1):
        curr_layer = layers[l_idx]
        next_layer = layers[l_idx + 1]
        if not curr_layer or not next_layer:
            continue
        # Connect each task in curr_layer to at least one task in next_layer
        for src in curr_layer:
            dst = rng.choice(next_layer)
            payload = rng.uniform(5.0, 45.0)  # MB
            dag.add_edge(src, dst, round(payload, 2))
        # Ensure each task in next_layer has at least one predecessor
        for dst in next_layer:
            if not dag.predecessors[dst]:
                src = rng.choice(curr_layer)
                payload = rng.uniform(5.0, 45.0)
                dag.add_edge(src, dst, round(payload, 2))
        # Extra random cross-layer edges based on density
        for src in curr_layer:
            for dst in next_layer:
                if (src, dst) not in dag.edge_payloads and rng.random() < density:
                    payload = rng.uniform(5.0, 45.0)
                    dag.add_edge(src, dst, round(payload, 2))

    # Calculate critical path length to set a realistic strict SLA deadline
    # We estimate critical path assuming nominal 1.0x execution speed and ~30 Mbps transfer
    order = dag.topological_sort()
    earliest_finish: Dict[str, float] = {}
    for t_id in order:
        t = dag.tasks[t_id]
        max_pred_finish = 0.0
        for p_id in dag.predecessors[t_id]:
            payload = dag.edge_payloads.get((p_id, t_id), 0.0)
            comm_time = (payload * 8.0) / 30.0
            finish_with_comm = earliest_finish.get(p_id, 0.0) + comm_time
            if finish_with_comm > max_pred_finish:
                max_pred_finish = finish_with_comm
        earliest_finish[t_id] = max_pred_finish + t.w_i

    critical_path = max(earliest_finish.values()) if earliest_finish else 100.0
    dag.workflow_deadline = round(critical_path * deadline_factor, 2)
    return dag
