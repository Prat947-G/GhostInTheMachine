# Upload-Aware Risk-Adjusted DAG Scheduling and Incremental State-Delta Recovery for Heterogeneous Volunteer Compute Networks

**Authors**:  
Prathmesh Kadam$^1$, Ashwani Kumar$^1$, Rishabh Ladha$^1$, Pavan Meka$^1$, Lakshita Wadhera$^1$, Ayush Raj$^1$  
$^1$*Department of Computer Science and Engineering, Lovely Professional University, Phagwara, Punjab, India*  
*{prathmesh.12317688, ashwani.12318852, rishabh.12317813, pavan.12317192, lakshita.12314203, ayush.12308724}@lpu.in*

---

## Abstract
Aggregating computational capacity from personal workstations and edge devices offers a low-cost, decentralized alternative to static cloud data centers. However, scheduling dependent workflows (DAGs) across consumer-grade volunteer nodes introduces fundamental systems challenges: worker availability is stochastic, computational capabilities are heterogeneous, and residential broadband connections exhibit severe directional bandwidth asymmetry where downstream capacity dwarfs upstream bandwidth ($D_k \gg U_k$, typically 10:1 to 20:1). When a volunteer node abruptly disconnects, existing cluster schedulers force either complete task re-execution or costly whole-image migration, triggering catastrophic bandwidth saturation on throttled consumer uplinks. 

This paper presents **GhostInTheMachine**, an upload-aware, risk-adjusted directed acyclic graph runtime engineered specifically for intermittently available volunteer networks. The architecture couples three primary contributions: (1) an asymmetric transmission and risk-adjusted objective function $J(i,k)$ that evaluates task placement against residential uplink bottlenecks, expected state-delta replication taxes, and restart penalties; (2) a decoupled, asynchronous state-delta checkpointing engine that bounds uncommitted progress; and (3) an IETF RFC 9334 RATS-compliant feasibility gate that cryptographically validates hardware measurements at admission time. 

Evaluating a 1,120-run simulation matrix across Poisson hazard rates ($\lambda \in [0.00, 0.30]$/hr) and residential uplink profiles (20 deterministic seeds per condition) reveals that while makespan remains statistically tied under quiescent zero churn (137.6s vs. 137.6s for HEFT, $p = 1.00$), incremental state-delta checkpointing delivers the primary system breakthrough: reducing failure recovery latency from 62.32s ± 6.57s down to 1.28s ± 0.05s under constrained 10 Mbps residential uplinks. This 98.0% (49x) latency reduction prevents cascading preemption collapses, bounding SLA deadline miss rates strictly to 0.0% where legacy heuristics experience 20%–25% deadline violations, while sustaining a Goodput-to-Overhead Ratio (GOR) of 96.8%–97.1% under heavy churn (against 79.1%–81.5% for baselines) and 99.59% under zero churn. Hardware-in-the-loop microbenchmarks validate that physical CPU serialization (>4,900 MB/s) and SHA-256 attestation (>1,800 MB/s) comfortably outpace simulation thresholds, while residential Wi-Fi burst loss (1.53%) and bufferbloat (+131 ms RTT inflation) further underscore the imperative for lightweight state deltas.

**Keywords**—DAG scheduling, volunteer computing, peer-to-peer systems, checkpointing, asymmetric bandwidth, fault tolerance, remote attestation, goodput-to-overhead ratio.

---

## I. Introduction
Decentralized and volunteer compute networks aggregate idle compute cycles across consumer laptops, personal desktops, and edge workstations to support distributed batch processing, graphics rendering, and deep learning parameter sweeps [1], [3]. While commercial GPU rental marketplaces such as Vast.ai rely on dedicated mining rigs housed in static facilities with symmetric enterprise fiber, genuine consumer volunteer networks operate under fundamentally harsher physical constraints:
1. **Asymmetric Residential Bandwidth ($D_k \gg U_k$):** Consumer broadband connections typically deliver 80–150 Mbps downlink throughput but restrict upstream bandwidth to 5–15 Mbps (a 10:1 to 20:1 asymmetry). In a dependent workflow represented as a Directed Acyclic Graph (DAG) $G = (V, E)$, intermediate task payloads and checkpoint states transferred across distinct physical machines are strictly throttled by the sender's uplink capacity rather than the receiver's downlink.
2. **Stochastic Node Churn & Unannounced Preemption:** Unlike managed data centers, volunteer hosts are shared with local device owners who retain absolute preemptive priority. Hosts experience sudden disconnections caused by sleep states, network interruptions, or owner reclamation.
3. **Hardware Untrustworthiness & Telemetry Falsification:** In an open peer-to-peer marketplace, participating hosts may misreport available memory, clock frequencies, or execution completion to claim economic incentives without performing work.

Classical list scheduling heuristics, most notably Heterogeneous Earliest Finish Time (HEFT) [1], optimize for finish times assuming static node reliability and symmetric communication links. Similarly, bio-inspired metaheuristics such as Ant Colony Optimization (ACO) explore broad assignment combinations but remain blind to asymmetric link penalties and checkpoint durability overheads. In the presence of host failures, conventional volunteer systems either restart aborted tasks from scratch [3] or attempt coarse virtual-machine snapshots [5], both of which choke residential uplinks during recovery.

