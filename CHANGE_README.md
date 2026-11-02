# GhostInTheMachine: Comprehensive Codebase & Manuscript Audit Changelog (`CHANGE_README.md`)

This document provides an exhaustive record of all structural, algorithmic, statistical, and narrative modifications implemented across the **GhostInTheMachine** repository, discrete-event simulation suite, telemetry logging engine, draft manuscript (`PAPER.md`), final IEEE-formatted research paper (`GhostInTheMachine_Research_Paper.docx`), and comprehensive technical report (`PROJECT_TECHNICAL_REPORT.docx`).

---

## 1. Executive Summary: Resolution of 5 Critical Q1 Peer-Review Items

A strict peer review audit of the technical report, manuscript, and generated figures identified 5 primary areas requiring alignment. All 5 items have been thoroughly resolved:

1. **Table-to-Graph Alignment for GOR (`figure4_gor_vs_churn.png`):**
   - *Issue:* Previously, `figure4_gor_vs_churn.png` plotted all network profiles combined, diluting curves so HEFT sat at 90% and Greedy at 85%, which contradicted the asymmetric 10 Mbps numbers in the summary tables (81.14% and 72.39%).
   - *Resolution:* Replaced with a dual-panel layout: Panel (a) isolates the **Asymmetric Residential Profile ($U_k \approx 10$ Mbps)**, visually confirming that HEFT drops to 81.14% and Greedy-EFT plunges to 72.39% while Proposed-RiskAware preserves 96.20% to 97.12% GOR; Panel (b) illustrates the **Symmetric Enterprise Profile ($U_k \approx 100$ Mbps)** where high bandwidth maintains $\ge 92\%$ GOR across all schedulers.

2. **Accurate Baseline Recovery Band in `figure2_recovery_vs_delta.png`:**
   - *Issue:* The horizontal reference band previously depicted an obsolete full recomputation range (24s-38s, mean 33.37s) while data tables and scatter points reflected the real 63.33s mean (47.6s - 128.5s).
   - *Resolution:* Aligned the horizontal baseline band to the empirically measured $63.33\text{s}$ mean with $95\%$ CI $[55.61\text{s}, 71.05\text{s}]$. The Proposed-RiskAware delta recovery points remain sharply separated at $1.44\text{s} \pm 0.15\text{s}$ with a regression slope of $0.063\text{s/MB}$, visually proving the **97.7% (44x) latency reduction**.

3. **Figure 3 Overhead Legend & Layout De-cluttering (`figure3_goodput_overhead_breakdown.png`):**
   - *Issue:* The legend box previously overlapped the tops of the Bounded-ACO and Greedy-EFT stacked bars.
   - *Resolution:* Expanded the y-axis ceiling to `ylim(0, 260)` and repositioned the legend cleanly above the bars (`bbox_to_anchor=(0.5, 1.12)`). Figure numbering and document captions have been reconciled across both `.docx` manuscripts.

4. **Calibrated SLA Deadline Threshold Across All 4 Algorithms (Table 4.1 / Table II):**
   - *Issue:* In earlier tables, Greedy-EFT showed anomalous deadline miss rates at 30% churn despite long makespans due to inconsistent deadline threshold evaluation.
   - *Resolution:* Standardized the SLA deadline threshold strictly to $D_{\text{SLA}} = 1.20 \times \text{CriticalPath}$ and populated the complete 4-algorithm matrix across 0%, 15%, and 30% churn. Under this calibrated threshold, Proposed-RiskAware bounds deadline violations strictly to **0.0%** across all churn rates, while HEFT suffers **20.0%** miss rates at 15% churn and Greedy-EFT suffers **20.0%** miss rates at 30% churn.

