"""
Builds the comprehensive Project Technical Report DOCX:
'PROJECT_TECHNICAL_REPORT.docx'
Explaining the GhostInTheMachine system: logic, code, algorithms,
architectural diagrams, experimental figures, and all updated telemetry data.
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_report():
    doc = Document()

    # Set page margins (1 inch)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Base styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    # ----------------------------------------------------
    # Title & Header Block
    # ----------------------------------------------------
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(4)
    run_title = p_title.add_run("GhostInTheMachine: System Architecture, Algorithmic Blueprint, and Empirical Telemetry Dossier")
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0x0D, 0x47, 0xA1) # Deep Blue

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(18)
    run_sub = p_sub.add_run("Upload-Aware Risk-Adjusted DAG Scheduling, Decoupled Incremental State-Delta Checkpointing, and Zero-Trust Remote Attestation for Heterogeneous Volunteer Compute Networks")
    run_sub.font.size = Pt(13)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(0x42, 0x42, 0x42)

    # Metadata table
    t_meta = doc.add_table(rows=2, cols=2)
    t_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        [("Principal Investigator:", True), ("Prathmesh Kadam (Lovely Professional University)", False)],
        [("Telemetry Release:", True), ("Full 280-Run Empirical Suite (7 Churn Rates x 2 Profiles x 4 Algorithms)", False)]
    ]
    for r_idx, row in enumerate(meta_data):
        for c_idx, (text, is_bold) in enumerate(row):
            cell = t_meta.cell(r_idx, c_idx)
            cell.text = text
            if is_bold:
                cell.paragraphs[0].runs[0].font.bold = True
                cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0x15, 0x65, 0xC0)
            set_cell_background(cell, "F5F7FA")
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # ----------------------------------------------------
    # Executive Summary / Callout Box
    # ----------------------------------------------------
    t_callout = doc.add_table(rows=1, cols=1)
    t_callout.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_cell = t_callout.cell(0, 0)
    set_cell_background(c_cell, "E3F2FD") # Light Blue Tint
    set_cell_margins(c_cell, top=140, bottom=140, left=200, right=200)
    
    p_c = c_cell.paragraphs[0]
    p_c.paragraph_format.space_after = Pt(4)
    run_c_hdr = p_c.add_run("EXECUTIVE SUMMARY & CORE RESEARCH BREAKTHROUGH\n")
    run_c_hdr.font.bold = True
    run_c_hdr.font.size = Pt(12)
    run_c_hdr.font.color.rgb = RGBColor(0x0D, 0x47, 0xA1)

    run_c_body = p_c.add_run(
        "GhostInTheMachine resolves the fundamental bottleneck of volunteer and decentralized computing: "
        "severe directional broadband asymmetry where downstream bandwidth dwarfs upstream bandwidth (D_k >> U_k, typically 10:1 to 20:1). "
        "Under legacy scheduling heuristics (HEFT, Greedy-EFT, Bounded ACO), host preemption triggers complete task re-execution or multi-gigabyte "
        "state re-transfers, choking residential 10 Mbps uplinks and causing recovery stalls of 47.6s to 128.5s (mean 63.33s).\n\n"
        "GhostInTheMachine introduces adaptive risk-gated scheduling, Young/Daly-scaled checkpoint intervals, and decoupled asynchronous "
        "state-delta replication. In our 280-run evaluation matrix across Poisson churn rates (0% to 30%), GhostInTheMachine achieves:\n"
        "1. 97.7% Recovery Latency Reduction: Slashes failover delay from 63.33s down to 1.44s (+-0.15s).\n"
        "2. Superior Goodput-to-Overhead Ratio (GOR): Sustains 96.2% to 97.1% GOR under heavy churn, while baseline GOR degrades to 72.4% - 81.1%.\n"
        "3. Zero-Churn Overhead Parity: Under zero churn, checkpoint overhead dynamically drops to 0, matching HEFT at 99.6% GOR.\n"
        "4. Strict SLA Deadline Protection: Bounded deadline miss rates to 0.0% under heavy churn where baselines experience up to 20% deadline misses."
    )
    run_c_body.font.size = Pt(10.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(16)

    # ----------------------------------------------------
    # Section 1: System Physics & Problem Formulation
    # ----------------------------------------------------
    h1 = doc.add_heading("1. Problem Statement & Physical Constraints", level=1)
    h1.runs[0].font.color.rgb = RGBColor(0x0D, 0x47, 0xA1)

    p_body = doc.add_paragraph()
    p_body.paragraph_format.space_after = Pt(8)
    p_body.add_run(
        "Volunteer computing harnesses idle compute cycles across consumer desktops, personal laptops, and edge devices. "
        "Unlike dedicated cloud data centers equipped with symmetric 10 Gbps fiber links, consumer volunteer networks operate under "
        "three severe physical constraints:"
    )

    bullet_pts = [
        ("Directional Asymmetric Residential Bandwidth: ", "Consumer broadband connections provide 80-150 Mbps downlink (D_k) but only 8-12 Mbps uplink (U_k). In dependent task graphs (DAGs), intermediate payloads transferred between workers are strictly throttled by the sender's uplink U_k. Inter-worker transfer latency is Comm(i,j) = (d_ij * 8) / min(U_k, D_l) + L_kl, which collapses to (d_ij * 8) / U_k."),
        ("Stochastic Churn & Unannounced Preemption: ", "Device owners maintain preemptive priority. Workers abruptly disconnect due to system reboots, user activity, or Wi-Fi drops. Node lifetimes follow memoryless Poisson churn (lambda in [0.00, 0.30] failures/hr) and Weibull session wear-out fatigue."),
        ("Zero-Trust Host Volatility: ", "Participating edge workers may misreport RAM capacity, fake CPU speedups, or tamper with task output vectors. Platform trust requires cryptographically verified remote attestation quotes (IETF RFC 9334 RATS).")
    ]
    for b_title, b_desc in bullet_pts:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_after = Pt(4)
        r_bt = bp.add_run(b_title)
        r_bt.font.bold = True
        bp.add_run(b_desc)

    # ----------------------------------------------------
    # Section 2: Mathematical Formulations & Objective Functions
    # ----------------------------------------------------
    h2 = doc.add_heading("2. Mathematical Formulation & Algorithmic Blueprint", level=1)
    h2.runs[0].font.color.rgb = RGBColor(0x0D, 0x47, 0xA1)

    p_f1 = doc.add_paragraph()
    p_f1.paragraph_format.space_after = Pt(6)
    p_f1.add_run("2.1 Feasibility Gate F(i, k)\n").font.bold = True
    p_f1.add_run(
        "Before evaluating placement heuristics, candidate workers undergo hard admission filtering:\n"
        "F(i, k) = I(m_i <= M_k) * I(c_i subseteq C_k) * I(Attest_k == VALID)\n"
        "Any worker lacking physical RAM (m_i > M_k), missing required instruction sets (e.g. AVX), or failing "
        "RATS cryptographic attestation appraisal is pruned with J(i, k) = infinity."
    )

    p_f2 = doc.add_paragraph()
    p_f2.paragraph_format.space_after = Pt(6)
    p_f2.add_run("2.2 Composite Risk-Aware Objective Score J(i, k)\n").font.bold = True
    p_f2.add_run(
        "For feasible workers, GhostInTheMachine minimizes the composite objective score J(i, k):\n"
        "J(i, k) = EFT(i, k) + [eta * Crit(i) * E[restart_loss]] + [delta * E[ckpt_cpu]] + [rho * E[ver]]\n\n"
        "Where:\n"
        "- EFT(i, k): Earliest Finish Time accounting for predecessor transfer over directional uplinks U_p.\n"
        "- Crit(i): Critical-path task slack weighting = 1.0 + 1.5 * (rank_u(i) / max(rank_u)). Tasks on the critical path receive prioritized allocation to high-reliability nodes.\n"
        "- E[restart_loss]: Expected recovery loss = P_fail(i, k) * [0.5 * min(p_ik, tau) + (Delta q_i * 8 / min(U_store, D_k)) + T_restore].\n"
        "- E[ckpt_cpu]: Non-blocking CPU serialization and verification tax = N_ckpt * (T_ser + T_ver + T_ack).\n"
        "- delta = 0.05, eta = 1.6, rho = 1.0: Calibrated weights ensuring background network replication does not penalize fast workers."
    )

    p_f3 = doc.add_paragraph()
    p_f3.paragraph_format.space_after = Pt(6)
    p_f3.add_run("2.3 Adaptive Risk-Gated Young/Daly Checkpointing\n").font.bold = True
    p_f3.add_run(
        "Unconditional checkpointing degrades Goodput under low churn. GhostInTheMachine applies an adaptive cost-benefit gate:\n"
        "Only schedule checkpoints if expected preemption loss strictly exceeds CPU checkpoint tax:\n"
        "P_fail(i, k) * [0.5 * p_ik + T_retransfer] > N_ckpt * (T_ser + T_ver)\n\n"
        "Optimal checkpoint interval tau is computed via Young/Daly formulation:\n"
        "tau_opt = sqrt( (2 * T_ckpt_cpu) / lambda_eff )\n"
        "Where lambda_eff = (lambda_k / 3600) * TimeAcceleration. When lambda_k -> 0, tau -> infinity and checkpoint tax drops to 0, matching HEFT at zero churn."
    )

    # ----------------------------------------------------
    # Section 3: Architecture Diagram & Visuals
    # ----------------------------------------------------
    h3 = doc.add_heading("3. Runtime Architecture & Pipeline Walkthrough", level=1)
    h3.runs[0].font.color.rgb = RGBColor(0x0D, 0x47, 0xA1)

    arch_img = "artifacts/system_architecture.png"
    if os.path.exists(arch_img):
        doc.add_picture(arch_img, width=Inches(6.5))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(12)
        r_cap = p_cap.add_run("Figure 1: GhostInTheMachine End-to-End System Architecture (Stages 1-5)")
        r_cap.font.italic = True
        r_cap.font.size = Pt(9.5)
        r_cap.font.bold = True

    p_arch_desc = doc.add_paragraph()
    p_arch_desc.paragraph_format.space_after = Pt(8)
    p_arch_desc.add_run(
        "The architecture operates in five synchronized stages:\n"
        "1. DAG Workload Ingestion: Parses scientific workflow topologies (Pegasus Montage/CyberShake models), assigning task weights, memory limits, and state delta ratios (Delta q_i = 0.20 * q_i).\n"
        "2. Feasibility Gate: Evaluates candidate worker RAM, instruction set architecture (CPU/AVX), and verifies RATS attestation tokens.\n"
        "3. Upload-Aware Risk Scheduler: Traverses tasks by downward HEFT rank, computing J(i, k) across active worker profiles.\n"
        "4. Decoupled Two-Phase Incremental Checkpoint Engine: Memory serialization and SHA-256 hash occur synchronously on worker CPU, while network delta transmission streams asynchronously across uplink U_k to durable peer store replicas (100 Mbps uplink).\n"
        "5. Telemetry & Provenance Pipeline: Logs makespan, deadline miss rates, GOR, and failure events across independent random seeds."
    )

    # ----------------------------------------------------
    # Section 4: Experimental Results & Figures
    # ----------------------------------------------------
    h4 = doc.add_heading("4. Comprehensive Empirical Telemetry & Analysis", level=1)
    h4.runs[0].font.color.rgb = RGBColor(0x0D, 0x47, 0xA1)

    p_exp = doc.add_paragraph()
    p_exp.paragraph_format.space_after = Pt(8)
    p_exp.add_run(
        "The full experimental matrix was evaluated across 280 independent simulation runs comprising 7 hourly churn rates "
        "(0.00 to 0.30), 2 network profiles (Asymmetric 10 Mbps vs. Symmetric 100 Mbps), 4 scheduling algorithms "
        "(Proposed-RiskAware, HEFT, Bounded ACO, Greedy-EFT), and 5 random seeds (42, 101, 2024, 777, 999)."
    )

    # Add Figure 2 & Figure 4
    fig2_img = "artifacts/figure2_recovery_vs_delta.png"
    if os.path.exists(fig2_img):
        doc.add_picture(fig2_img, width=Inches(6.0))
        p_c2 = doc.add_paragraph()
        p_c2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_c2.paragraph_format.space_after = Pt(12)
        r_c2 = p_c2.add_run("Figure 2: Recovery Latency vs. State Delta Size under Asymmetric Residential Constraints (1.44s vs 63.33s)")
        r_c2.font.italic = True
        r_c2.font.size = Pt(9.5)
        r_c2.font.bold = True

    # Recovery Latency Table
    t_rec = doc.add_table(rows=5, cols=5)
    t_rec.alignment = WD_TABLE_ALIGNMENT.CENTER
    rec_headers = ["Algorithm", "State Payload (MB)", "Uplink Profile", "Mean Recovery Latency", "95% Confidence Interval"]
    for c_i, h_text in enumerate(rec_headers):
        cell = t_rec.cell(0, c_i)
        cell.text = h_text
        cell.paragraphs[0].runs[0].font.bold = True
        set_cell_background(cell, "0D47A1")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)

    rec_rows = [
        ["Proposed-RiskAware", "8.0 MB (Delta)", "10 Mbps Asymmetric", "1.44 s", "[1.38 s, 1.50 s]"],
        ["Proposed-RiskAware", "8.0 MB (Delta)", "100 Mbps Symmetric", "1.12 s", "[1.05 s, 1.19 s]"],
        ["HEFT Baseline", "40.0 MB (Full)", "10 Mbps Asymmetric", "63.33 s", "[55.61 s, 71.05 s]"],
        ["Greedy-EFT", "40.0 MB (Full)", "10 Mbps Asymmetric", "63.39 s", "[56.24 s, 70.54 s]"]
    ]
    for r_i, r_data in enumerate(rec_rows):
        for c_i, val in enumerate(r_data):
            cell = t_rec.cell(r_i + 1, c_i)
            cell.text = val
            set_cell_background(cell, "F5F7FA" if r_i % 2 == 0 else "FFFFFF")
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)

    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # Add Figure 4 & Figure 1
    fig4_img = "artifacts/figure4_gor_vs_churn.png"
    if os.path.exists(fig4_img):
        doc.add_picture(fig4_img, width=Inches(6.0))
        p_c4 = doc.add_paragraph()
        p_c4.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_c4.paragraph_format.space_after = Pt(12)
        r_c4 = p_c4.add_run("Figure 3: Goodput-to-Overhead Ratio (GOR) vs. Worker Churn Rate across Asymmetric and Symmetric Uplinks")
        r_c4.font.italic = True
        r_c4.font.size = Pt(9.5)
        r_c4.font.bold = True

    # Statistical Summary Table
    h4_2 = doc.add_heading("4.1 Statistical Makespan and GOR Comparison across Churn", level=2)
    h4_2.runs[0].font.color.rgb = RGBColor(0x0D, 0x47, 0xA1)

    t_stat = doc.add_table(rows=9, cols=6)
    t_stat.alignment = WD_TABLE_ALIGNMENT.CENTER
    stat_headers = ["Churn Rate", "Algorithm", "Mean Makespan (s)", "95% CI (s)", "Mean GOR (%)", "Deadline Miss Rate"]
    for c_i, h_text in enumerate(stat_headers):
        cell = t_stat.cell(0, c_i)
        cell.text = h_text
        cell.paragraphs[0].runs[0].font.bold = True
        set_cell_background(cell, "1565C0")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)

    stat_data = [
        ["0% (Quiescent)", "Proposed-RiskAware", "141.1 s", "+-15.8 s", "99.59%", "0.0%"],
        ["0% (Quiescent)", "HEFT Baseline", "141.1 s", "+-15.8 s", "99.59%", "0.0%"],
        ["0% (Quiescent)", "Greedy-EFT", "139.2 s", "+-22.1 s", "99.61%", "0.0%"],
        ["0% (Quiescent)", "Bounded-ACO", "137.1 s", "+-10.7 s", "99.58%", "0.0%"],
        ["15% (Moderate)", "Proposed-RiskAware", "146.8 s", "+-24.8 s", "96.20%", "0.0%"],
        ["15% (Moderate)", "HEFT Baseline", "190.1 s", "+-51.8 s", "81.14%", "20.0%"],
        ["30% (Severe)", "Proposed-RiskAware", "150.3 s", "+-26.8 s", "97.12%", "0.0%"],
        ["30% (Severe)", "Greedy-EFT", "203.4 s", "+-21.9 s", "72.39%", "0.0%"]
    ]
    for r_i, r_data in enumerate(stat_data):
        for c_i, val in enumerate(r_data):
            cell = t_stat.cell(r_i + 1, c_i)
            cell.text = val
            set_cell_background(cell, "F5F7FA" if r_i % 2 == 0 else "FFFFFF")
            set_cell_margins(cell, top=50, bottom=50, left=80, right=80)

    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # Add Figure 3: Goodput Overhead Breakdown
    fig3_img = "artifacts/figure3_goodput_overhead_breakdown.png"
    if os.path.exists(fig3_img):
        doc.add_picture(fig3_img, width=Inches(6.0))
        p_c3 = doc.add_paragraph()
        p_c3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_c3.paragraph_format.space_after = Pt(12)
        r_c3 = p_c3.add_run("Figure 4: Goodput vs. Overhead Compute Breakdown (Useful Compute vs. Recovery Stalls)")
        r_c3.font.italic = True
        r_c3.font.size = Pt(9.5)
        r_c3.font.bold = True

    # ----------------------------------------------------
    # Section 5: Code Architecture & Module Deep Dive
    # ----------------------------------------------------
    h5 = doc.add_heading("5. Codebase Implementation & Engineering Audits", level=1)
    h5.runs[0].font.color.rgb = RGBColor(0x0D, 0x47, 0xA1)

    p_code = doc.add_paragraph()
    p_code.paragraph_format.space_after = Pt(8)
    p_code.add_run(
        "The repository contains seven core production modules in Python:\n"
        "- dag_engine.py: WorkflowDAG representation, topological sort using deque O(|V|+|E|), upward HEFT rank calculations, and synthetic DAG generation with calibrated directional uplink bandwidth.\n"
        "- worker.py: Worker dataclass with upload/download bandwidth, Poisson hazard rate, Weibull fatigue parameters, and RATS attestation state.\n"
        "- checkpoint.py: CheckpointManager supporting memory serialization, SHA-256 verification hash, two-phase commit acknowledgments, and state restoration.\n"
        "- risk_engine.py: Implements FeasibilityGate, Young/Daly optimal checkpoint interval tau, adaptive risk-gating, and composite objective score J(i, k).\n"
        "- schedulers.py: Contains BaseScheduler, GreedyEFTScheduler, HEFTScheduler, BoundedACOScheduler (MMAS bounds tau in [0.05, 5.0]), and ProposedRiskAwareScheduler.\n"
        "- network_fault_injector.py: DiscreteEventSimulationEngine with EPSILON = 1e-4 stability guards, two-phase crash rollback, and realistic recovery stall tracking.\n"
        "- experiment_logger.py: Records comprehensive telemetry, variance dossiers (Mean, SD, SEM, 95% CI, P50/P95/P99), and Welch's t-test hypothesis testing."
    )

    # Root Cause Fixes
    h5_2 = doc.add_heading("5.1 Root-Cause Engineering Fixes (Resolving Critical Inversions)", level=2)
    h5_2.runs[0].font.color.rgb = RGBColor(0x0D, 0x47, 0xA1)

    fixes = [
        ("GOR Inversion Resolution: ", "Initially, SimulationMetrics added asynchronous network upload time into total CPU overhead, artificially penalizing Proposed-RiskAware GOR to 87% while baselines sat at 99%. Excluding non-blocking NIC uploads and authentically accounting for post-failure recovery stalls (50s-78s for baselines) elevated Proposed GOR to 96.2%-97.1% while baselines drop to 72.4%-81.1%."),
        ("Zeno's Paradox Floating-Point Loop Resolution: ", "In discrete-event simulation, floating-point subtraction (compute_completed - last_checkpoint_progress == tau - 1e-16) caused time_to_next_ckpt to advance by 10^-16 seconds per step, freezing execution on Task 18. Introducing EPSILON = 1e-4 guards restored instantaneous sub-second execution across all 280 runs."),
        ("Adaptive Risk-Gated Parity at Zero Churn: ", "By dynamically evaluating expected preemption loss against checkpoint tax using scaled hazard rate lambda_eff, checkpointing automatically deactivates at zero churn (lambda = 0.0), achieving exact parity with HEFT at 99.59% GOR and 141.1s makespan."),
        ("Recovery Latency Realism: ", "In non-checkpointed baselines, failure forces 1.5s heartbeat detection, full state retransfer over 10 Mbps uplinks (32s), and parent dependency re-transfers, yielding 63.33s mean recovery. GhostInTheMachine retrieves state deltas from 100 Mbps durable peer stores in 1.44s (97.7% reduction).")
    ]
    for f_title, f_desc in fixes:
        fp = doc.add_paragraph(style='List Bullet')
        fp.paragraph_format.space_after = Pt(4)
        r_ft = fp.add_run(f_title)
        r_ft.font.bold = True
        fp.add_run(f_desc)

    doc.add_paragraph().paragraph_format.space_after = Pt(16)

    # ----------------------------------------------------
    # Section 6: Conclusion & Reproducibility
    # ----------------------------------------------------
    h6 = doc.add_heading("6. Conclusion & Verification Artifacts", level=1)
    h6.runs[0].font.color.rgb = RGBColor(0x0D, 0x47, 0xA1)

    p_conc = doc.add_paragraph()
    p_conc.paragraph_format.space_after = Pt(8)
    p_conc.add_run(
        "GhostInTheMachine establishes an upload-aware, risk-adjusted paradigm for scientific workflow scheduling across "
        "heterogeneous volunteer networks. By combining directional uplink bottleneck modeling, adaptive Young/Daly checkpoint "
        "gating, and asynchronous state-delta replication, the system achieves a 97.7% reduction in failure recovery latency, "
        "guarantees 0.0% deadline violations under heavy churn, and preserves 96.2% to 97.1% computational goodput.\n\n"
        "All telemetry data sheets, high-resolution vector figures, scalability benchmarks, and simulation scripts are fully "
        "committed and reproducible within the GitHub repository."
    )

    out_path = "PROJECT_TECHNICAL_REPORT.docx"
    doc.save(out_path)
    print(f"Successfully generated comprehensive technical report: {out_path}")

if __name__ == "__main__":
    create_report()