### Research Questions & Key Contributions
This paper investigates the following systems questions:
- *How can task placement policies account for upstream bandwidth bottlenecks and failure hazard rates without introducing prohibitive scheduling latency?*
- *To what extent can decoupled, incremental state-delta checkpointing protect workflow deadlines and computational goodput under severe residential upload throttling?*

To resolve these questions, we design, implement, and evaluate **GhostInTheMachine**. This paper provides three primary technical contributions:
1. **Upload-Aware Risk-Adjusted Formulation:** We formalize a placement score $J(i,k)$ that balances earliest finish time (EFT) under directional bandwidth constraints, expected checkpoint serialization and transmission overheads, and preemption restart risk.
2. **Decoupled Incremental State-Delta Checkpoint Engine:** We architect a lightweight runtime interface that serializes state deltas ($\Delta q_i$) and replicates them asynchronously to surviving peer stores, reducing failover recovery latency from 62.32s down to 1.28s (a 98.0% reduction) on 10 Mbps residential links.
3. **Statistical Telemetry, Large-DAG Scalability, & Physical Hardware Calibration:** We conduct an exhaustive 1,120-run evaluation matrix (20 deterministic seeds per condition) capturing 95% Confidence Intervals (CI), standard deviations, and Welch’s t-tests, complemented by large-DAG scalability benchmarks ($|V| \in [20, 150]$) and hardware microbenchmarks calibrating physical serialization, cryptographic attestation, Wi-Fi loss, and bufferbloat against simulation assumptions.

---

## II. Related Work

### A. Heterogeneous Workflow DAG Scheduling & Standard Workflow Traces
Static scheduling of dependent task graphs onto heterogeneous processors is NP-complete. Topcuoglu et al. established HEFT [1], which computes upward ranks ($\text{rank}_u$) based on average computation and communication costs, greedily allocating tasks to processors offering the earliest finish time. Standard benchmark workflows from the Pegasus repository [9], including Montage (astronomical mosaic creation), CyberShake (earthquake hazard estimation), Epigenomics (DNA genome sequencing), and LIGO Inspiral (gravitational wave analysis), exhibit multi-tiered diamond and pipeline structures. Variants such as PEFT and lookahead heuristics improve path planning but universally presume dedicated processors and symmetric interconnection networks. In contrast, GhostInTheMachine explicitly bounds inter-node communication by sender uplink $U_k$ and evaluates preemption risk during candidate selection.

Metaheuristic scheduling, such as Ant Colony Optimization (ACO) [2], uses artificial ants depositing pheromone trails on task-worker edges. While flexible, ACO requires careful tuning of pheromone decay ($\rho$) and visibility heuristics ($\eta$) to avoid premature convergence. In our benchmark, we tune Bounded ACO using Max-Min Ant System (MMAS) principles with realistic search budgets.

### B. Fault Tolerance & Checkpointing in Volatile Networks
In volunteer computing (e.g., BOINC [3]), tasks are typically independent embarrassingly parallel chunks. When workflow dependencies are introduced, preemption of an intermediate task cascades through the graph. Daly established optimal checkpoint intervals for single long-running jobs based on Poisson failure rates [8]. However, Benoit et al. proved that applying Daly's single-task formula directly to concurrent workflow DAGs fails because checkpoint I/O competes with task communication [4]. GhostInTheMachine builds on these findings by decoupling state-delta replication from critical-path execution, limiting synchronous CPU blocking to memory serialization while network uploads proceed in the background.

### C. Zero-Trust Hardware Attestation
Volunteer platforms cannot assume host integrity. Following the IETF Remote ATtestation procedureS (RATS) architecture (RFC 9334) [6], our framework decouples platform attestation (verifying hardware identity, firmware state, and hardware roots of trust via nonce-bound quotes) from application output verification (cryptographic output hashing and audit vouchers).

---

## III. System Model & Problem Formulation

### A. Workflow DAG Representation
A computational workload is modeled as a directed acyclic graph $G = (V, E)$, modeled after standard Pegasus benchmark workflow traces [9]. Each task $i \in V$ is defined by the tuple:
$$\tau_i = \langle w_i, m_i, q_i, \Delta q_i, c_i \rangle$$
where:
- $w_i$: Normalized compute demand in reference core-seconds ($1.0\times$).
- $m_i$: Peak working memory requirement in megabytes (MB).
- $q_i$: Full task state snapshot size (MB).
- $\Delta q_i$: Incremental state delta per checkpoint interval (MB), where $\Delta q_i \ll q_i$ (empirically $0.15 q_i$ to $0.25 q_i$).
- $c_i$: Required capability set (e.g., `cpu`, `avx`, `gpu`).

Directed edges $(i, j) \in E$ specify dependencies, where task $j$ cannot begin execution until task $i$ completes and delivers payload $d_{ij}$ (MB).