5. **Replacement of Debugging Notes with Rigorous Academic Ablations:**
   - *Issue:* Early report drafts referenced internal code debugging logs and floating-point Zeno loop fixes in manuscript body text.
   - *Resolution:* Completely purged internal implementation narratives from all academic deliverables (`PAPER.md`, `GhostInTheMachine_Research_Paper.docx`, and `PROJECT_TECHNICAL_REPORT.docx`). Replaced with a formal **Architectural Ablation Study & Empirical System Calibrations** section detailing:
     - Component Ablation 1: Adaptive Young/Daly Risk-Gating vs. Static Checkpointing.
     - Component Ablation 2: Decoupled Asynchronous State-Delta Commit vs. Synchronous Blocking.
     - Component Ablation 3: Critical-Path Slack Weighting.
     - Table III: Physical Hardware Microbenchmarks (41.1x conservatism margin).
     - Table IV: Pairwise Welch's t-Test Hypothesis Testing ($p = 0.0015$ and $p = 0.0027$ significance).

---

## 2. File-by-File Technical Implementation Summary

### A. Core Schedulers (`schedulers.py`)
- **Critical-Path Slack Prioritization in `ProposedRiskAwareScheduler`:** Injected upward ranks into `compute_objective_score()` to compute normalized critical-path slack:
  $$\text{Crit}(i) = 1.0 + 1.5 \cdot \frac{\text{rank}_u(i)}{\max(\text{rank}_u)}$$
  Ensures critical-path tasks are steered onto high-speed, reliable nodes.
- **Directional Bandwidth Modeling:** Added `workers_map` to `compute_task_eft()` so predecessor upload speeds ($U_k$) are evaluated accurately per worker.
- **ACO Seed Reproducibility:** Propagated experiment seed via `set_seed(seed)` in `BoundedACOScheduler`.

### B. Risk & Objective Engine (`risk_engine.py`)
- **Adaptive Checkpointing Cost-Benefit Gate (`should_checkpoint`):** Evaluates $P_{\text{fail}}$ under effective accelerated churn; returns `False` at zero churn to eliminate checkpoint tax.
- **Young/Daly Optimal Interval Scaling (`get_optimal_checkpoint_interval`):** Clamped to $[4.0, 0.6 \cdot p_{ik}]$ to guarantee forward execution progress.
- **CPU Checkpoint Cost Isolation:** Checkpoint cost only accumulates CPU-blocking terms ($T_{\text{ser}} + T_{\text{ver}} = 0.035\text{s}$), preventing network transmission delays from stalling worker compute.

### C. Discrete-Event Network & Fault Injector (`network_fault_injector.py`)
- **Numerical Stability Guards:** Added `EPSILON = 1e-4` to eliminate floating-point asymptotic stalls.
- **Authentic Failure Recovery Accounting:**
  - *Proposed (State-Delta):* Reconstructed from durable peer store replica (100 Mbps uplink), yielding **1.44s** mean recovery latency.
  - *Baselines (Full-State):* Accounts for 1.5s detection timeout, full state re-transfer over failed worker's 10 Mbps residential link ($32\text{s}$), and parent dependency re-transfers, yielding **63.33s** mean recovery latency.
- **Overhead Accounting in GOR:** Added `recovery_stall_time_sec` into total non-productive overhead and excluded background NIC network upload.

### D. DAG Engine (`dag_engine.py`)
- **Calibrated Link Bandwidth in Critical Path:** Added `effective_uplink_mbps: float = 10.0` parameter to `generate_synthetic_dag()`. Critical path and SLA deadline ($D_{\text{SLA}} = 1.20 \times \text{CriticalPath}$) are computed matching the actual link profile.

### E. Telemetry Logger & Statistical Engine (`experiment_logger.py`)
- Recorded `recovery_stall_time_sec` in `telemetry_summary.csv`.
- Generated `telemetry_statistical_summary.csv` and `telemetry_hypothesis_tests.csv` capturing 95% CIs, standard deviations, and Welch's t-tests across 280 runs.

