"""
generate_synopsis_figures.py
============================
Generates high-resolution (300 DPI) publication-quality figures for the
GhostInTheMachine DevOps Project Synopsis:
1. artifacts/synopsis_devops_architecture.png
2. artifacts/synopsis_workflow_lifecycle.png
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUTPUT_DIR = r"p:\GhostInTheMachine\artifacts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_devops_architecture():
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.8)
    ax.axis("off")

    # Title & Subtitle
    ax.text(6.0, 7.5, "GhostInTheMachine: Multi-Tier DevOps Infrastructure & Orchestration Architecture",
            fontsize=13, fontweight="bold", ha="center", va="center", color="#0D47A1")
    ax.text(6.0, 7.22, "Infrastructure as Code (Terraform) • Agentless Orchestration (Ansible) • Observability & Automated Failover (Nagios Core)",
            fontsize=9.5, fontstyle="italic", ha="center", va="center", color="#424242")

    # Tier 1: Infrastructure as Code (Terraform)
    t1_rect = patches.FancyBboxPatch((0.5, 5.3), 11.0, 1.65, boxstyle="round,pad=0.1,rounding_size=0.15",
                                     facecolor="#E8EAF6", edgecolor="#3949AB", linewidth=1.8)
    ax.add_patch(t1_rect)
    ax.text(0.7, 6.75, "TIER 1: INFRASTRUCTURE AS CODE (TERRAFORM v1.8+)", fontsize=10.5, fontweight="bold", color="#1A237E")

    t1_boxes = [
        {"x": 0.8, "y": 5.45, "w": 2.4, "h": 1.15, "title": "Declarative Topology", "sub": "• HCL Cluster Blueprint\n• Multi-Tier Worker Matrix\n• MinIO S3 Replica Store", "col": "#FFFFFF", "border": "#3F51B5"},
        {"x": 3.5, "y": 5.45, "w": 2.6, "h": 1.15, "title": "Heterogeneous Compute", "sub": "• AWS Spot c5.large (2.0x)\n• On-Demand t3.medium (1.25x)\n• Edge Spot t3.small (0.8x)", "col": "#FFFFFF", "border": "#3F51B5"},
        {"x": 6.4, "y": 5.45, "w": 2.5, "h": 1.15, "title": "Asymmetric tc/netem", "sub": "• 10 Mbps Egress Ceiling\n• 25ms Delay, 5ms Jitter\n• HTB Kernel Qdiscs", "col": "#FFF9C4", "border": "#FBC02D"},
        {"x": 9.2, "y": 5.45, "w": 2.1, "h": 1.15, "title": "Security & IAM", "sub": "• Scoped S3 Policies\n• VPC Isolated Subnets\n• Bastion Ingress Filter", "col": "#FFFFFF", "border": "#3F51B5"},
    ]
    for b in t1_boxes:
        rect = patches.FancyBboxPatch((b["x"], b["y"]), b["w"], b["h"], boxstyle="round,pad=0.08,rounding_size=0.1",
                                      facecolor=b["col"], edgecolor=b["border"], linewidth=1.2)
        ax.add_patch(rect)
        ax.text(b["x"] + b["w"]/2, b["y"] + b["h"] - 0.22, b["title"], fontsize=8.8, fontweight="bold", ha="center", color="#1A237E")
        ax.text(b["x"] + 0.12, b["y"] + b["h"] - 0.42, b["sub"], fontsize=7.2, va="top", color="#212121", linespacing=1.25)

    # Downward connector arrow
    ax.annotate("", xy=(6.0, 5.25), xytext=(6.0, 5.0),
                arrowprops=dict(arrowstyle="<-", color="#3949AB", lw=2.2))

    # Tier 2: Agentless Orchestration & Zero-Trust Hardening (Ansible)
    t2_rect = patches.FancyBboxPatch((0.5, 3.5), 11.0, 1.45, boxstyle="round,pad=0.1,rounding_size=0.15",
                                     facecolor="#E0F2F1", edgecolor="#00796B", linewidth=1.8)
    ax.add_patch(t2_rect)
    ax.text(0.7, 4.75, "TIER 2: AGENTLESS ORCHESTRATION & ZERO-TRUST HARDENING (ANSIBLE v2.16+)", fontsize=10.5, fontweight="bold", color="#004D40")

    t2_boxes = [
        {"x": 0.8, "y": 3.65, "w": 2.4, "h": 0.95, "title": "Runtime Provisioning", "sub": "• Python 3.11 Isolated Venv\n• Pinned Scipy & Cryptography", "col": "#FFFFFF", "border": "#00897B"},
        {"x": 3.5, "y": 3.65, "w": 2.6, "h": 0.95, "title": "RATS Attestation Agent", "sub": "• TPM 2.0 PCR Quote Daemon\n• IETF RFC 9334 Attestation", "col": "#FFFFFF", "border": "#00897B"},
        {"x": 6.4, "y": 3.65, "w": 2.5, "h": 0.95, "title": "State-Delta Sync Daemon", "sub": "• Asynchronous S3 Delta Push\n• cgroups v2 (CPU 40%, 1G RAM)", "col": "#FFFFFF", "border": "#00897B"},
        {"x": 9.2, "y": 3.65, "w": 2.1, "h": 0.95, "title": "Host Hardening", "sub": "• Non-root ghost User\n• UFW & Ed25519 Keys", "col": "#FFFFFF", "border": "#00897B"},
    ]
    for b in t2_boxes:
        rect = patches.FancyBboxPatch((b["x"], b["y"]), b["w"], b["h"], boxstyle="round,pad=0.08,rounding_size=0.1",
                                      facecolor=b["col"], edgecolor=b["border"], linewidth=1.2)
        ax.add_patch(rect)
        ax.text(b["x"] + b["w"]/2, b["y"] + b["h"] - 0.20, b["title"], fontsize=8.8, fontweight="bold", ha="center", color="#004D40")
        ax.text(b["x"] + 0.12, b["y"] + b["h"] - 0.38, b["sub"], fontsize=7.2, va="top", color="#212121", linespacing=1.25)

    # Downward connector arrow
    ax.annotate("", xy=(6.0, 3.45), xytext=(6.0, 3.2),
                arrowprops=dict(arrowstyle="<-", color="#00796B", lw=2.2))

    # Tier 3: Zero-Trust DAG Runtime & Risk-Aware Scheduler (GhostInTheMachine)
    t3_rect = patches.FancyBboxPatch((0.5, 1.8), 11.0, 1.35, boxstyle="round,pad=0.1,rounding_size=0.15",
                                     facecolor="#FFF3E0", edgecolor="#E65100", linewidth=1.8)
    ax.add_patch(t3_rect)
    ax.text(0.7, 2.95, "TIER 3: ZERO-TRUST DAG RUNTIME & RISK-AWARE SCHEDULER (GHOSTINTHEMACHINE)", fontsize=10.5, fontweight="bold", color="#BF360C")

    t3_boxes = [
        {"x": 0.8, "y": 1.95, "w": 2.4, "h": 0.85, "title": "Workflow Ingestion", "sub": "• Pegasus DAG Parser\n• Compute w_i, Payload d_ij", "col": "#FFFFFF", "border": "#FB8C00"},
        {"x": 3.5, "y": 1.95, "w": 2.6, "h": 0.85, "title": "Feasibility Gate F(i,k)", "sub": "• Memory & Capability Check\n• RFC 9334 Attest Validation", "col": "#FFFFFF", "border": "#FB8C00"},
        {"x": 6.4, "y": 1.95, "w": 2.5, "h": 0.85, "title": "Risk-Aware Placement", "sub": "• Min J(i,k) with Crit(i) Slack\n• Upload Penalty Mitigation", "col": "#FFFFFF", "border": "#FB8C00"},
        {"x": 9.2, "y": 1.95, "w": 2.1, "h": 0.85, "title": "Adaptive Checkpoint", "sub": "• Young/Daly tau Scaling\n• 8 MB Delta Persistence", "col": "#FFFFFF", "border": "#FB8C00"},
    ]
    for b in t3_boxes:
        rect = patches.FancyBboxPatch((b["x"], b["y"]), b["w"], b["h"], boxstyle="round,pad=0.08,rounding_size=0.1",
                                      facecolor=b["col"], edgecolor=b["border"], linewidth=1.2)
        ax.add_patch(rect)
        ax.text(b["x"] + b["w"]/2, b["y"] + b["h"] - 0.18, b["title"], fontsize=8.8, fontweight="bold", ha="center", color="#BF360C")
        ax.text(b["x"] + 0.12, b["y"] + b["h"] - 0.35, b["sub"], fontsize=7.2, va="top", color="#212121", linespacing=1.2)

    # Downward connector arrow
    ax.annotate("", xy=(6.0, 1.75), xytext=(6.0, 1.5),
                arrowprops=dict(arrowstyle="<-", color="#E65100", lw=2.2))

    # Tier 4: Observability & Automated Incident Recovery (Nagios Core)
    t4_rect = patches.FancyBboxPatch((0.5, 0.15), 11.0, 1.3, boxstyle="round,pad=0.1,rounding_size=0.15",
                                     facecolor="#FFEBEE", edgecolor="#C62828", linewidth=1.8)
    ax.add_patch(t4_rect)
    ax.text(0.7, 1.25, "TIER 4: CONTINUOUS OBSERVABILITY & AUTOMATED FAILOVER (NAGIOS CORE v4.5+)", fontsize=10.5, fontweight="bold", color="#B71C1C")

    t4_boxes = [
        {"x": 0.8, "y": 0.28, "w": 2.4, "h": 0.82, "title": "Continuous Health Probes", "sub": "• 5s TCP/ICMP Node Heartbeats\n• Host Availability Tracking", "col": "#FFFFFF", "border": "#E53935"},
        {"x": 3.5, "y": 0.28, "w": 2.6, "h": 0.82, "title": "Spot Interruption Warning", "sub": "• 2s Polling on AWS Rebalance\n• Instant Churn Flagging", "col": "#FFFFFF", "border": "#E53935"},
        {"x": 6.4, "y": 0.28, "w": 2.5, "h": 0.82, "title": "Uplink Saturation Monitor", "sub": "• > 9.0 Mbps Alert Trigger\n• Queueing Bottleneck Alert", "col": "#FFFFFF", "border": "#E53935"},
        {"x": 9.2, "y": 0.28, "w": 2.1, "h": 0.82, "title": "HMAC Event Handler", "sub": "• Webhook to Scheduler\n• 1.28s Delta Failover", "col": "#FFCDD2", "border": "#B71C1C"},
    ]
    for b in t4_boxes:
        rect = patches.FancyBboxPatch((b["x"], b["y"]), b["w"], b["h"], boxstyle="round,pad=0.08,rounding_size=0.1",
                                      facecolor=b["col"], edgecolor=b["border"], linewidth=1.2)
        ax.add_patch(rect)
        ax.text(b["x"] + b["w"]/2, b["y"] + b["h"] - 0.18, b["title"], fontsize=8.8, fontweight="bold", ha="center", color="#B71C1C")
        ax.text(b["x"] + 0.12, b["y"] + b["h"] - 0.35, b["sub"], fontsize=7.2, va="top", color="#212121", linespacing=1.2)

    # Loopback recovery arrow from Tier 4 back to Tier 3
    ax.annotate("Automated Preemption Event Webhook\n(Triggers Delta Replay on Worker k')",
                xy=(10.25, 1.8), xytext=(10.25, 1.2),
                arrowprops=dict(arrowstyle="->", color="#B71C1C", lw=2.0, connectionstyle="arc3,rad=-0.3"),
                fontsize=7.2, fontweight="bold", color="#B71C1C", ha="center")

    out_path = os.path.join(OUTPUT_DIR, "synopsis_devops_architecture.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated DevOps Architecture Diagram: {out_path}")

def generate_workflow_lifecycle():
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8.0)
    ax.axis("off")

    ax.text(6.0, 7.7, "GhostInTheMachine: End-to-End System Execution & Fault-Tolerance Lifecycle Flowchart",
            fontsize=12.5, fontweight="bold", ha="center", va="center", color="#0D47A1")
    ax.text(6.0, 7.42, "From Declarative Provisioning to Zero-Trust Scheduling, Continuous Monitoring, and 1.28s State-Delta Failover",
            fontsize=9.2, fontstyle="italic", ha="center", va="center", color="#424242")

    boxes = [
        {"id": "ingest", "x": 0.4, "y": 5.9, "w": 2.2, "h": 1.1, "title": "Scientific DAG Ingestion", "sub": "Pegasus Workflow G=(V,E)\nCompute Demand w_i, RAM m_i\nPayload Size d_ij, Snapshot q_i", "col": "#E1F5FE", "border": "#0288D1"},
        {"id": "tf", "x": 3.2, "y": 5.9, "w": 2.4, "h": 1.1, "title": "1. Terraform Provisioning", "sub": "Heterogeneous AWS Spot/EC2\nMinIO Peer Replica Store (S3)\ntc/netem 10 Mbps Egress Cap", "col": "#EDE7F6", "border": "#512DA8"},
        {"id": "ansible", "x": 6.2, "y": 5.9, "w": 2.5, "h": 1.1, "title": "2. Ansible Orchestration", "sub": "Python 3.11 Environment\nRATS Attestation Daemon (TPM)\nState-Delta Sync Daemon (cgroups)", "col": "#E0F2F1", "border": "#00796B"},
        {"id": "gate", "x": 9.3, "y": 5.9, "w": 2.3, "h": 1.1, "title": "3. Feasibility Gate F(i,k)", "sub": "m_i <= M_k (RAM Bounds)\nc_i in C_k (Instruction Sets)\nAttest(k) == VALID (RATS Quote)", "col": "#FFF3E0", "border": "#E65100"},

        {"id": "sched", "x": 9.3, "y": 4.1, "w": 2.3, "h": 1.2, "title": "4. Risk-Aware Scheduler", "sub": "Compute Upward Rank rank_u(i)\nCrit(i) = 1.0 + 1.5*(rank/max)\nMin J(i,k) = EFT + delta*E_ckpt\n  + eta*E_restart + rho*E_ver", "col": "#FFF8E1", "border": "#FFA000"},
        {"id": "exec", "x": 6.2, "y": 4.1, "w": 2.5, "h": 1.2, "title": "5. Task Execution & Delta", "sub": "Assigned to Best Worker k*\nYoung/Daly Checkpoint Gate\nAsync 8 MB Delta Upload to MinIO\nSync CPU Stall: 0.035s only", "col": "#E8F5E9", "border": "#2E7D32"},
        {"id": "nagios", "x": 3.2, "y": 4.1, "w": 2.4, "h": 1.2, "title": "6. Nagios Core Monitor", "sub": "5s ICMP/TCP Heartbeat\n2s Spot Interruption Poller\nResidential Uplink Saturation\nWorker Health Decision", "col": "#FFEBEE", "border": "#C62828"},

        {"id": "failover", "x": 3.2, "y": 2.0, "w": 2.4, "h": 1.4, "title": "7. Event Handler Failover", "sub": "Trigger: handle_preemption.py\nHMAC-SHA256 Signed Webhook\nScheduler picks Worker k'\nDownload 8 MB Delta (100 Mbps)\nResume in 1.28s (98% Faster!)", "col": "#FCE4EC", "border": "#880E4F"},
        {"id": "complete", "x": 0.4, "y": 4.1, "w": 2.2, "h": 1.2, "title": "8. Task Output Commit", "sub": "Worker Alive & Healthy\nOutput payload d_ij generated\nSuccessor tasks unlocked\nForward execution proceeds", "col": "#E8EAF6", "border": "#283593"},

        {"id": "sla", "x": 0.4, "y": 2.0, "w": 2.2, "h": 1.4, "title": "9. SLA & Telemetry Audit", "sub": "Workflow DAG Complete\nCheck D_SLA = 1.20 x CritPath\nMiss Rate: 0.0% Under 30% Churn\nGOR Preserved: 96.8% - 97.1%\nProvenance Hash Logged", "col": "#E0F7FA", "border": "#00838F"},
    ]

    for b in boxes:
        rect = patches.FancyBboxPatch((b["x"], b["y"]), b["w"], b["h"], boxstyle="round,pad=0.08,rounding_size=0.12",
                                      facecolor=b["col"], edgecolor=b["border"], linewidth=1.4)
        ax.add_patch(rect)
        ax.text(b["x"] + b["w"]/2, b["y"] + b["h"] - 0.22, b["title"], fontsize=8.8, fontweight="bold", ha="center", color=b["border"])
        ax.text(b["x"] + 0.12, b["y"] + b["h"] - 0.42, b["sub"], fontsize=7.1, va="top", color="#212121", linespacing=1.2)

    # Arrows for Pipeline Flow
    arrow_spec = dict(arrowstyle="->", color="#37474F", lw=1.8)
    
    # Ingest -> Terraform -> Ansible -> Gate
    ax.annotate("", xy=(3.2, 6.45), xytext=(2.6, 6.45), arrowprops=arrow_spec)
    ax.annotate("", xy=(6.2, 6.45), xytext=(5.6, 6.45), arrowprops=arrow_spec)
    ax.annotate("", xy=(9.3, 6.45), xytext=(8.7, 6.45), arrowprops=arrow_spec)

    # Gate -> Sched (Downward)
    ax.annotate("", xy=(10.45, 5.3), xytext=(10.45, 5.9), arrowprops=arrow_spec)

    # Sched -> Exec -> Nagios
    ax.annotate("", xy=(8.7, 4.7), xytext=(9.3, 4.7), arrowprops=arrow_spec)
    ax.annotate("", xy=(5.6, 4.7), xytext=(6.2, 4.7), arrowprops=arrow_spec)

    # Nagios -> Complete (Healthy path)
    ax.annotate("", xy=(2.6, 4.7), xytext=(3.2, 4.7), arrowprops=dict(arrowstyle="->", color="#2E7D32", lw=2.0))
    ax.text(2.9, 4.88, "Healthy", fontsize=8.0, fontweight="bold", color="#2E7D32", ha="center")

    # Nagios -> Failover (Preemption path downward)
    ax.annotate("", xy=(4.4, 3.4), xytext=(4.4, 4.1), arrowprops=dict(arrowstyle="->", color="#C62828", lw=2.0))
    ax.text(4.4, 3.75, "Preempted!", fontsize=8.0, fontweight="bold", color="#C62828", ha="center")

    # Failover loops back to Exec
    ax.annotate("Re-assigned to k' via 8 MB Delta", xy=(6.8, 4.1), xytext=(5.6, 2.7),
                arrowprops=dict(arrowstyle="->", color="#880E4F", lw=2.0, connectionstyle="arc3,rad=-0.25"),
                fontsize=7.5, fontweight="bold", color="#880E4F")

    # Complete -> SLA
    ax.annotate("", xy=(1.5, 3.4), xytext=(1.5, 4.1), arrowprops=arrow_spec)

    # Metric callout box at bottom center-right
    callout_rect = patches.FancyBboxPatch((6.2, 0.4), 5.4, 2.8, boxstyle="round,pad=0.1,rounding_size=0.12",
                                          facecolor="#F3E5F5", edgecolor="#7B1FA2", linewidth=1.5)
    ax.add_patch(callout_rect)
    ax.text(8.9, 2.95, "CORE EMPIRICAL BENCHMARKS (1,120 RUNS)", fontsize=9.2, fontweight="bold", ha="center", color="#4A148C")
    metrics_text = (
        "• Recovery Latency: 1.28s ± 0.05s vs. 62.32s Baseline (98.0% / 49x Speedup, p < 0.0001)\n"
        "• Goodput-to-Overhead Ratio (GOR): Sustains 96.79% - 97.10% under 30% Churn (vs. 79.1% Base)\n"
        "• SLA Deadline Miss Rate: Strictly 0.0% (vs. 20.0% - 25.0% Failures in Legacy Heuristics)\n"
        "• Quiescent Parity: Matches HEFT at 99.59% GOR and 137.6s Makespan under zero churn\n"
        "• DevOps Verification: Nagios 2s spot notice + Ansible cgroups bounds CPU tax to < 0.25%"
    )
    ax.text(6.4, 2.70, metrics_text, fontsize=7.4, va="top", color="#212121", linespacing=1.35)

    out_path = os.path.join(OUTPUT_DIR, "synopsis_workflow_lifecycle.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated Workflow Lifecycle Diagram: {out_path}")

if __name__ == "__main__":
    generate_devops_architecture()
    generate_workflow_lifecycle()