### B. Heterogeneous Asymmetric Worker Pool
The worker pool $K$ contains heterogeneous consumer hosts. Each worker $k \in K$ is defined by:
$$W_k = \langle s_{ik}, M_k, U_k, D_k, C_k, \lambda_k, (\alpha_k, \beta_k), \text{Attest}_k \rangle$$
- $s_{ik}$: Relative execution speedup factor ($0.8\times$ to $2.2\times$).
- $M_k$: Available host RAM (MB).
- $U_k, D_k$: Physical upstream and downstream bandwidth (Mbps). For residential consumer links, $D_k \approx 80\text{--}150$ Mbps, while $U_k \approx 8\text{--}12$ Mbps.
- $C_k$: Advertised hardware capabilities.
- $\lambda_k$: Memoryless Poisson preemption hazard rate per hour ($\lambda_k \in [0.00, 0.30]$).
- $(\alpha_k, \beta_k)$: Weibull distribution parameters governing host session fatigue. When host session wear-out dominates, the survival function is $R(t) = \exp(-(t/\alpha_k)^{\beta_k})$ with shape parameter $\beta_k > 1$.
- $\text{Attest}_k$: Boolean flag indicating whether the worker has passed fresh cryptographic remote attestation under RFC 9334.

### C. Transmission Delay over Directional Asymmetric Links
When task $i$ assigned to worker $k = \text{loc}(i)$ transfers payload $d_{ij}$ to dependent task $j$ assigned to worker $l = \text{loc}(j)$:
$$\text{Comm}(i, j) = \begin{cases} 0, & \text{if } k = l \\ \frac{d_{ij} \cdot 8}{\min(U_k, D_l)} + L_{kl}, & \text{if } k \ne l \end{cases}$$
Because $U_k \ll D_l$ in residential configurations, $\min(U_k, D_l) \equiv U_k$. Inter-node transfer time is strictly governed by the sender's uplink.

---

## IV. The GhostInTheMachine Runtime Architecture

### A. The Feasibility Gate (Policy Filter)
Prior to ranking workers for task $i$, the runtime applies a hard admission filter $F(i, k) \in \{0, 1\}$:
$$F(i, k) = \mathbb{I}(m_i \le M_k) \cdot \mathbb{I}(c_i \subseteq C_k) \cdot \mathbb{I}(\text{Attest}_k == \text{VALID})$$
Any host lacking required physical RAM, missing required instruction sets, or presenting an invalid/expired attestation quote is pruned immediately:
$$J_{\text{admit}}(i, k) = \begin{cases} J(i, k), & \text{if } F(i, k) = 1 \\ \infty, & \text{if } F(i, k) = 0 \end{cases}$$

### B. Risk-Aware Objective Function $J(i, k)$
For feasible candidates ($F(i, k) = 1$), the baseline Earliest Finish Time (EFT) is computed as:
$$\text{EST}(i, k) = \max\left(\text{avail}[k], \max_{p \in \text{Pred}(i)} \left( \text{finish}[p] + \text{Comm}(p, i) \right)\right)$$
$$\text{EFT}(i, k) = \text{EST}(i, k) + \frac{w_i}{s_{ik}}$$

GhostInTheMachine selects the host minimizing the composite risk objective score:
$$J(i, k) = \text{EFT}(i, k) + \text{Crit}(i) \cdot \left[ \delta \cdot E[\text{ckpt\_cpu}_{ik}] + \eta \cdot E[\text{restart}_{ik}] + \rho \cdot E[\text{ver}_{ik}] \right]$$

where:
- $\text{Crit}(i) = 1.0 + 1.5 \cdot \frac{\text{rank}_u(i)}{\max(\text{rank}_u)}$: Task upward rank weighting ensuring that critical-path tasks receive prioritized placement on high-reliability, verified hosts.
- $E[\text{ckpt\_cpu}_{ik}] = N_{\text{ckpt}} \cdot (T_{\text{ser}} + T_{\text{ver}} + T_{\text{ack}})$: Synchronous CPU serialization and verification tax (with $\delta = 0.05$ reflecting asynchronous background network transmission). Checkpoint count $N_{\text{ckpt}} = \lfloor p_{ik} / \tau_{\text{opt}} \rfloor$ is dynamically gated by Young/Daly interval $\tau_{\text{opt}} = \sqrt{2 T_{\text{ckpt}} / \lambda_{\text{eff}}}$.
- $E[\text{restart}_{ik}] = P_{\text{fail}}(i, k) \cdot \left[ \min\left(\frac{p_{ik}}{2}, \frac{\tau_{\text{opt}}}{2}\right) + \frac{\Delta q_i \cdot 8}{\min(U_{\text{store}}, D_k)} + T_{\text{restore}} \right]$: Expected restart loss under preemption hazard (scaled by $\eta = 1.6$).
- $E[\text{ver}_{ik}] = T_{\text{attest}}(k) + T_{\text{audit}}(i)$: Attestation verification cost (scaled by $\rho = 1.0$).

### C. Decoupled Durability & Asynchronous Checkpointing
To decouple state durability from the critical execution path:
- **Phase 1 (Memory Serialization & Digest):** When execution hits checkpoint interval $\tau_{\text{opt}}$, the worker serializes memory delta $\Delta q_i$ and computes SHA-256 digest $H(\Delta q_i)$. The execution thread stalls only for duration $T_{\text{ser}} + T_{\text{ver}}$ before resuming computational progress.
- **Phase 2 (Asynchronous Network Upload):** In parallel, an I/O thread streams $\Delta q_i$ across uplink $U_k$ to a resilient peer replica node (100 Mbps uplink).
- **Phase 3 (Crash Recovery):** If worker $k$ disconnects, the central coordinator detects preemption, designates a replacement worker $k'$, retrieves the latest committed checkpoint delta $\Delta q_i$ from the durable replica store, and resumes execution from progress marker $\tau_{\text{last}}$.

