# GhostInTheMachine: Core Execution Engine & Telemetry Pipeline

**GhostInTheMachine** is an end-to-end benchmark runtime and discrete-event simulation engine for risk-aware Directed Acyclic Graph (DAG) scheduling across heterogeneous, intermittently available peer-to-peer (P2P) compute networks.

It empirically evaluates whether accounting for asymmetric upload bandwidth bottlenecks ($D_k \gg U_k$), incremental state-delta checkpointing, worker preemption churn (Poisson & Weibull hazard models), and remote attestation overhead can significantly reduce workflow deadline miss rates and improve Goodput-to-Overhead Ratios (GOR) relative to established baselines (**HEFT**, **Greedy EFT**, and **Bounded ACO**).

---

## 🏛 Architecture Overview

```
Workload DAG (w_i, m_i, d_ij, q_i)
            │
            ▼
┌───────────────────────────────────────┐
│ Feasibility Gate F(i,k)               │ ──> Rejects infeasible/unattested workers
└───────────────────────────────────────┘
            │
            ▼
┌───────────────────────────────────────┐
│ Risk-Aware Scheduler                  │ ──> Minimizes J(i,k) = E[p_ik] + γE[xfer]
│ (GhostInTheMachine)                   │       + δE[ckpt] + ηE[restart_loss] + ρE[ver]
└───────────────────────────────────────┘
            │
            ▼
┌───────────────────────────────────────┐
│ Discrete-Event Simulation & Faults    │ ──> Asymmetric residential links (10 Mbps upload)
│                                       │ ──> Preemption churn (Weibull / Exponential)
└───────────────────────────────────────┘
            │
            ▼
┌───────────────────────────────────────┐
│ Telemetry & Provenance Logger         │ ──> Makespan, SLA Miss %, GOR, Attestation Tax
└───────────────────────────────────────┘
```

---

## 🚀 Quickstart

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Run Single Schedule & Simulation
```bash
python cli.py schedule --tasks 15 --algorithm proposed --churn 0.15 --profile asymmetric
```

### 3. Run Comprehensive Experiment Matrix & Generate Publication Figures
Run the complete evaluation scenario across seeds and churn configurations:
```bash
# On Linux/macOS
bash run_experiments.sh

# On Windows PowerShell
.\run_experiments.ps1
```

Or via Python directly:
```bash
python run_experiments.py --tasks 20
```

---

## 📊 Generated Artifacts & Figures

All figures are automatically compiled from experimental CSV telemetry logs (`telemetry_logs/telemetry_summary.csv` and `telemetry_logs/telemetry_events.csv`) and output to the `figures/` directory as publication-ready vector assets (PDF) and 300-DPI images (PNG):

1. **`system_architecture.pdf` / `.png`**: Structured layout diagram illustrating the scheduling and recovery pipeline.
2. **`figure1_deadline_miss_rate.pdf` / `.png`**: Workflow deadline miss rate vs. hourly worker churn rate (0% to 30%) with 95% confidence intervals.
3. **`figure2_recovery_vs_delta.pdf` / `.png`**: Recovery latency vs. checkpoint delta size under asymmetric upload links (10 Mbps vs. 100 Mbps).
4. **`figure3_goodput_overhead_breakdown.pdf` / `.png`**: Stacked bar chart showing total execution time breakdown (Useful Compute, State Serialization, Network Migration, Verification Tax, and Wasted Recompute).

---

## 📂 Project Structure

```
GhostInTheMachine/
├── dag_engine.py               # Workflow DAG generator, task representation, upward ranks
├── worker.py                   # Heterogeneous worker models, asymmetric links, churn params
├── checkpoint.py               # Checkpoint & state delta API (checkpoint(), restore())
├── risk_engine.py              # Feasibility gate F(i,k) and objective score J(i,k)
├── schedulers.py               # Proposed policy, HEFT, Greedy-EFT, Bounded ACO, Exact Solver
├── network_fault_injector.py   # Discrete-event engine, asymmetric link simulator, churn injector
├── experiment_logger.py        # Telemetry logger (Makespan, GOR, CSV/JSON MLflow provenance)
├── generate_paper_artifacts.py # Automated publication-ready figure generator
├── run_experiments.py          # Matrix experiment harness across seeds and churn rates
├── run_experiments.sh          # Bash runner
├── run_experiments.ps1         # PowerShell runner
├── cli.py                      # Interactive CLI tool
├── requirements.txt            # Python dependencies
├── telemetry_logs/             # Output CSV and JSON telemetry datasets
└── figures/                    # Generated publication vector assets (PDF/PNG)
```