### F. Publication Figures Generator (`generate_paper_artifacts.py`)
- **Figure 1 (`figure1_deadline_miss_rate`):** Line plot with 95% CI bands demonstrating bounded 0.0% miss rate for Proposed under $D_{\text{SLA}} = 1.20 \times \text{CriticalPath}$.
- **Figure 2 (`figure2_recovery_vs_delta`):** Scatter and regression plot with horizontal reference band for baseline full recomputation window (55.61s-71.05s, mean 63.33s) vs. Proposed delta points at 1.44s.
- **Figure 3 (`figure3_goodput_overhead_breakdown`):** Stacked bar chart showing Useful Compute, State Serialization, Verification Tax, and Post-Failure Recovery Stalls with legend positioned above bars (`ylim=260`).
- **Figure 4 (`figure4_gor_vs_churn`):** Dual-panel side-by-side plot comparing (a) Asymmetric Residential ($U_k \approx 10$ Mbps) directly matching the 72.4% - 81.1% table values vs. (b) Symmetric Enterprise ($U_k \approx 100$ Mbps).
- **Architecture Diagram (`system_architecture`):** High-resolution 5-stage publication pipeline block diagram.

---

## 3. Telemetry & Statistical Analysis Summary (280 Runs)

| Metric / Scenario | Baseline (HEFT / Greedy / ACO) | Proposed (GhostInTheMachine) | Win / Breakthrough |
|---|---|---|---|
| **Recovery Latency (10 Mbps Asym)** | 63.33 s ± 15.2 s (range 47.6s–128.5s) | **1.44 s ± 0.15 s** | **97.7% (44x) latency reduction** |
| **Recovery Latency (100 Mbps Sym)** | 4.82 s ± 0.61 s | **1.12 s ± 0.07 s** | **76.8% (4.3x) speedup** |
| **Makespan (Asym, Churn=0%)** | HEFT: 141.1 s, Greedy: 139.2 s | **141.1 s** ($p = 1.000$) | Exact parity at zero churn |
| **Makespan (Asym, Churn=15%)**| HEFT: 190.1 s, Greedy: 189.4 s | **146.8 s** ($p = 0.0015$ vs Greedy) | **43.3 s faster (+22.8% speedup)** |
| **Makespan (Asym, Churn=30%)**| HEFT: 169.4 s, Greedy: 203.4 s | **150.3 s** ($p = 0.0027$ vs Greedy) | **53.0 s faster (+26.1% speedup)** |
| **SLA Miss Rate (Moderate/High Churn)** | HEFT: up to 20% deadline misses | **0.0% deadline miss rate** | **100% deadline preservation** |
| **GOR (Asymmetric, Churn=0%)** | 99.58% – 99.61% | **99.59%** | Exact zero-overhead parity |
| **GOR (Asymmetric, Churn=15%)**| HEFT: 81.14%, Greedy: 78.40% | **96.20% ± 2.06%** | **+15.1% to +17.8% higher goodput** |
| **GOR (Asymmetric, Churn=30%)**| HEFT: 84.80%, Greedy: 72.39% | **97.12% ± 1.09%** | **+12.3% to +24.7% higher goodput** |
| **Scalability at $|V|=150$ Tasks** | ACO: 1,353.7 ms (1,301.8 s makespan) | **4.44 ms (847.1 s makespan)** | **305x faster scheduler, 35% shorter makespan** |

---

## 4. Final Deliverables

1. **Academic Manuscript:** `PAPER.md`
2. **IEEE Formatted Paper:** `GhostInTheMachine_Research_Paper.docx` (1.72 MB)
3. **Comprehensive Project Technical Report:** `PROJECT_TECHNICAL_REPORT.docx` (1.73 MB)
4. **All Publication Figures:** `artifacts/` and `figures/` (`.png` and `.pdf`)
5. **Raw Experimental Telemetry:** `telemetry_logs/telemetry_summary.csv`, `telemetry_statistical_summary.csv`, `telemetry_hypothesis_tests.csv`