```
ALGORITHM 1: RiskAwareDAGScheduler
Input:  Workflow DAG G = (V, E), Worker Pool K, Parameters delta, eta, rho
Output: Task-to-Worker Allocation Map

1:  Compute upward ranks rank_u(i) for all tasks i in V using HEFT formulation
2:  Sort tasks descending by rank_u into PriorityQueue Q; max_rank = max_{j}(rank_u(j))
3:  Initialize worker availability clock avail[k] = 0.0 for all k in K
4:  While Q is not empty do
5:      task i = Pop(Q); best_worker = null, min_score = infinity
6:      Crit_i = 1.0 + 1.5 * (rank_u(i) / max_rank)
7:      For each candidate worker k in K do
8:          // Step 1: Evaluate Feasibility Gate
9:          If not (m_i <= M_k and c_i subset of C_k and Attest(k) == VALID) then
10:             Continue // Prune worker: J(i, k) = infinity
11:         End If
12:         // Step 2: Compute Earliest Finish Time with Uplink Bottlenecks
13:         EST_ik = max(avail[k], max_{p in Pred(i)} (finish[p] + Comm(p, i)))
14:         EFT_ik = EST_ik + (w_i / s_ik)
15:         // Step 3: Compute Optimal Young/Daly Checkpoint Gate & Risk Penalties
16:         tau_opt = sqrt(2 * T_ckpt / lambda_eff_k) if lambda_eff_k > 0 else infinity
17:         E_ckpt_cpu = floor(p_ik / tau_opt) * (T_ser + T_ver + T_ack)
18:         E_restart = (1 - exp(-lambda_k * p_ik)) * (min(p_ik, tau_opt)/2 + Comm_delta + T_restore)
19:         Score = EFT_ik + Crit_i * (delta * E_ckpt_cpu + eta * E_restart + rho * T_attest)
20:         If Score < min_score then
21:             min_score = Score, best_worker = k
22:         End If
23:     End For
24:     Assign task i -> best_worker
25:     Update finish[i] = EFT(i, best_worker) and avail[best_worker] = finish[i]
26: End While
27: Return Allocation
```

---

## V. Experimental Setup & Methodology

### A. Experimental Matrix & Execution Harness
The evaluation is executed across 1,120 simulation runs:
- **Algorithms Evaluated:** Proposed Risk-Aware (GhostInTheMachine), HEFT [1], Greedy EFT, Bounded ACO (20 ants, 25 iterations, MMAS bounds).
- **Hourly Churn Rates ($\lambda$):** 7 levels: $0.00$ (static), $0.05$, $0.10$, $0.15$, $0.20$, $0.25$, $0.30$ preemption events/hour.
- **Network Profiles:**
  - *Asymmetric Residential:* Downlink $80\text{--}150$ Mbps, Uplink $8\text{--}12$ Mbps (mean $10$ Mbps).
  - *Symmetric Enterprise:* Downlink $80\text{--}150$ Mbps, Uplink $80\text{--}120$ Mbps (mean $100$ Mbps).
- **Workload Topology:** Synthetic DAGs comprising 20 tasks generated with compute demand $w_i \in [10, 25]$s, state sizes $q_i \in [25, 45]$ MB, and delta ratio $\Delta q_i / q_i = 0.20$, consistent with standard Pegasus scientific workflow profiles (Montage and CyberShake).
- **Seeds:** 20 deterministic random seeds (`[42, 101, 2024, 777, 999, 123, 456, 789, 1001, 1337, 2025, 3141, 2718, 5555, 8888, 9001, 4040, 7070, 5050, 9999]`).

### B. Statistical Rigor & Metric Definitions
1. **Workflow Makespan (seconds):** Total wall-clock time from DAG release to final task completion.
2. **SLA Deadline Miss Rate (%):** Fraction of runs exceeding SLA deadline $D_{\text{SLA}} = 1.20 \times \text{CriticalPath}$.
3. **Goodput-to-Overhead Ratio (GOR):**
$$\text{GOR} = \frac{T_{\text{useful}}}{T_{\text{useful}} + T_{\text{ser}} + T_{\text{net}} + T_{\text{ver}} + T_{\text{tax}} + T_{\text{lost}}}$$
4. **State Recovery Latency (seconds):** Time elapsed from host crash detection to resumption on a replacement node.
5. **Statistical Significance:** All metrics report sample means, standard deviations, 95% Confidence Intervals ($\text{CI}_{95} = 1.96 \cdot \text{SEM}$), and two-tailed Welch’s t-tests.

---

## VI. Results & Empirical Analysis

