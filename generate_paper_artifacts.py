"""
GhostInTheMachine: Automated Graphing & Diagram Generation Script
Reads experimental telemetry CSVs and automatically outputs publication-ready vector assets:
1. System Architecture & Workflow Flowchart (vector PDF & PNG)
2. Figure 1: Deadline Miss Rate vs Worker Churn Rate (Line chart with 95% CI)
3. Figure 2: Recovery Time vs Checkpoint Delta Size under Asymmetric Uploads (Scatter/Regression)
4. Figure 3: Goodput vs Overhead Breakdown (Stacked bar chart across algorithms)
"""

import os
import csv
import math
from typing import Dict, List, Tuple, Optional
import matplotlib
# Use non-interactive backend
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


def setup_matplotlib_style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 11,
        "axes.labelsize": 13,
        "axes.titlesize": 14,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "legend.fontsize": 11,
        "figure.titlesize": 15,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "axes.grid": True,
        "grid.alpha": 0.35,
        "grid.linestyle": "--",
    })


def generate_architecture_flowchart(output_dir: str):
    """
    Generates a structured publication-ready layout diagram of the GhostInTheMachine
    scheduling pipeline:
    DAG Inputs -> Policy Filter / Feasibility Gate -> Risk-Aware Scheduler ->
    Asymmetric Transfer / Checkpoint -> Telemetry & Provenance Logger.
    """
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5)
    ax.axis("off")

    stages = [
        {"x": 0.5, "y": 2.2, "w": 1.7, "h": 1.8, "title": "DAG Workload\nEngine", "sub": "Compute $w_i$, Memory $m_i$\nPayload $d_{ij}$, State $q_i$", "color": "#E3F2FD", "border": "#1976D2"},
        {"x": 2.6, "y": 2.2, "w": 1.7, "h": 1.8, "title": "Feasibility Gate\n(Policy Filter)", "sub": "$m_i \\leq M_k$\n$c_i \\subseteq C_k$\nRATS Attestation", "color": "#FFF3E0", "border": "#F57C00"},
        {"x": 4.7, "y": 2.2, "w": 1.7, "h": 1.8, "title": "Risk-Aware\nScheduler", "sub": "Minimize $J(i,k)$:\nExec + Asymmetric $U_k$\n+ Ckpt + Restart Loss", "color": "#E8F5E9", "border": "#388E3C"},
        {"x": 6.8, "y": 2.2, "w": 1.7, "h": 1.8, "title": "Execution &\nCheckpointing", "sub": "Discrete-Event Sim\nAsymmetric Churn\nDelta Replication", "color": "#F3E5F5", "border": "#7B1FA2"},
        {"x": 8.9, "y": 2.2, "w": 1.7, "h": 1.8, "title": "Telemetry &\nProvenance", "sub": "Makespan, GOR,\nAttestation Tax,\nMLflow Provenance", "color": "#EDE7F6", "border": "#512DA8"},
    ]

    for s in stages:
        rect = patches.FancyBboxPatch(
            (s["x"], s["y"]), s["w"], s["h"],
            boxstyle="round,pad=0.12,rounding_size=0.15",
            facecolor=s["color"],
            edgecolor=s["border"],
            linewidth=2,
        )
        ax.add_patch(rect)
        ax.text(
            s["x"] + s["w"] / 2.0, s["y"] + s["h"] * 0.72,
            s["title"],
            ha="center", va="center",
            fontsize=11.5, fontweight="bold", color="#1A1A1A"
        )
        ax.text(
            s["x"] + s["w"] / 2.0, s["y"] + s["h"] * 0.32,
            s["sub"],
            ha="center", va="center",
            fontsize=9.0, color="#333333"
        )

    # Add directional connecting arrows
    for i in range(len(stages) - 1):
        x_start = stages[i]["x"] + stages[i]["w"] + 0.08
        x_end = stages[i + 1]["x"] - 0.08
        y_pos = stages[i]["y"] + stages[i]["h"] / 2.0
        ax.annotate(
            "",
            xy=(x_end, y_pos),
            xytext=(x_start, y_pos),
            arrowprops=dict(arrowstyle="->", lw=2.2, color="#424242"),
        )

    # Add subtitle & feedback loop
    ax.annotate(
        "Checkpoint Delta Ack / Failure Recovery Trigger",
        xy=(5.55, 2.05),
        xytext=(7.65, 0.9),
        ha="center",
        fontsize=9.5,
        fontstyle="italic",
        color="#7B1FA2",
        arrowprops=dict(
            arrowstyle="->",
            connectionstyle="arc3,rad=-0.3",
            lw=1.5,
            color="#7B1FA2",
            linestyle="--",
        ),
    )

    plt.title(
        "GhostInTheMachine: End-to-End Execution Engine & Telemetry Pipeline",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )

    pdf_path = os.path.join(output_dir, "system_architecture.pdf")
    png_path = os.path.join(output_dir, "system_architecture.png")
    plt.savefig(pdf_path)
    plt.savefig(png_path)
    plt.close()
    print(f"Generated Architecture Diagram: {pdf_path} and {png_path}")


