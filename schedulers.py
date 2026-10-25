"""
GhostInTheMachine: Schedulers & Baselines
Implements:
1. Greedy Earliest-Finish (Greedy EFT)
2. HEFT (Heterogeneous Earliest Finish Time with upward ranks)
3. Bounded ACO (Ant Colony Optimization with explicit colony/iteration bounds)
4. Proposed Risk-Aware Policy (GhostInTheMachine risk-adjusted scheduler)
5. Exact Small-Instance Reference Solver
"""

import math
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
from dag_engine import WorkflowDAG, Task
from worker import Worker
from risk_engine import RiskEngine


class BaseScheduler(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def schedule(
        self,
        dag: WorkflowDAG,
        workers: List[Worker],
        risk_engine: Optional[RiskEngine] = None,
    ) -> Dict[str, str]:
        """Returns mapping: task_id -> worker_id"""
        pass

    def compute_task_eft(
        self,
        task: Task,
        worker: Worker,
        dag: WorkflowDAG,
        allocations: Dict[str, str],
        task_finish_times: Dict[str, float],
        worker_avail_time: Dict[str, float],
    ) -> float:
        """
        Computes Earliest Finish Time (EFT) of a task on a specific worker.
        EFT = max(worker_avail, max_pred_arrival) + (w_i / s_ik)
        """
        w_avail = worker_avail_time.get(worker.id, 0.0)
        max_pred_arrival = 0.0
        for p_id in dag.predecessors.get(task.id, []):
            p_finish = task_finish_times.get(p_id, 0.0)
            p_worker_id = allocations.get(p_id)
            if p_worker_id and p_worker_id != worker.id:
                p_worker = next((w for w in [worker] if w.id == p_worker_id), None)
                p_up = 10.0 if not p_worker else p_worker.upload_mbps
                payload = dag.edge_payloads.get((p_id, task.id), 0.0)
                comm_time = (payload * 8.0) / min(p_up, worker.download_mbps) + 0.025
                p_arrival = p_finish + comm_time
            else:
                p_arrival = p_finish

            if p_arrival > max_pred_arrival:
                max_pred_arrival = p_arrival

        start_time = max(w_avail, max_pred_arrival)
        finish_time = start_time + (task.w_i / worker.speed)
        return finish_time


class GreedyEFTScheduler(BaseScheduler):
    """
    Greedy Earliest-Finish-Time:
    Traverses DAG topologically, places each task on the worker yielding minimum finish time.
    """
    def __init__(self):
        super().__init__("Greedy-EFT")

    def schedule(
        self,
        dag: WorkflowDAG,
        workers: List[Worker],
        risk_engine: Optional[RiskEngine] = None,
    ) -> Dict[str, str]:
        allocations: Dict[str, str] = {}
        task_finish_times: Dict[str, float] = {}
        worker_avail_time: Dict[str, float] = {w.id: 0.0 for w in workers}
        order = dag.topological_sort()

        for t_id in order:
            task = dag.tasks[t_id]
            best_worker = None
            best_eft = float("inf")

            for w in workers:
                if risk_engine and not risk_engine.is_feasible(task, w):
                    continue
                eft = self.compute_task_eft(
                    task, w, dag, allocations, task_finish_times, worker_avail_time
                )
                if eft < best_eft:
                    best_eft = eft
                    best_worker = w

            if best_worker is None:
                # Fallback to any worker with memory
                best_worker = max(workers, key=lambda w: w.memory_mb)

            allocations[t_id] = best_worker.id
            task_finish_times[t_id] = best_eft
            worker_avail_time[best_worker.id] = best_eft

        return allocations


class HEFTScheduler(BaseScheduler):
    """
    Standard Heterogeneous Earliest Finish Time (HEFT) [Topcuoglu et al. 2002].
    Prioritizes tasks by upward rank, then assigns to worker with minimum EFT.
    """
    def __init__(self):
        super().__init__("HEFT")

    def schedule(
        self,
        dag: WorkflowDAG,
        workers: List[Worker],
        risk_engine: Optional[RiskEngine] = None,
    ) -> Dict[str, str]:
        allocations: Dict[str, str] = {}
        task_finish_times: Dict[str, float] = {}
        worker_avail_time: Dict[str, float] = {w.id: 0.0 for w in workers}

        # 1. Compute upward ranks
        ranks = dag.compute_upward_ranks(workers)
        # Sort tasks descending by rank_u
        sorted_tasks = sorted(dag.tasks.keys(), key=lambda t: ranks[t], reverse=True)

        # 2. Assign tasks by earliest finish time
        for t_id in sorted_tasks:
            task = dag.tasks[t_id]
            best_worker = None
            best_eft = float("inf")

            for w in workers:
                if risk_engine and not risk_engine.is_feasible(task, w):
                    continue
                eft = self.compute_task_eft(
                    task, w, dag, allocations, task_finish_times, worker_avail_time
                )
                if eft < best_eft:
                    best_eft = eft
                    best_worker = w

            if best_worker is None:
                best_worker = workers[0]

            allocations[t_id] = best_worker.id
            task_finish_times[t_id] = best_eft
            worker_avail_time[best_worker.id] = best_eft

        return allocations


class BoundedACOScheduler(BaseScheduler):
    """
    Bounded Ant Colony Optimization (ACO) DAG Scheduler.
    Uses pheromone matrix tau[task][worker], heuristic visibility eta[task][worker],
    colony size limit, and iteration limit.
    """
    def __init__(
        self,
        colony_size: int = 10,
        max_iterations: int = 15,
        rho_evap: float = 0.15,
        alpha: float = 1.0,
        beta: float = 2.0,
        seed: int = 42,
    ):
        super().__init__("Bounded-ACO")
        self.colony_size = colony_size
        self.max_iterations = max_iterations
        self.rho = rho_evap
        self.alpha = alpha
        self.beta = beta
        self.seed = seed

    def schedule(
        self,
        dag: WorkflowDAG,
        workers: List[Worker],
        risk_engine: Optional[RiskEngine] = None,
    ) -> Dict[str, str]:
        rng = random.Random(self.seed)
        task_order = dag.topological_sort()

        # Initialize pheromone matrix
        pheromone: Dict[Tuple[str, str], float] = {
            (t_id, w.id): 1.0 for t_id in task_order for w in workers
        }

        best_makespan = float("inf")
        best_allocation: Dict[str, str] = {}

        for iteration in range(self.max_iterations):
            colony_schedules = []

            for ant in range(self.colony_size):
                ant_alloc: Dict[str, str] = {}
                worker_avail = {w.id: 0.0 for w in workers}
                task_finish = {}

                for t_id in task_order:
                    task = dag.tasks[t_id]
                    # Compute probabilities for feasible workers
                    feasible_workers = [
                        w for w in workers
                        if (not risk_engine or risk_engine.is_feasible(task, w))
                    ]
                    if not feasible_workers:
                        feasible_workers = workers

                    weights = []
                    for w in feasible_workers:
                        eft = self.compute_task_eft(
                            task, w, dag, ant_alloc, task_finish, worker_avail
                        )
                        eta = 1.0 / max(0.1, eft)
                        tau = pheromone.get((t_id, w.id), 1.0)
                        prob_weight = (tau ** self.alpha) * (eta ** self.beta)
                        weights.append(prob_weight)

                    total_w = sum(weights)
                    if total_w > 0:
                        norm_probs = [w / total_w for w in weights]
                        chosen_w = rng.choices(feasible_workers, weights=norm_probs, k=1)[0]
                    else:
                        chosen_w = rng.choice(feasible_workers)

                    ant_alloc[t_id] = chosen_w.id
                    eft = self.compute_task_eft(
                        task, chosen_w, dag, ant_alloc, task_finish, worker_avail
                    )
                    task_finish[t_id] = eft
                    worker_avail[chosen_w.id] = eft

                makespan = max(task_finish.values()) if task_finish else float("inf")
                colony_schedules.append((makespan, ant_alloc))

                if makespan < best_makespan:
                    best_makespan = makespan
                    best_allocation = ant_alloc

            # Pheromone evaporation
            for key in pheromone:
                pheromone[key] *= (1.0 - self.rho)

            # Pheromone deposit by best ant
            if best_allocation:
                deposit = 1.0 / max(1.0, best_makespan)
                for t_id, w_id in best_allocation.items():
                    pheromone[(t_id, w_id)] += deposit

        return best_allocation


class ProposedRiskAwareScheduler(BaseScheduler):
    """
    GhostInTheMachine Proposed Policy:
    Risk-aware, checkpoint-aware DAG placement under asymmetric bandwidth bottlenecks.
    Minimizes objective score J(i, k) while strictly enforcing feasibility gates.
    """
    def __init__(self, risk_engine: Optional[RiskEngine] = None):
        super().__init__("Proposed-RiskAware")
        self.risk_engine = risk_engine or RiskEngine()

    def schedule(
        self,
        dag: WorkflowDAG,
        workers: List[Worker],
        risk_engine: Optional[RiskEngine] = None,
    ) -> Dict[str, str]:
        engine = risk_engine or self.risk_engine
        allocations: Dict[str, str] = {}
        task_finish_times: Dict[str, float] = {}
        worker_avail_time: Dict[str, float] = {w.id: 0.0 for w in workers}
        workers_by_id = {w.id: w for w in workers}

        # 1. Compute upward ranks for prioritization
        ranks = dag.compute_upward_ranks(workers)
        sorted_tasks = sorted(dag.tasks.keys(), key=lambda t: ranks[t], reverse=True)

        for t_id in sorted_tasks:
            task = dag.tasks[t_id]
            best_worker = None
            best_score = float("inf")

            for w in workers:
                # Check feasibility gate first
                if not engine.is_feasible(task, w):
                    continue

                # Calculate Risk-Adjusted Objective Score J(i, k)
                j_score = engine.compute_objective_score(
                    task=task,
                    worker=w,
                    dag=dag,
                    allocations=allocations,
                    task_finish_times=task_finish_times,
                    worker_avail_time=worker_avail_time,
                )

                if j_score < best_score:
                    best_score = j_score
                    best_worker = w
                    best_worker = w

            if best_worker is None:
                # Fallback to worker with lowest hazard rate
                best_worker = min(workers, key=lambda w: w.hazard_rate)

            allocations[t_id] = best_worker.id
            eft = self.compute_task_eft(
                task, best_worker, dag, allocations, task_finish_times, worker_avail_time
            )
            task_finish_times[t_id] = eft
            worker_avail_time[best_worker.id] = eft

        return allocations


class ExactSmallInstanceScheduler(BaseScheduler):
    """
    Branch-and-bound exact solver for small DAGs (<= 8 tasks).
    Guarantees optimal schedule makespan.
    """
    def __init__(self):
        super().__init__("Exact-Solver")

    def schedule(
        self,
        dag: WorkflowDAG,
        workers: List[Worker],
        risk_engine: Optional[RiskEngine] = None,
    ) -> Dict[str, str]:
        task_order = dag.topological_sort()
        best_allocation = {}
        best_makespan = [float("inf")]

        def search(idx: int, current_alloc: Dict[str, str], worker_avail: Dict[str, float], task_finish: Dict[str, float]):
            if idx == len(task_order):
                ms = max(task_finish.values()) if task_finish else 0.0
                if ms < best_makespan[0]:
                    best_makespan[0] = ms
                    best_allocation.clear()
                    best_allocation.update(current_alloc)
                return

            t_id = task_order[idx]
            task = dag.tasks[t_id]
            for w in workers:
                if risk_engine and not risk_engine.is_feasible(task, w):
                    continue
                eft = self.compute_task_eft(task, w, dag, current_alloc, task_finish, worker_avail)
                if eft >= best_makespan[0]:
                    continue  # Prune branch

                prev_w_avail = worker_avail[w.id]
                current_alloc[t_id] = w.id
                worker_avail[w.id] = eft
                task_finish[t_id] = eft

                search(idx + 1, current_alloc, worker_avail, task_finish)

                # Backtrack
                worker_avail[w.id] = prev_w_avail
                del current_alloc[t_id]
                del task_finish[t_id]

        init_avail = {w.id: 0.0 for w in workers}
        search(0, {}, init_avail, {})
        return best_allocation if best_allocation else GreedyEFTScheduler().schedule(dag, workers, risk_engine)