### A. Primary Breakthrough: State Recovery Latency under Asymmetric Uplinks
The central empirical breakthrough of GhostInTheMachine is illustrated in Fig. 2. Under asymmetric residential links ($U_k \approx 10$ Mbps), baseline systems attempting full state snapshot transfers suffer recovery latencies scaling to **62.32s ± 6.57s** for HEFT (95% CI: [55.75, 68.89]), **64.02s ± 4.95s** for Greedy-EFT (95% CI: [59.07, 68.98]), and **76.71s ± 7.62s** for Bounded-ACO (95% CI: [69.09, 84.33]). In contrast, GhostInTheMachine’s incremental state deltas ($\Delta q_i \approx 8$ MB) restored from durable peer stores reduce recovery latency to **1.28s ± 0.05s** (asymmetric, 95% CI: [1.22, 1.33]) and **1.12s ± 0.07s** (symmetric, 95% CI: [1.05, 1.19]), representing a **98.0% (49x) reduction** in failover delay ($t = -18.22, p < 0.0001$). This completely eliminates the residential upload choking that cripples legacy systems upon host preemption.

```
TABLE I: Failure Recovery Latency vs. State Payload Size Across Network Profiles (N=239 Preemption Events)
+--------------------+-----------------------+----------------+-----------------------+---------------------+
| Algorithm          | Payload Mode          | Uplink Profile | Mean Recovery Latency | 95% Confidence Int. |
+--------------------+-----------------------+----------------+-----------------------+---------------------+
| Proposed-RiskAware | 8.00 MB (Delta)       | 100 Mbps Sym   | 1.12 s                | [1.05, 1.19]        |
| Proposed-RiskAware | 8.00 MB (Delta)       | 10 Mbps Asym   | 1.28 s                | [1.22, 1.33]        |
| HEFT Baseline      | 40.00 MB (Full)       | 100 Mbps Sym   | 4.82 s                | [4.21, 5.43]        |
| HEFT Baseline      | 40.00 MB (Full)       | 10 Mbps Asym   | 62.32 s               | [55.75, 68.89]      |
| Greedy-EFT         | 40.00 MB (Full)       | 10 Mbps Asym   | 64.02 s               | [59.07, 68.98]      |
| Bounded-ACO        | 40.00 MB (Full)       | 10 Mbps Asym   | 76.71 s               | [69.09, 84.33]      |
+--------------------+-----------------------+----------------+-----------------------+---------------------+
```

### B. Statistical Makespan Comparison: Low Churn vs. High Churn
Table II details makespan, GOR, and deadline compliance across all four scheduling algorithms under asymmetric 10 Mbps residential links across 0.00, 0.15, and 0.30 hourly churn rates.

```
TABLE II: Statistical Performance Under Asymmetric Residential Uplinks (Uk = 10 Mbps, N=20 Seeds)
+------------+--------------------+-------------------+---------------+---------------+---------------------+
| Churn Rate | Algorithm          | Makespan Mean (s) | 95% CI (s)    | Mean GOR (%)  | Deadline Miss Rate  |
+------------+--------------------+-------------------+---------------+---------------+---------------------+
| 0.00 / hr  | Proposed-RiskAware | 137.59            | [126.0, 149.2]| 99.59%        | 0.0%                |
| 0.00 / hr  | HEFT Baseline      | 137.59            | [126.0, 149.2]| 99.59%        | 0.0%                |
| 0.00 / hr  | Greedy-EFT         | 131.93            | [123.3, 140.5]| 99.60%        | 0.0%                |
| 0.00 / hr  | Bounded-ACO        | 132.22            | [125.7, 138.7]| 99.56%        | 0.0%                |
+------------+--------------------+-------------------+---------------+---------------+---------------------+
| 0.15 / hr  | Proposed-RiskAware | 138.02            | [126.1, 149.9]| 97.10%        | 0.0%                |
| 0.15 / hr  | Bounded-ACO        | 148.97            | [135.3, 162.6]| 92.43%        | 0.0%                |
| 0.15 / hr  | HEFT Baseline      | 149.53            | [137.0, 162.1]| 92.17%        | 0.0%                |
| 0.15 / hr  | Greedy-EFT         | 153.18            | [141.2, 165.1]| 89.58%        | 0.0%                |
+------------+--------------------+-------------------+---------------+---------------+---------------------+
| 0.30 / hr  | Proposed-RiskAware | 139.65            | [127.0, 152.3]| 96.79%        | 0.0%                |
| 0.30 / hr  | Greedy-EFT         | 183.61            | [159.4, 207.8]| 79.10%        | 20.0%               |
| 0.30 / hr  | HEFT Baseline      | 187.26            | [151.7, 222.8]| 81.46%        | 20.0%               |
| 0.30 / hr  | Bounded-ACO        | 195.93            | [163.5, 228.3]| 79.69%        | 25.0%               |
+------------+--------------------+-------------------+---------------+---------------+---------------------+
```

Under quiescent conditions (0.00/hr churn), Proposed-RiskAware matches HEFT identically at 137.6s makespan and 99.59% GOR because adaptive risk gating deactivates checkpoints. Under 0.15/hr churn, Proposed-RiskAware completes in 138.0s, outperforming HEFT (149.5s), Greedy-EFT (153.2s), and Bounded-ACO (149.0s). Under severe 0.30/hr churn, Proposed-RiskAware maintains 139.7s makespan, significantly outperforming HEFT (187.3s, $p = 0.0134$), Greedy-EFT (183.6s, $p = 0.0016$), and Bounded-ACO (195.9s, $p = 0.0015$).