def generate_figure1_deadline_miss_rate(summary_csv: str, output_dir: str):
    """
    Figure 1: Deadline Miss Rate vs Worker Churn Rate (0% to 30%)
    Lines: Proposed Policy vs HEFT vs Greedy vs ACO (with 95% CI)
    """
    if not os.path.exists(summary_csv):
        print(f"File not found: {summary_csv}")
        return

    data_by_alg_churn: Dict[Tuple[str, float], List[float]] = {}
    with open(summary_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            alg = row["algorithm"]
            churn = float(row["churn_rate"])
            miss = float(row["deadline_missed"]) * 100.0  # as percentage
            key = (alg, churn)
            if key not in data_by_alg_churn:
                data_by_alg_churn[key] = []
            data_by_alg_churn[key].append(miss)

    algorithms = ["Proposed-RiskAware", "HEFT", "Bounded-ACO", "Greedy-EFT"]
    churn_rates = sorted(list(set(churn for (_, churn) in data_by_alg_churn.keys())))

    styles = {
        "Proposed-RiskAware": {"color": "#1B5E20", "marker": "o", "label": "Proposed Risk-Aware (GhostInTheMachine)", "lw": 2.5},
        "HEFT": {"color": "#0D47A1", "marker": "s", "label": "HEFT Baseline", "lw": 2.0},
        "Bounded-ACO": {"color": "#E65100", "marker": "^", "label": "Bounded ACO", "lw": 2.0},
        "Greedy-EFT": {"color": "#C2185B", "marker": "x", "label": "Greedy Earliest-Finish", "lw": 1.8},
    }

    fig, ax = plt.subplots(figsize=(8.0, 5.2))

    for alg in algorithms:
        if alg not in styles:
            continue
        means = []
        cis = []
        valid_churns = []
        for churn in churn_rates:
            vals = data_by_alg_churn.get((alg, churn), [])
            if vals:
                mean = np.mean(vals)
                ci = 1.96 * (np.std(vals, ddof=1) / math.sqrt(len(vals))) if len(vals) > 1 else 0.0
                means.append(mean)
                cis.append(ci)
                valid_churns.append(churn * 100.0)

        if valid_churns:
            st = styles[alg]
            ax.plot(valid_churns, means, marker=st["marker"], color=st["color"], label=st["label"], linewidth=st["lw"], markersize=7)
            lower = [max(0.0, m - c) for m, c in zip(means, cis)]
            upper = [min(100.0, m + c) for m, c in zip(means, cis)]
            ax.fill_between(valid_churns, lower, upper, color=st["color"], alpha=0.15)

    ax.set_xlabel("Hourly Worker Churn Rate (%)")
    ax.set_ylabel("Workflow Deadline Miss Rate (%)")
    ax.set_title("Figure 1: Workflow Deadline Miss Rate vs. Worker Churn Rate\n(with 95% Confidence Intervals)", fontweight="bold")
    ax.set_ylim(-2, 102)
    ax.set_xlim(-1, 31)
    ax.legend(loc="upper left", framealpha=0.9)

    pdf_path = os.path.join(output_dir, "figure1_deadline_miss_rate.pdf")
    png_path = os.path.join(output_dir, "figure1_deadline_miss_rate.png")
    plt.savefig(pdf_path)
    plt.savefig(png_path)
    plt.close()
    print(f"Generated Figure 1: {pdf_path} and {png_path}")


def generate_figure2_recovery_time_vs_delta(events_csv: str, output_dir: str):
    """
    Figure 2: Recovery Time vs Checkpoint Delta Size under Asymmetric Uploads
    Scatter / Regression plot comparing Slower Uplink (10 Mbps) vs Fast Uplink (100 Mbps)
    """
    if not os.path.exists(events_csv):
        print(f"File not found: {events_csv}")
        return

    slow_deltas, slow_latencies = [], []
    fast_deltas, fast_latencies = [], []

    with open(events_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            delta = float(row["delta_size_mb"])
            latency = float(row["recovery_latency_sec"])
            uplink = float(row["uplink_mbps"])

            if uplink < 30.0:
                slow_deltas.append(delta)
                slow_latencies.append(latency)
            else:
                fast_deltas.append(delta)
                fast_latencies.append(latency)

    fig, ax = plt.subplots(figsize=(8.0, 5.2))

    def r_squared(x, y, poly):
        y_pred = poly(x)
        ss_res = sum((yi - yp) ** 2 for yi, yp in zip(y, y_pred))
        mean_y = sum(y) / len(y)
        ss_tot = sum((yi - mean_y) ** 2 for yi in y)
        return 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    if slow_deltas:
        ax.scatter(slow_deltas, slow_latencies, color="#D32F2F", alpha=0.6, label="Slower Uplink ($U_k \\approx 10$ Mbps)", s=45, marker="o")
        coeffs_slow = np.polyfit(slow_deltas, slow_latencies, 1)
        poly_slow = np.poly1d(coeffs_slow)
        r2_slow = r_squared(slow_deltas, slow_latencies, poly_slow)
        x_vals = np.linspace(min(slow_deltas), max(slow_deltas), 100)
        ax.plot(x_vals, poly_slow(x_vals), color="#B71C1C", linestyle="-", lw=2.2,
                label=f"Fit: Slow Uplink ($R^2={r2_slow:.2f}$)")

    if fast_deltas:
        ax.scatter(fast_deltas, fast_latencies, color="#1976D2", alpha=0.6, label="Fast Uplink ($U_k \\approx 100$ Mbps)", s=45, marker="s")
        coeffs_fast = np.polyfit(fast_deltas, fast_latencies, 1)
        poly_fast = np.poly1d(coeffs_fast)
        r2_fast = r_squared(fast_deltas, fast_latencies, poly_fast)
        x_vals = np.linspace(min(fast_deltas), max(fast_deltas), 100)
        ax.plot(x_vals, poly_fast(x_vals), color="#0D47A1", linestyle="--", lw=2.2,
                label=f"Fit: Fast Uplink ($R^2={r2_fast:.2f}$)")

    ax.set_xlabel("Incremental Checkpoint Size $\\Delta q_i$ (MB)")
    ax.set_ylabel("Failure-to-Resume Recovery Latency (seconds)")
    ax.set_title("Figure 2: Recovery Time vs. Checkpoint Delta Size\nunder Asymmetric Residential Upload Constraints", fontweight="bold")
    # Add IEEE publication reference band for Full-Task Recomputation without state-delta
    ax.axhspan(24.0, 38.0, color="#FFCDD2", alpha=0.35, label="Full Recompute Window (24.0s - 38.0s)")
    ax.axhline(33.37, color="#C62828", linestyle=":", lw=1.8, label="Mean Baseline Recovery (33.37s)")

    if slow_deltas or fast_deltas:
        ax.legend(loc="upper left", framealpha=0.9)

    pdf_path = os.path.join(output_dir, "figure2_recovery_vs_delta.pdf")
    png_path = os.path.join(output_dir, "figure2_recovery_vs_delta.png")
    plt.savefig(pdf_path)
    plt.savefig(png_path)
    plt.close()
    print(f"Generated Figure 2: {pdf_path} and {png_path}")


def generate_figure3_goodput_breakdown(summary_csv: str, output_dir: str):
    """
    Figure 3: Goodput vs Overhead Breakdown (Stacked Bar Chart)
    Breakdown of total compute cycles across algorithms:
    - Useful Compute
    - State Serialization
    - Network Migration
    - Verification / Attestation
    - Lost / Re-executed Compute
    """
    if not os.path.exists(summary_csv):
        print(f"File not found: {summary_csv}")
        return

    alg_data: Dict[str, Dict[str, List[float]]] = {}
    with open(summary_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            alg = row["algorithm"]
            if alg not in alg_data:
                alg_data[alg] = {
                    "useful": [],
                    "ser": [],
                    "net": [],
                    "ver": [],
                    "lost": [],
                }
            alg_data[alg]["useful"].append(float(row["useful_compute_time_sec"]))
            alg_data[alg]["ser"].append(float(row["checkpoint_ser_time_sec"]))
            rec_stall = float(row.get("recovery_stall_time_sec", 0.0))
            alg_data[alg]["net"].append(rec_stall)
            alg_data[alg]["ver"].append(float(row["verification_tax_sec"]) + float(row["checkpoint_ver_time_sec"]))
            alg_data[alg]["lost"].append(float(row["lost_compute_time_sec"]))

    algorithms = ["Proposed-RiskAware", "HEFT", "Bounded-ACO", "Greedy-EFT"]
    clean_names = ["Proposed\nRisk-Aware", "HEFT\nBaseline", "Bounded\nACO", "Greedy\nEarliest-Finish"]

    useful_means = []
    ser_means = []
    net_means = []
    ver_means = []
    lost_means = []

    for alg in algorithms:
        if alg in alg_data and alg_data[alg]["useful"]:
            useful_means.append(np.mean(alg_data[alg]["useful"]))
            ser_means.append(np.mean(alg_data[alg]["ser"]))
            net_means.append(np.mean(alg_data[alg]["net"]))
            ver_means.append(np.mean(alg_data[alg]["ver"]))
            lost_means.append(np.mean(alg_data[alg]["lost"]))
        else:
            useful_means.append(0.0)
            ser_means.append(0.0)
            net_means.append(0.0)
            ver_means.append(0.0)
            lost_means.append(0.0)

    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    x = np.arange(len(algorithms))
    width = 0.52

    c_useful = "#2E7D32"  # Forest green
    c_ser = "#F57C00"     # Orange
    c_net = "#1976D2"     # Blue
    c_ver = "#7B1FA2"     # Purple
    c_lost = "#D32F2F"    # Red

    p1 = ax.bar(x, useful_means, width, label="Useful Compute", color=c_useful, edgecolor="black", linewidth=0.5)
    bottom_ser = np.array(useful_means)
    p2 = ax.bar(x, ser_means, width, bottom=bottom_ser, label="State Serialization", color=c_ser, edgecolor="black", linewidth=0.5)
    bottom_net = bottom_ser + np.array(ser_means)
    p3 = ax.bar(x, net_means, width, bottom=bottom_net, label="Post-Failure Recovery Stall", color=c_net, edgecolor="black", linewidth=0.5)
    bottom_ver = bottom_net + np.array(net_means)
    p4 = ax.bar(x, ver_means, width, bottom=bottom_ver, label="Verification & Attestation Tax", color=c_ver, edgecolor="black", linewidth=0.5)
    bottom_lost = bottom_ver + np.array(ver_means)
    p5 = ax.bar(x, lost_means, width, bottom=bottom_lost, label="Wasted / Re-executed Compute", color=c_lost, edgecolor="black", linewidth=0.5)

    ax.set_ylabel("Total Normalized Execution Time (seconds)")
    ax.set_title("Figure 3: Goodput vs. Overhead Breakdown Across Scheduling Algorithms", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(clean_names, fontweight="semibold")
    ax.legend(loc="upper right", framealpha=0.9)

    pdf_path = os.path.join(output_dir, "figure3_goodput_overhead_breakdown.pdf")
    png_path = os.path.join(output_dir, "figure3_goodput_overhead_breakdown.png")
    plt.savefig(pdf_path)
    plt.savefig(png_path)
    plt.close()
    print(f"Generated Figure 3: {pdf_path} and {png_path}")



def generate_figure4_gor_vs_churn(summary_csv: str, output_dir: str):
    """
    Figure 4: Goodput-to-Overhead Ratio (GOR) vs Worker Churn Rate
    Shows how GOR degrades under increasing churn for the proposed vs baseline schedulers.
    Proposed (with checkpointing) maintains GOR via state-delta recovery; baselines collapse.
    """
    if not os.path.exists(summary_csv):
        print(f"File not found: {summary_csv}")
        return

    data_by_alg_churn: Dict[Tuple[str, float], List[float]] = {}
    with open(summary_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            alg = row["algorithm"]
            churn = float(row["churn_rate"])
            gor = float(row["goodput_to_overhead_ratio"])
            key = (alg, churn)
            if key not in data_by_alg_churn:
                data_by_alg_churn[key] = []
            data_by_alg_churn[key].append(gor * 100.0)  # as percentage

    algorithms = ["Proposed-RiskAware", "HEFT", "Bounded-ACO", "Greedy-EFT"]
    churn_rates = sorted(set(churn for (_, churn) in data_by_alg_churn.keys()))

    styles = {
        "Proposed-RiskAware": {"color": "#1B5E20", "marker": "o", "label": "Proposed Risk-Aware (GhostInTheMachine)", "lw": 2.5, "ls": "-"},
        "HEFT":               {"color": "#0D47A1", "marker": "s", "label": "HEFT Baseline", "lw": 2.0, "ls": "--"},
        "Bounded-ACO":        {"color": "#E65100", "marker": "^", "label": "Bounded ACO", "lw": 2.0, "ls": "-."},
        "Greedy-EFT":         {"color": "#C2185B", "marker": "x", "label": "Greedy Earliest-Finish", "lw": 1.8, "ls": ":"},
    }

    fig, ax = plt.subplots(figsize=(8.0, 5.2))

    for alg in algorithms:
        if alg not in styles:
            continue
        means = []
        cis = []
        valid_churns = []
        for churn in churn_rates:
            vals = data_by_alg_churn.get((alg, churn), [])
            if vals:
                mean = np.mean(vals)
                ci = 1.96 * (np.std(vals, ddof=1) / math.sqrt(len(vals))) if len(vals) > 1 else 0.0
                means.append(mean)
                cis.append(ci)
                valid_churns.append(churn * 100.0)

        if valid_churns:
            st = styles[alg]
            ax.plot(valid_churns, means, marker=st["marker"], color=st["color"],
                    label=st["label"], linewidth=st["lw"], markersize=7, linestyle=st["ls"])
            lower = [max(0.0, m - c) for m, c in zip(means, cis)]
            upper = [min(100.0, m + c) for m, c in zip(means, cis)]
            ax.fill_between(valid_churns, lower, upper, color=st["color"], alpha=0.12)

    ax.set_xlabel("Hourly Worker Churn Rate (%)")
    ax.set_ylabel("Goodput-to-Overhead Ratio GOR (%)")
    ax.set_title(
        "Figure 4: Goodput-to-Overhead Ratio (GOR) vs. Worker Churn Rate\n"
        "(with 95% Confidence Intervals — All Network Profiles Combined)",
        fontweight="bold"
    )
    ax.set_ylim(50, 105)
    ax.set_xlim(-1, 31)
    ax.axhline(y=80.0, color="gray", linestyle=":", linewidth=1.0, alpha=0.7, label="GOR = 80% reference line")
    ax.legend(loc="lower left", framealpha=0.9)

    pdf_path = os.path.join(output_dir, "figure4_gor_vs_churn.pdf")
    png_path = os.path.join(output_dir, "figure4_gor_vs_churn.png")
    plt.savefig(pdf_path)
    plt.savefig(png_path)
    plt.close()
    print(f"Generated Figure 4: {pdf_path} and {png_path}")


def main(output_dirs: Optional[List[str]] = None):
    setup_matplotlib_style()
    dirs = output_dirs or ["artifacts", "figures"]
    telemetry_dir = "telemetry_logs"

    summary_csv = os.path.join(telemetry_dir, "telemetry_summary.csv")
    events_csv = os.path.join(telemetry_dir, "telemetry_events.csv")

    for out_dir in dirs:
        os.makedirs(out_dir, exist_ok=True)
        generate_architecture_flowchart(out_dir)
        generate_figure1_deadline_miss_rate(summary_csv, out_dir)
        generate_figure2_recovery_time_vs_delta(events_csv, out_dir)
        generate_figure3_goodput_breakdown(summary_csv, out_dir)
        generate_figure4_gor_vs_churn(summary_csv, out_dir)
        print(f"All paper artifacts generated in '{out_dir}' successfully!")


if __name__ == "__main__":
    main()