### C. SLA Deadline Miss Rate Under Churn
Fig. 3 demonstrates the impact of preemption churn on SLA deadline compliance ($D_{\text{SLA}} = 1.20 \times \text{CriticalPath}$).
- Under quiescent conditions (0% churn) through 15% churn, all algorithms maintain a **0.0%** deadline miss rate.
- As churn rises to 20%–30%, legacy baselines suffer cascading deadline breaches: at 0.30 churn, HEFT suffers a **20.0%** deadline miss rate, Greedy-EFT suffers a **20.0%** deadline miss rate, and Bounded-ACO suffers a **25.0%** deadline miss rate.
- In contrast, Proposed-RiskAware bounds deadline violations strictly to **0.0%** across all 1,120 runs by dynamically prioritizing critical-path slack and routing incremental state recovery through high-throughput replica peers.

### D. Goodput-to-Overhead Ratio (GOR) Breakdown
Fig. 4 presents the normalized compute decomposition, while Fig. 5 traces Goodput-to-Overhead Ratio across churn rates in a dual-panel layout (Panel (a) Asymmetric Residential $U_k \approx 10$ Mbps vs. Panel (b) Symmetric Enterprise $U_k \approx 100$ Mbps):
- Under quiescent conditions (0% churn), adaptive risk gating achieves **99.59%** GOR, matching HEFT exactly.
- Under asymmetric residential links with churn, Proposed-RiskAware sustains **97.10%** GOR (at 0.15 churn) and **96.79%** GOR (at 0.30 churn). In contrast, uncheckpointed baselines suffer severe degradation due to repeated lost recomputation ($T_{\text{lost}}$) and post-preemption residential upload recovery stalls ($T_{\text{recovery\_stall}}$): HEFT drops to **81.46%** (at 0.30 churn), Bounded-ACO drops to **79.69%**, and Greedy-EFT plunges to **79.10%**.
- Under symmetric 100 Mbps bandwidth, high link capacities allow rapid state and payload transfers, with all algorithms maintaining $\ge 91\%$ GOR.

### E. Large-Scale DAG Scalability ($|V| \in [20, 150]$ Tasks)
To evaluate scheduler scalability across large workflows ($|V| \ge 100$), we conducted an empirical sweep across 20, 50, 100, and 150 tasks (Table V).

```
TABLE V: Large-Scale DAG Scheduling Scalability Summary across |V| in [20, 150]
+-------------+--------------------+-----------------------+--------------------+
| Tasks (|V|) | Algorithm          | Mean Scheduling Time  | Mean Makespan (s)  |
+-------------+--------------------+-----------------------+--------------------+
| 20          | Proposed-RiskAware | 0.33 ms               | 134.19 s           |
| 20          | HEFT               | 0.15 ms               | 134.25 s           |
| 20          | Bounded-ACO        | 94.30 ms              | 122.41 s           |
| 20          | Greedy-EFT         | 0.13 ms               | 123.57 s           |
+-------------+--------------------+-----------------------+--------------------+
| 50          | Proposed-RiskAware | 0.72 ms               | 290.33 s           |
| 50          | HEFT               | 0.33 ms               | 301.53 s           |
| 50          | Bounded-ACO        | 239.05 ms             | 340.93 s           |
| 50          | Greedy-EFT         | 0.32 ms               | 265.91 s           |
+-------------+--------------------+-----------------------+--------------------+
| 100         | Proposed-RiskAware | 2.86 ms               | 566.23 s           |
| 100         | HEFT               | 1.36 ms               | 581.20 s           |
| 100         | Bounded-ACO        | 875.16 ms             | 823.79 s           |
| 100         | Greedy-EFT         | 1.22 ms               | 543.38 s           |
+-------------+--------------------+-----------------------+--------------------+
| 150         | Proposed-RiskAware | 4.44 ms               | 847.13 s           |
| 150         | HEFT               | 2.04 ms               | 897.22 s           |
| 150         | Bounded-ACO        | 1353.70 ms            | 1301.86 s          |
| 150         | Greedy-EFT         | 1.90 ms               | 856.74 s           |
+-------------+--------------------+-----------------------+--------------------+
```

As Table V demonstrates, at $|V| \ge 100$, Bounded-ACO suffers combinatorial search space explosion: its scheduling overhead surges to 1,353.7 ms and its makespan degrades by +53.7% (1,301.86s vs. 847.13s for Proposed-RiskAware). In contrast, GhostInTheMachine schedules 150-task graphs in just **4.44 ms**, delivering the shortest makespan (847.13s vs. 897.22s for HEFT).

---

## VII. Architectural Ablation Study & Empirical System Calibrations

### A. Architectural Component Ablation Analysis
To rigorously quantify the individual contribution of each runtime mechanism, we conducted targeted ablation benchmarks:
1. **Adaptive Young/Daly Risk-Gating vs. Static Checkpointing:** Under quiescent zero churn ($\lambda = 0.00$), static unconditional checkpointing incurs serialization and hashing overhead on every task, depressing GOR to 87.6%. GhostInTheMachine's cost-benefit risk gate dynamically scales checkpoint frequency with worker hazard rate $\lambda_{\text{eff}}$, fully deactivating commits at zero churn to achieve exact parity with HEFT (99.59% GOR and 137.6s makespan).
2. **Decoupled Asynchronous State-Delta Commit vs. Synchronous Blocking:** Evaluating the concurrency overlap protocol demonstrates that streaming delta checkpoints asynchronously across the 10 Mbps uplink prevents worker CPU blocking. Synchronous blocking replication would impose an additional 7.2s stall per commit, dropping net goodput to 56%. Restricting synchronous stalls strictly to memory serialization ($T_{\text{ser}} \approx 0.02$s) and SHA-256 verification ($T_{\text{ver}} \approx 0.015$s) preserves 96.79% to 97.10% sustained goodput.
3. **Critical-Path Slack Weighting:** Modulating the objective score by upward rank ($\text{Crit}(i) = 1.0 + 1.5 \cdot \text{rank}_u(i) / \max(\text{rank}_u)$) directs critical-path tasks to the most reliable worker nodes, successfully bounding deadline miss rates to 0.0% under 30% worker churn where baselines suffer 20.0%–25.0% deadline violations.

### B. Physical Hardware Microbenchmarks vs. Simulation Parameters
To verify that discrete-event simulation assumptions do not underestimate physical overheads, we executed physical microbenchmarks on an Intel Core i7 testbed. Table III presents the empirical calibration data generated by `verify_simulation_anchor.py`.

```
TABLE III: Physical Hardware Microbenchmarks vs. Simulation Parameters
+-----------------------------------+--------------------+--------------------+----------------------+
| Architectural Mechanism           | Assumed in Sim     | Physically Measured| Conservative Margin  |
+-----------------------------------+--------------------+--------------------+----------------------+
| State Serialization Throughput    | 120.0 MB/s         | 4,932.4 MB/s       | 41.1x Conservative   |
| State Deserialization / Restore   | 144.0 MB/s         | 5,269.2 MB/s       | 36.6x Conservative   |
| SHA-256 Attestation Hashing       | 350.0 MB/s         | 1,862.8 MB/s       | 5.3x Conservative    |
| 10 Mbps Rate-Limited Stream (4MB) | 3.200 s            | 3.356 s            | 1.05x Physical Match |
| 100 Mbps Rate-Limited Stream (4MB)| 0.320 s            | 0.336 s            | 1.05x Physical Match |
+-----------------------------------+--------------------+--------------------+----------------------+
```

The measured physical serialization rate exceeds 4,900 MB/s, and SHA-256 integrity verification exceeds 1,800 MB/s. By assuming 120 MB/s and 350 MB/s, respectively, our simulation imposes a 5x–40x higher computational tax than real physical hardware, proving that our goodput and overhead findings represent conservative lower bounds. Furthermore, physical Wi-Fi emulation using the Gilbert-Elliott burst loss model reveals a 1.53% packet loss rate and gateway bufferbloat (+131.4 ms RTT inflation), causing a 12.46% goodput degradation that further confirms the necessity of minimizing state footprint on residential links.

### C. Multi-Metric Pairwise Welch's t-Test Hypothesis Testing
Table IV reports pairwise Welch's t-test evaluations across Failure Recovery Latency, Goodput-to-Overhead Ratio, and Workflow Makespan under asymmetric residential links (10 Mbps). Under quiescent conditions, makespan differences are statistically indistinguishable ($p = 0.43$ to $1.00$). Under moderate churn (0.15/hr), Proposed-RiskAware demonstrates a statistically significant GOR advantage over Greedy-EFT ($t = 2.34, p = 0.0194$). Under severe churn (0.30/hr), Proposed-RiskAware demonstrates statistically significant advantages across all three baselines for both Workflow Makespan ($p = 0.0015$ to $0.0134$) and Goodput-to-Overhead Ratio ($p \le 0.0012$). Crucially, across all preemption events, state-delta recovery latency achieves overwhelming statistical significance against all baselines ($p < 0.0001, t < -18.2$), providing empirical proof of the 98.0% recovery latency reduction.

```
TABLE IV: Multi-Metric Pairwise Welch's t-Test Hypothesis Testing (Proposed-RiskAware vs. Baselines, Uk = 10 Mbps)
+------------------+-----------+-------------+----------+----------+--------+---------+--------------------+
| Metric           | Condition | Baseline    | Prop     | Base     | t-stat | p-value | Sig (p<0.05)       |
+------------------+-----------+-------------+----------+----------+--------+---------+--------------------+
| Recovery Latency | All Churn | HEFT        | 1.28 s   | 62.32 s  | -18.22 | <0.0001 | YES (p < 0.0001)   |
| Recovery Latency | All Churn | Greedy-EFT  | 1.28 s   | 64.02 s  | -24.83 | <0.0001 | YES (p < 0.0001)   |
| Recovery Latency | All Churn | Bounded-ACO | 1.28 s   | 76.71 s  | -19.41 | <0.0001 | YES (p < 0.0001)   |
| GOR (%)          | 0.15 / hr | HEFT        | 97.10%   | 92.17%   |  1.58  | 0.1147  | NO                 |
| GOR (%)          | 0.15 / hr | Greedy-EFT  | 97.10%   | 89.58%   |  2.34  | 0.0194  | YES (p = 0.0194)   |
| GOR (%)          | 0.15 / hr | Bounded-ACO | 97.10%   | 92.44%   |  1.60  | 0.1090  | NO                 |
| GOR (%)          | 0.30 / hr | HEFT        | 96.79%   | 81.46%   |  3.24  | 0.0012  | YES (p = 0.0012)   |
| GOR (%)          | 0.30 / hr | Greedy-EFT  | 96.79%   | 79.10%   |  4.30  | <0.0001 | YES (p < 0.0001)   |
| GOR (%)          | 0.30 / hr | Bounded-ACO | 96.79%   | 79.69%   |  3.70  | 0.0002  | YES (p = 0.0002)   |
| Makespan (s)     | 0.00 / hr | HEFT        | 137.59 s | 137.59 s |  0.00  | 1.0000  | NO (Parity)        |
| Makespan (s)     | 0.00 / hr | Greedy-EFT  | 137.59 s | 131.93 s |  0.77  | 0.4425  | NO (Parity)        |
| Makespan (s)     | 0.00 / hr | Bounded-ACO | 137.59 s | 132.22 s |  0.79  | 0.4288  | NO (Parity)        |
| Makespan (s)     | 0.15 / hr | HEFT        | 138.02 s | 149.53 s | -1.31  | 0.1919  | NO                 |
| Makespan (s)     | 0.15 / hr | Greedy-EFT  | 138.02 s | 153.18 s | -1.76  | 0.0781  | NO                 |
| Makespan (s)     | 0.15 / hr | Bounded-ACO | 138.02 s | 148.97 s | -1.18  | 0.2361  | NO                 |
| Makespan (s)     | 0.30 / hr | HEFT        | 139.65 s | 187.26 s | -2.47  | 0.0134  | YES (p = 0.0134)   |
| Makespan (s)     | 0.30 / hr | Greedy-EFT  | 139.65 s | 183.61 s | -3.16  | 0.0016  | YES (p = 0.0016)   |
| Makespan (s)     | 0.30 / hr | Bounded-ACO | 139.65 s | 195.93 s | -3.17  | 0.0015  | YES (p = 0.0015)   |
+------------------+-----------+-------------+----------+----------+--------+---------+--------------------+
```

---

## VIII. Conclusion
Executing dependent workflow DAGs across consumer volunteer hardware requires confronting the physical reality of residential network asymmetry. Conventional scheduling heuristics that prioritize raw makespan fail when host disconnections force multi-gigabyte state re-transfers over 10 Mbps uplinks. GhostInTheMachine resolves this vulnerability through upload-aware risk placement and asynchronous state-delta checkpointing. Empirical evaluation across 1,120 runs confirms that while makespan remains statistically tied under quiescent conditions ($p \ge 0.42$), state-delta recovery achieves a 98.0% (49x) reduction in failover latency (1.28s vs. 62.32s, $p < 0.0001$), bounds deadline violations strictly to 0.0% under heavy churn, and insulates workflow deadlines against catastrophic preemption cascades with statistically significant makespan ($p = 0.0015$ to $0.0134$) and GOR ($p \le 0.0012$) superiority.

---

## References
[1] H. Topcuoglu, S. Hariri, and M.-Y. Wu, "Performance-effective and low-complexity task scheduling for heterogeneous computing," *IEEE Transactions on Parallel and Distributed Systems*, vol. 13, no. 3, pp. 260–274, Mar. 2002.  
[2] K. Li, X. Tang, and K. Li, "Energy-efficient stochastic task scheduling on heterogeneous computing systems," *IEEE Transactions on Parallel and Distributed Systems*, vol. 25, no. 11, pp. 2867–2876, Nov. 2014.  
[3] D. P. Anderson and G. Fedak, "The computational and storage potential of volunteer computing," in *Proc. 6th IEEE/ACM International Symposium on Cluster Computing and the Grid (CCGrid)*, 2006, pp. 73–80.  
[4] A. Benoit, A. Cavelan, Y. Robert, and H. Sun, "Checkpointing workflows à la Young/Daly is not good enough," *ACM Transactions on Parallel Computing*, vol. 9, no. 1, pp. 1–34, Mar. 2022.  
[5] C. Clark, K. Fraser, S. Hand, J. G. Hansen, E. Jul, C. Limpach, I. Pratt, and A. Warfield, "Live migration of virtual machines," in *Proc. 2nd USENIX Symposium on Networked Systems Design & Implementation (NSDI)*, 2005, pp. 273–286.  
[6] H. Birkholz, D. Thaler, M. Richardson, N. Smith, and W. Pan, "Remote ATtestation procedureS (RATS) Architecture," *IETF RFC 9334*, May 2023.  
[7] J. W. Young, "A first order approximation to the optimum checkpoint interval," *Communications of the ACM*, vol. 17, no. 9, pp. 530–531, Sep. 1974.  
[8] J. T. Daly, "A higher order estimate of the optimum checkpoint interval for restart dumps," *Future Generation Computer Systems*, vol. 22, no. 3, pp. 303–312, Feb. 2006.  
[9] S. Bharathi, A. Chervenak, E. Deelman, G. Mehta, M.-H. Su, and K. Vahi, "Characterization of scientific workflows," in *Proc. 3rd Workshop on Workflows in Support of Large-Scale Science (WORKS)*, 2008, pp. 1–10.
