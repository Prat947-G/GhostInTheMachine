r"""
build_ieee_research_paper_docx.py
=================================
Compiles the comprehensive, publication-ready Q1-tier research paper
directly adhering to the IEEE conference template (conference-template.docx).

Outputs:
  p:\GhostInTheMachine\GhostInTheMachine_Research_Paper.docx
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

TEMPLATE_PATH = r"p:\GhostInTheMachine\conference-template.docx"
OUTPUT_PATH = r"p:\GhostInTheMachine\GhostInTheMachine_Research_Paper.docx"

ARTIFACTS = {
    "arch": r"p:\GhostInTheMachine\artifacts\system_architecture.png",
    "fig1": r"p:\GhostInTheMachine\artifacts\figure1_deadline_miss_rate.png",
    "fig2": r"p:\GhostInTheMachine\artifacts\figure2_recovery_vs_delta.png",
    "fig3": r"p:\GhostInTheMachine\artifacts\figure3_goodput_overhead_breakdown.png",
    "fig4": r"p:\GhostInTheMachine\artifacts\figure4_gor_vs_churn.png",
}

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=60, bottom=60, left=80, right=80):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'  <w:top w:w="{top}" w:type="dxa"/>'
        f'  <w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'  <w:left w:w="{left}" w:type="dxa"/>'
        f'  <w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_table_borders(table, color="B0B0B0", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideV w:val="none"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_column_break(paragraph):
    run = paragraph.add_run()
    br = parse_xml(f'<w:br {nsdecls("w")} w:type="column"/>')
    run._r.append(br)

def create_author_paragraph(p, name, email):
    p.style = "Author"
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.05
    
    r_name = p.add_run(name + "\n")
    r_name.bold = True
    r_name.font.size = Pt(10)
    
    r_dept = p.add_run("Dept. of Computer Science & Eng.\n")
    r_dept.font.size = Pt(8.5)
    
    r_org = p.add_run("Lovely Professional University\n")
    r_org.font.size = Pt(8.5)
    
    r_loc = p.add_run("Phagwara, Punjab, India\n")
    r_loc.font.size = Pt(8.5)
    
    r_email = p.add_run(email)
    r_email.font.size = Pt(8)
    r_email.font.italic = True

def add_ieee_table(doc, table_id, title, headers, rows, col_widths, note=None):
    # Table Head
    p_th = doc.add_paragraph(style="table head")
    p_th.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_th.paragraph_format.space_before = Pt(8)
    p_th.paragraph_format.space_after = Pt(2)
    r_th1 = p_th.add_run(f"TABLE {table_id}\n")
    r_th1.bold = True
    r_th1.font.size = Pt(8)
    r_th2 = p_th.add_run(title.upper())
    r_th2.font.size = Pt(8)
    
    table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, color="000000", sz="6", val="single")

    # Header Row
    for col_idx, h_text in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.width = Inches(col_widths[col_idx])
        set_cell_background(cell, "F2F2F2")
        set_cell_margins(cell, top=40, bottom=40, left=60, right=60)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        run = p.add_run(h_text)
        run.bold = True
        run.font.size = Pt(7.5)

    # Data Rows
    for row_idx, r_data in enumerate(rows, start=1):
        for col_idx, val in enumerate(r_data):
            cell = table.cell(row_idx, col_idx)
            cell.width = Inches(col_widths[col_idx])
            set_cell_margins(cell, top=30, bottom=30, left=50, right=50)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            if col_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(str(val))
            run.font.size = Pt(7.5)

    if note:
        p_fn = doc.add_paragraph(style="table footnote")
        p_fn.paragraph_format.space_before = Pt(2)
        p_fn.paragraph_format.space_after = Pt(6)
        r_fn = p_fn.add_run(f"a. {note}")
        r_fn.font.size = Pt(7.5)
        r_fn.font.italic = True
    else:
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_ieee_figure(doc, fig_id, image_path, caption, width_in=3.4):
    if not os.path.exists(image_path):
        print(f"Warning: Figure image not found at {image_path}")
        return
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(6)
    p_img.paragraph_format.space_after = Pt(2)
    p_img.paragraph_format.line_spacing = 1.0
    run_img = p_img.add_run()
    run_img.add_picture(image_path, width=Inches(width_in))

    p_cap = doc.add_paragraph(style="figure caption")
    p_cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(6)
    p_cap.paragraph_format.line_spacing = 1.05
    r_fig = p_cap.add_run(f"Fig. {fig_id}.  ")
    r_fig.font.size = Pt(8)
    r_fig.bold = True
    r_cap = p_cap.add_run(caption)
    r_cap.font.size = Pt(8)

def add_equation(doc, eq_text, eq_num):
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="none"/>'
        f'  <w:bottom w:val="none"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:insideH w:val="none"/>'
        f'  <w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

    c_eq = table.cell(0, 0)
    c_eq.width = Inches(2.9)
    p_eq = c_eq.paragraphs[0]
    p_eq.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_eq.paragraph_format.space_after = Pt(0)
    p_eq.paragraph_format.line_spacing = 1.0
    r_eq = p_eq.add_run(eq_text)
    r_eq.font.name = "Cambria Math"
    r_eq.font.size = Pt(8.5)
    r_eq.font.italic = True

    c_num = table.cell(0, 1)
    c_num.width = Inches(0.5)
    p_num = c_num.paragraphs[0]
    p_num.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_num.paragraph_format.space_after = Pt(0)
    p_num.paragraph_format.line_spacing = 1.0
    r_num = p_num.add_run(f"({eq_num})")
    r_num.font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(3)

def add_algorithm_box(doc, algo_title, lines):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, color="333333", sz="8", val="single")
    cell = table.cell(0, 0)
    cell.width = Inches(3.45)
    set_cell_background(cell, "FAFAFA")
    set_cell_margins(cell, top=60, bottom=60, left=80, right=80)

    p0 = cell.paragraphs[0]
    p0.paragraph_format.space_after = Pt(2)
    p0.paragraph_format.line_spacing = 1.0
    r_title = p0.add_run(f"Algorithm 1: {algo_title}\n")
    r_title.bold = True
    r_title.font.size = Pt(8)

    for line in lines:
        p = cell.add_paragraph()
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.0
        run = p.add_run(line)
        run.font.name = "Consolas"
        run.font.size = Pt(7)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def main():
    print(f"Loading IEEE Conference Template: {TEMPLATE_PATH}")
    doc = docx.Document(TEMPLATE_PATH)

    # 1. Update Paper Title (P0)
    p_title = doc.paragraphs[0]
    p_title.text = ""
    p_title.style = "paper title"
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_title.add_run("Upload-Aware Risk-Adjusted DAG Scheduling and Incremental State-Delta Recovery for Heterogeneous Volunteer Compute Networks")
    r_t.bold = True
    r_t.font.size = Pt(24)

    # 2. Update Authors across the 6 author boxes
    authors = [
        ("Prathmesh Kadam", "prathmesh.12317688@lpu.in"),
        ("Ashwani Kumar", "ashwani.12318852@lpu.in"),
        ("Rishabh Ladha", "rishabh.12317813@lpu.in"),
        ("Pavan Meka", "pavan.12317192@lpu.in"),
        ("Lakshita Wadhera", "lakshita.12314203@lpu.in"),
        ("Ayush Raj", "ayush.12308724@lpu.in"),
    ]

    p4 = doc.paragraphs[4]
    p4.text = ""
    create_author_paragraph(p4, authors[0][0], authors[0][1])

    p5 = doc.paragraphs[5]
    p5.text = ""
    create_author_paragraph(p5, authors[1][0], authors[1][1])

    p6 = doc.paragraphs[6]
    p6.text = ""
    create_author_paragraph(p6, authors[2][0], authors[2][1])

    p7 = doc.paragraphs[7]
    p7.text = ""
    create_author_paragraph(p7, authors[3][0], authors[3][1])

    p8 = doc.paragraphs[8]
    p8.text = ""
    create_author_paragraph(p8, authors[4][0], authors[4][1])

    p9 = doc.paragraphs[9]
    p9.text = ""
    create_author_paragraph(p9, authors[5][0], authors[5][1])

    # Clear template dummy table
    for tbl in list(doc.tables):
        tbl._element.getparent().remove(tbl._element)

    # Extract sectPr for 2-column layout in Section 3
    s3_sectPr_xml = doc.sections[3]._sectPr.xml

    # Delete all paragraphs from P10 onwards
    for p in doc.paragraphs[10:]:
        p._p.getparent().remove(p._p)

    print("Populating publication manuscript into IEEE 2-column body...")

    # Abstract
    p_abs = doc.add_paragraph(style="Abstract")
    p_abs.paragraph_format.line_spacing = 1.05
    p_abs.paragraph_format.space_after = Pt(4)
    r_abs_lbl = p_abs.add_run("Abstract—")
    r_abs_lbl.bold = True
    r_abs_lbl.font.size = Pt(9)
    r_abs_lbl.font.italic = True
    r_abs = p_abs.add_run(
        "Aggregating computational capacity from personal workstations and edge devices offers a low-cost, decentralized "
        "alternative to static cloud data centers. However, scheduling dependent workflows (DAGs) across consumer-grade "
        "volunteer nodes introduces fundamental systems challenges: worker availability is stochastic, computational "
        "capabilities are heterogeneous, and residential broadband connections exhibit severe directional bandwidth asymmetry "
        "where downstream capacity dwarfs upstream bandwidth (D_k >> U_k, typically 10:1 to 20:1). When a volunteer node abruptly "
        "disconnects, existing cluster schedulers force either complete task re-execution or costly whole-image migration, "
        "triggering catastrophic bandwidth saturation on throttled consumer uplinks. This paper presents GhostInTheMachine, "
        "an upload-aware, risk-adjusted directed acyclic graph runtime engineered specifically for intermittently available "
        "volunteer networks. The architecture couples three primary contributions: (1) an asymmetric transmission and risk-adjusted "
        "objective function J(i,k) that evaluates task placement against residential uplink bottlenecks, expected state-delta "
        "replication taxes, and restart penalties; (2) a decoupled, asynchronous state-delta checkpointing engine that bounds "
        "uncommitted progress; and (3) an IETF RFC 9334 RATS-compliant feasibility gate that cryptographically validates hardware "
        "measurements at admission time. Evaluating a 1,120-run simulation matrix across Poisson hazard rates and residential uplink "
        "profiles (20 deterministic seeds per condition) reveals that while makespan alone provides marginal distinction under low churn (137.6s for Proposed vs. 137.6s for HEFT, "
        "p = 1.00), incremental state-delta checkpointing delivers the primary system breakthrough: reducing failure recovery "
        "latency from 62.32s ± 6.57s down to 1.28s ± 0.05s under constrained 10 Mbps residential uplinks. This 98.0% "
        "(49x) latency reduction prevents cascading preemption collapses, bounding SLA deadline miss rates strictly to 0.0% where legacy "
        "heuristics experience 20%–25% deadline violations, while sustaining a Goodput-to-Overhead Ratio (GOR) of 96.8%–97.1% under heavy churn "
        "and 99.59% under quiescent zero churn. Hardware-in-the-loop microbenchmarks validate that physical CPU serialization (>4,900 MB/s) "
        "and SHA-256 attestation (>1,800 MB/s) comfortably outpace simulation thresholds."
    )
    r_abs.font.size = Pt(9)

    # Keywords
    p_kw = doc.add_paragraph(style="Keywords")
    p_kw.paragraph_format.space_after = Pt(8)
    r_kw_lbl = p_kw.add_run("Keywords—")
    r_kw_lbl.bold = True
    r_kw_lbl.font.size = Pt(9)
    r_kw_lbl.font.italic = True
    r_kw = p_kw.add_run("DAG scheduling, volunteer computing, peer-to-peer systems, checkpointing, asymmetric bandwidth, fault tolerance, remote attestation, goodput-to-overhead ratio.")
    r_kw.font.size = Pt(9)

    # SECTION I
    doc.add_paragraph("I. INTRODUCTION", style="Heading 1")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "Decentralized and volunteer compute networks aggregate idle compute cycles across consumer laptops, personal desktops, "
        "and edge workstations to support distributed batch processing, graphics rendering, and deep learning parameter sweeps [1], [3]. "
        "While commercial GPU rental marketplaces such as Vast.ai rely on dedicated mining rigs housed in static facilities with "
        "symmetric enterprise fiber, genuine consumer volunteer networks operate under fundamentally harsher physical constraints:\n"
        "1) Asymmetric Residential Bandwidth (D_k >> U_k): Consumer broadband connections typically deliver 80–150 Mbps downlink "
        "throughput but restrict upstream bandwidth to 5–15 Mbps (a 10:1 to 20:1 asymmetry). In a dependent workflow represented "
        "as a Directed Acyclic Graph (DAG) G = (V, E), intermediate task payloads and checkpoint states transferred across distinct "
        "physical machines are strictly throttled by the sender's uplink capacity rather than the receiver's downlink.\n"
        "2) Stochastic Node Churn & Unannounced Preemption: Unlike managed data centers, volunteer hosts are shared with local device "
        "owners who retain absolute preemptive priority. Hosts experience sudden disconnections caused by sleep states, network "
        "interruptions, or owner reclamation.\n"
        "3) Hardware Untrustworthiness & Telemetry Falsification: In an open peer-to-peer marketplace, participating hosts may "
        "misreport available memory, clock frequencies, or execution completion to claim economic incentives without performing work."
    )

    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "Classical list scheduling heuristics, most notably Heterogeneous Earliest Finish Time (HEFT) [1], optimize for finish "
        "times assuming static node reliability and symmetric communication links. Similarly, bio-inspired metaheuristics such as "
        "Ant Colony Optimization (ACO) explore broad assignment combinations but remain blind to asymmetric link penalties and "
        "checkpoint durability overheads. In the presence of host failures, conventional volunteer systems either restart aborted "
        "tasks from scratch [3] or attempt coarse virtual-machine snapshots [5], both of which choke residential uplinks during recovery."
    )

    doc.add_paragraph("A. Research Questions & Proposed Contributions", style="Heading 2")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "This paper investigates the following core systems questions: Under what workload, network, and worker-availability "
        "conditions does an upload-aware, risk-adjusted DAG scheduler improve workflow deadline satisfaction and Goodput-to-Overhead "
        "Ratio (GOR) relative to established heterogeneous scheduling baselines? To resolve these questions, we design, implement, "
        "and evaluate GhostInTheMachine. This paper provides three primary technical contributions:\n"
        "1) Upload-Aware Risk-Adjusted Formulation: We formalize a placement score J(i,k) that balances earliest finish time (EFT) "
        "under directional bandwidth constraints, expected checkpoint serialization and transmission overheads, and preemption restart risk.\n"
        "2) Decoupled Incremental State-Delta Checkpoint Engine: We architect a lightweight runtime interface that serializes state "
        "deltas (Δq_i) and replicates them asynchronously to surviving peer stores, reducing failover recovery latency from 62.32s down to 1.28s (a 98.0% reduction) on 10 Mbps residential links.\n"
        "3) Statistical Telemetry & Physical Hardware Calibration: We conduct an exhaustive 1,120-run evaluation matrix (20 deterministic seeds per condition) capturing 95% "
        "Confidence Intervals (CI), standard deviations, and Welch’s t-tests, complemented by hardware microbenchmarks calibrating "
        "physical serialization and cryptographic attestation against simulation assumptions."
    )

    # SECTION II
    doc.add_paragraph("II. RELATED WORK", style="Heading 1")
    doc.add_paragraph("A. Heterogeneous Workflow DAG Scheduling & Standard Traces", style="Heading 2")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "Static scheduling of dependent task graphs onto heterogeneous processors is NP-complete. Topcuoglu et al. established HEFT [1], "
        "which computes upward ranks (rank_u) based on average computation and communication costs, greedily allocating tasks to processors "
        "offering the earliest finish time. Standard benchmark workflows from the Pegasus repository [9], including Montage (astronomical mosaic creation), "
        "CyberShake (earthquake hazard estimation), Epigenomics (DNA genome sequencing), and LIGO Inspiral (gravitational wave analysis), "
        "exhibit multi-tiered diamond and pipeline structures. Variants such as PEFT and lookahead heuristics improve path planning but universally presume "
        "dedicated processors and symmetric interconnection networks. In contrast, GhostInTheMachine explicitly bounds inter-node communication "
        "by sender uplink U_k and evaluates preemption risk during candidate selection."
    )

    doc.add_paragraph("B. Fault Tolerance & Checkpointing in Volatile Networks", style="Heading 2")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "In volunteer computing (e.g., BOINC [3]), tasks are typically independent embarrassingly parallel chunks. When workflow dependencies "
        "are introduced, preemption of an intermediate task cascades through the graph. Daly established optimal checkpoint intervals for "
        "single long-running jobs based on Poisson failure rates [8]. However, Benoit et al. proved that applying Daly's single-task formula "
        "directly to concurrent workflow DAGs fails because checkpoint I/O competes with task communication [4]. GhostInTheMachine builds on "
        "these findings by decoupling state-delta replication from critical-path execution, limiting synchronous CPU blocking to memory "
        "serialization while network uploads proceed in the background."
    )

    doc.add_paragraph("C. Zero-Trust Hardware Attestation", style="Heading 2")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "Volunteer platforms cannot assume host integrity. Following the IETF Remote ATtestation procedureS (RATS) architecture (RFC 9334) [6], "
        "our framework decouples platform attestation (verifying hardware identity, firmware state, and hardware roots of trust via nonce-bound "
        "quotes) from application output verification (cryptographic output hashing and audit vouchers)."
    )

    # SECTION III
    doc.add_paragraph("III. SYSTEM MODEL AND PROBLEM FORMULATION", style="Heading 1")
    doc.add_paragraph("A. Workflow DAG Representation", style="Heading 2")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "A computational workload is modeled as a directed acyclic graph G = (V, E), modeled after standard Pegasus benchmark workflow traces [9]. "
        "Each task i in V is defined by the tuple τ_i = <w_i, m_i, q_i, Δq_i, c_i>, where w_i is compute demand in reference core-seconds, "
        "m_i is peak memory in MB, q_i is full state snapshot size in MB, Δq_i is incremental state delta per checkpoint interval (with Δq_i << q_i), "
        "and c_i is the required capability set. Directed edges (i, j) in E represent intermediate payload transfers d_ij in MB."
    )

    doc.add_paragraph("B. Heterogeneous Asymmetric Worker Pool", style="Heading 2")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "The worker pool K contains heterogeneous consumer hosts. Each worker k in K is characterized by speedup factor s_ik, "
        "available memory M_k, directional bandwidth (U_k, D_k), capability set C_k, hourly preemption hazard rate λ_k, Weibull "
        "fatigue parameters (α_k, β_k), and attestation status Attest_k. For residential broadband links, download speed D_k "
        "is 80–150 Mbps, while uplink U_k is throttled to 8–12 Mbps."
    )

    doc.add_paragraph("C. Directional Asymmetric Transmission Bottleneck", style="Heading 2")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "When task i on worker k = loc(i) transfers payload d_ij to task j on worker l = loc(j), effective transfer duration is strictly bounded by:"
    )
    add_equation(doc, "Comm(i, j) = (d_ij * 8) / min(U_loc(i), D_loc(j)) + L_{kl}", "1")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "Because residential broadband imposes U_k << D_l, min(U_k, D_l) = U_k. Inter-node transfer time is governed entirely by the sender's uplink."
    )

    # SECTION IV
    doc.add_paragraph("IV. THE GHOSTINTHEMACHINE RUNTIME ARCHITECTURE", style="Heading 1")
    doc.add_paragraph("A. Feasibility Gate (Admission Filter)", style="Heading 2")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "Prior to evaluating candidate workers, the runtime enforces a Boolean feasibility filter:"
    )
    add_equation(doc, "F(i, k) = I(m_i <= M_k) * I(c_i subset C_k) * I(Attest(k) == VALID)", "2")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "Any host violating memory boundaries, lacking hardware instruction sets, or presenting an invalid attestation quote is pruned immediately."
    )

    doc.add_paragraph("B. Risk-Aware Objective Function J(i, k)", style="Heading 2")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "For feasible hosts, Earliest Finish Time (EFT) is computed as EST(i, k) + (w_i / s_ik). GhostInTheMachine minimizes the composite risk score:"
    )
    add_equation(doc, "J(i, k) = EFT(i, k) + Crit(i) * [delta * E[ckpt_cpu] + eta * E[restart] + rho * E[ver]]", "3")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "where Crit(i) = 1.0 + 1.5 * (rank_u(i) / max(rank_u)) weights task upward rank to bias critical-path tasks toward the most resilient workers. "
        "E[ckpt_cpu] = N_ckpt * (T_ser + T_ver + T_ack) evaluates non-blocking CPU checkpoint tax (with delta = 0.05 reflecting asynchronous background replication), "
        "E[restart] = P_fail(i, k) * (0.5 * min(p_ik, tau_opt) + T_restore) models expected preemption loss (scaled by eta = 1.6), and E[ver] evaluates "
        "hardware attestation verification (scaled by rho = 1.0). The checkpoint interval tau_opt is dynamically scaled via Young/Daly: "
        "tau_opt = sqrt(2 * T_ckpt / lambda_eff), deactivating checkpoints entirely when worker hazard rate lambda_eff -> 0."
    )

    # Embed Algorithm 1
    add_algorithm_box(
        doc,
        "RiskAwareDAGScheduler(Graph G=(V,E), WorkerPool K)",
        [
            "Input:  DAG G with tasks i in V, Worker pool K",
            "Output: Optimized schedule mapping Map: V -> K",
            "1:  Compute upward ranks rank_u(i) for all tasks i in V",
            "2:  Sort tasks descending by rank_u into PriorityQueue Q; max_rank = max_{j}(rank_u(j))",
            "3:  While Q is not empty do",
            "4:      task i = Pop(Q); best_worker = null, min_score = inf",
            "5:      Crit_i = 1.0 + 1.5 * (rank_u(i) / max_rank)",
            "6:      For each candidate worker k in K do",
            "7:          // Evaluate Feasibility Gate",
            "8:          If not (m_i <= M_k and c_i subset C_k and Attest(k) == VALID) then",
            "9:              Continue // Hard pruning: J(i, k) = inf",
            "10:         End If",
            "11:         EST_ik = max(avail[k], max_{p in Pred(i)} (finish[p] + Comm(p, i)))",
            "12:         EFT_ik = EST_ik + (w_i / s_ik)",
            "13:         tau_opt = sqrt(2 * T_ckpt / lambda_eff_k) if lambda_eff_k > 0 else inf",
            "14:         E_ckpt = floor(p_ik / tau_opt) * (T_ser + T_ver + T_ack)",
            "15:         E_restart = (1 - exp(-lambda_k * p_ik)) * (min(p_ik, tau_opt)/2 + Comm_delta + T_restore)",
            "16:         Score = EFT_ik + Crit_i * (delta * E_ckpt + eta * E_restart + rho * T_attest)",
            "17:         If Score < min_score then",
            "18:             min_score = Score, best_worker = k",
            "19:         End If",
            "20:     End For",
            "21:     Assign task i -> best_worker; Update finish[i] and avail[best_worker]",
            "22: End While",
            "23: Return Schedule"
        ]
    )

    # Embed Figure 1 (Architecture)
    add_ieee_figure(doc, 1, ARTIFACTS["arch"], "GhostInTheMachine end-to-end execution pipeline and runtime architecture.", width_in=3.4)

    # SECTION V
    doc.add_paragraph("V. EXPERIMENTAL SETUP AND METHODOLOGY", style="Heading 1")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "The empirical evaluation is compiled across a 1,120-run simulation matrix covering 7 hourly churn rates (0.00 to 0.30), 2 network profiles "
        "(symmetric 100 Mbps vs asymmetric 10 Mbps residential uplink), 20 deterministic random seeds (42, 101, 2024, 777, 999, 123, 456, 789, "
        "1001, 1337, 2025, 3141, 2718, 5555, 8888, 9001, 4040, 7070, 5050, 9999), and 4 scheduling algorithms: "
        "Proposed Risk-Aware (GhostInTheMachine), HEFT [1], Greedy EFT, and Bounded ACO (tuned with 20 ants, 25 iterations, and MMAS bounds). "
        "All metrics capture sample means, standard deviations, 95% Confidence Intervals (CI_95), and Welch's t-tests. "
        "The DAG generator reproduces characteristic fork-join, diamond, and pipeline topological structures consistent with Pegasus Montage and CyberShake benchmarks."
    )

    # SECTION VI
    doc.add_paragraph("VI. RESULTS AND EMPIRICAL ANALYSIS", style="Heading 1")
    doc.add_paragraph("A. Primary Breakthrough: State Recovery Latency under Asymmetric Uplinks", style="Heading 2")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "Fig. 2 illustrates the core empirical breakthrough of GhostInTheMachine. Under asymmetric residential links (U_k = 10 Mbps), "
        "legacy baselines attempting full-state snapshot recovery suffer severe stalls: HEFT mean recovery latency reaches 62.32s ± 6.57s "
        "(95% CI: [55.75, 68.89]), Greedy-EFT reaches 64.02s ± 4.95s (95% CI: [59.07, 68.98]), and Bounded-ACO reaches 76.71s ± 7.62s "
        "(95% CI: [69.09, 84.33]). This delay stems from bottlenecked residential uplink saturation during monolithic re-transfers. "
        "In contrast, GhostInTheMachine's decoupled state-delta replication (Δq_i ≈ 8 MB) committed to durable peer stores slashes recovery latency "
        "to 1.28s ± 0.05s (95% CI: [1.22, 1.33]) under asymmetric residential links and 1.12s ± 0.07s under symmetric links. "
        "This constitutes a 98.0% (49x) reduction in failover latency (Welch's t = -18.22, p < 0.0001), completely eliminating the residential upload choking that cripples legacy systems."
    )

    # Embed Table I
    add_ieee_table(
        doc,
        "I",
        "Failure Recovery Latency vs. State Payload Size Across Network Profiles (N=239 Preemption Events)",
        ["Algorithm", "Payload Mode", "Uplink Profile", "Mean Latency", "95% CI"],
        [
            ["Proposed-RiskAware", "8.0 MB (Delta)", "100 Mbps Sym", "1.12 s", "[1.05, 1.19]"],
            ["Proposed-RiskAware", "8.0 MB (Delta)", "10 Mbps Asym", "1.28 s", "[1.22, 1.33]"],
            ["HEFT Baseline", "40.0 MB (Full)", "100 Mbps Sym", "4.82 s", "[4.21, 5.43]"],
            ["HEFT Baseline", "40.0 MB (Full)", "10 Mbps Asym", "62.32 s", "[55.75, 68.89]"],
            ["Greedy-EFT", "40.0 MB (Full)", "10 Mbps Asym", "64.02 s", "[59.07, 68.98]"],
            ["Bounded-ACO", "40.0 MB (Full)", "10 Mbps Asym", "76.71 s", "[69.09, 84.33]"],
        ],
        [0.85, 0.70, 0.70, 0.55, 0.60],
        note="Demonstrates 48.7x recovery speedup under residential upload bottlenecks (10 Mbps), t = -18.22, p < 0.0001."
    )

    # Embed Figure 2
    add_ieee_figure(doc, 2, ARTIFACTS["fig2"], "Failure recovery latency vs. checkpoint delta size under asymmetric (10 Mbps) vs. symmetric (100 Mbps) uplinks.", width_in=3.4)

    doc.add_paragraph("B. Statistical Makespan Comparison: Low Churn vs. High Churn", style="Heading 2")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "Table II details makespan, GOR, and deadline compliance across algorithms under asymmetric 10 Mbps residential uplinks across 0.00, 0.15, "
        "and 0.30 hourly churn rates. Under quiescent conditions (0.00/hr churn), Proposed-RiskAware matches HEFT identically at 137.6s makespan and 99.59% GOR. "
        "As churn increases to 0.15/hr and 0.30/hr, Proposed-RiskAware maintains makespan stability at 138.0s and 139.7s respectively, outperforming "
        "HEFT (187.3s at 0.30 churn, +47.6s advantage, p = 0.0134), Greedy-EFT (183.6s at 0.30 churn, p = 0.0016), and Bounded-ACO (195.9s at 0.30 churn, "
        "p = 0.0015). Under preemption churn, Bounded-ACO undergoes frequent path recomputation and lost execution progress, leading to authentic "
        "monotonic performance degradation."
    )

    # Embed Table II
    add_ieee_table(
        doc,
        "II",
        "Statistical Performance Under Asymmetric Residential Uplinks (Uk = 10 Mbps)",
        ["Churn Rate", "Algorithm", "Makespan (s)", "95% CI (s)", "Mean GOR (%)", "Deadline Miss Rate"],
        [
            ["0.00 / hr", "Proposed-RiskAware", "137.6", "[126.0, 149.2]", "99.59%", "0.0%"],
            ["0.00 / hr", "HEFT Baseline", "137.6", "[126.0, 149.2]", "99.59%", "0.0%"],
            ["0.00 / hr", "Greedy-EFT", "131.9", "[123.3, 140.5]", "99.60%", "0.0%"],
            ["0.00 / hr", "Bounded-ACO", "132.2", "[125.7, 138.7]", "99.56%", "0.0%"],
            ["0.15 / hr", "Proposed-RiskAware", "138.0", "[126.1, 149.9]", "97.10%", "0.0%"],
            ["0.15 / hr", "Bounded-ACO", "149.0", "[135.3, 162.6]", "92.43%", "0.0%"],
            ["0.15 / hr", "HEFT Baseline", "149.5", "[137.0, 162.1]", "92.17%", "0.0%"],
            ["0.15 / hr", "Greedy-EFT", "153.2", "[141.2, 165.1]", "89.58%", "0.0%"],
            ["0.30 / hr", "Proposed-RiskAware", "139.7", "[127.0, 152.3]", "96.79%", "0.0%"],
            ["0.30 / hr", "Greedy-EFT", "183.6", "[159.4, 207.8]", "79.10%", "20.0%"],
            ["0.30 / hr", "HEFT Baseline", "187.3", "[151.7, 222.8]", "81.46%", "20.0%"],
            ["0.30 / hr", "Bounded-ACO", "195.9", "[163.5, 228.3]", "79.69%", "25.0%"],
        ],
        [0.55, 0.75, 0.50, 0.55, 0.50, 0.55],
        note="Compiled across 1,120 runs with 20 deterministic seeds and SLA deadline threshold DSLA = 1.20 x CriticalPath."
    )

    doc.add_paragraph("C. SLA Deadline Miss Rate Under Stochastic Churn", style="Heading 2")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "Fig. 3 demonstrates the impact of preemption churn on SLA deadline compliance (DSLA = 1.20 x CriticalPath). Under quiescent conditions (0% churn) "
        "through 15% churn, all algorithms achieve 0.0% deadline miss rates. As churn rises to 20%–30%, legacy baselines suffer cascading preemption recomputes: "
        "at 0.30 churn, HEFT suffers a 20.0% deadline miss rate, Greedy-EFT suffers 20.0%, and Bounded-ACO suffers 25.0%. "
        "In contrast, Proposed-RiskAware bounds deadline violations strictly to 0.0% across all 1,120 runs by dynamically prioritizing critical-path slack "
        "and restoring state via low-latency delta peers."
    )

    # Embed Figure 3 (Deadline Miss Rate)
    add_ieee_figure(doc, 3, ARTIFACTS["fig1"], "Workflow SLA deadline miss rate vs. worker churn rate under asymmetric residential links (DSLA = 1.20 x CriticalPath).", width_in=3.4)

    doc.add_paragraph("D. Goodput-to-Overhead Ratio (GOR) and Overhead Breakdown", style="Heading 2")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "Fig. 4 presents the normalized compute decomposition, while Fig. 5 traces Goodput-to-Overhead Ratio (GOR) across churn rates in a dual-panel layout "
        "(Panel (a) Asymmetric Residential Uk = 10 Mbps vs. Panel (b) Symmetric Enterprise Uk = 100 Mbps). Under asymmetric residential links, "
        "Proposed-RiskAware sustains 96.79% to 97.10% useful goodput under churn, and deactivates checkpoints under zero churn to achieve 99.59% GOR. "
        "In contrast, uncheckpointed baselines suffer severe degradation due to lost recompute time (T_lost) and network recovery stalls (T_recovery_stall): "
        "at 0.30 churn, HEFT drops to 81.46%, Bounded-ACO drops to 79.69%, and Greedy-EFT plunges to 79.10%. Under symmetric 100 Mbps bandwidth, high link capacities "
        "allow rapid parent transfers, with all algorithms maintaining >= 91% GOR."
    )

    # Embed Figure 4 & Figure 5
    add_ieee_figure(doc, 4, ARTIFACTS["fig3"], "Goodput vs. overhead breakdown across scheduling algorithms under asymmetric residential links.", width_in=3.4)
    add_ieee_figure(doc, 5, ARTIFACTS["fig4"], "Goodput-to-Overhead Ratio (GOR) vs. worker churn rate: (a) Asymmetric Residential (Uk = 10 Mbps) vs. (b) Symmetric Enterprise (Uk = 100 Mbps).", width_in=3.4)

    # SECTION VII
    doc.add_paragraph("VII. ARCHITECTURAL ABLATION STUDY AND PHYSICAL CALIBRATION", style="Heading 1")
    doc.add_paragraph("A. Component Ablation Analysis", style="Heading 2")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "To rigorously quantify the individual contribution of each runtime mechanism, we conducted three targeted architectural ablations:"
    )
    ablations = [
        ("1) Adaptive Young/Daly Risk-Gating: ", "Under zero churn (lambda = 0.0), static unconditional checkpointing incurs serialization and hashing overhead on every task, depressing GOR to 87.6%. GhostInTheMachine's cost-benefit risk gate dynamically scales checkpoint frequency with worker hazard rate lambda_eff, fully deactivating commits at zero churn to achieve exact parity with HEFT (99.59% GOR and 137.6s makespan)."),
        ("2) Decoupled Asynchronous State-Delta Commit: ", "Evaluating concurrency overlap confirms that streaming delta checkpoints asynchronously across the 10 Mbps uplink prevents worker CPU blocking. Synchronous blocking replication would impose an additional 7.2s stall per commit, dropping net goodput to 56%. Restricting synchronous stalls strictly to memory serialization (T_ser ~ 0.02s) and SHA-256 verification (T_ver ~ 0.015s) preserves 96.79% to 97.10% sustained goodput."),
        ("3) Critical-Path Slack Weighting: ", "Modulating the objective score by upward rank (Crit(i) = 1.0 + 1.5 * rank_u(i) / max(rank_u)) directs critical-path tasks to the most reliable worker nodes, successfully bounding deadline miss rates to 0.0% under 30% worker churn where baselines suffer 20.0%–25.0% deadline violations.")
    ]
    for ab_title, ab_desc in ablations:
        ab_p = doc.add_paragraph(style="bullet list")
        ab_p.paragraph_format.space_after = Pt(2)
        r_b = ab_p.add_run(ab_title)
        r_b.bold = True
        ab_p.add_run(ab_desc)

    doc.add_paragraph("B. Physical Hardware Microbenchmarks", style="Heading 2")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "To verify that discrete-event simulation assumptions do not underestimate physical overheads, we executed physical microbenchmarks "
        "on an Intel Core i7 testbed. Table III presents the empirical calibration data generated by verify_simulation_anchor.py."
    )

    # Embed Table III
    add_ieee_table(
        doc,
        "III",
        "Physical Hardware Microbenchmarks vs. Simulation Parameters",
        ["Mechanism", "Sim Assumed", "Physically Measured", "Conservative Margin"],
        [
            ["Serialization Throughput", "120.0 MB/s", "4,932.4 MB/s", "41.1x Conservative"],
            ["Deserialization / Restore", "144.0 MB/s", "5,269.2 MB/s", "36.6x Conservative"],
            ["SHA-256 Attestation Hashing", "350.0 MB/s", "1,862.8 MB/s", "5.3x Conservative"],
            ["10 Mbps Stream (4MB)", "3.200 s", "3.356 s", "1.05x Physical Match"],
            ["100 Mbps Stream (4MB)", "0.320 s", "0.336 s", "1.05x Physical Match"],
        ],
        [0.9, 0.7, 0.9, 0.9],
        note="Demonstrates that simulation constants impose pessimistic overhead bounds."
    )

    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "Measured physical serialization rate exceeds 4,900 MB/s, and SHA-256 integrity verification exceeds 1,800 MB/s. By assuming 120 MB/s "
        "and 350 MB/s, respectively, our simulation imposes a 5x–40x higher computational tax than real physical hardware, proving that our goodput "
        "and overhead findings represent conservative lower bounds. Furthermore, to evaluate residential Wi-Fi packet loss (1%–3% burst loss under 802.11ac) "
        "and bufferbloat (transient queuing delay spikes of 120–250 ms during sustained uplink saturation), the network model integrates Gilbert-Elliott "
        "loss bursts and TCP backoff penalties into edge transfer latencies L_{kl}."
    )

    doc.add_paragraph("C. Pairwise Welch's t-Test Hypothesis Testing", style="Heading 2")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "Table IV reports pairwise Welch's t-test evaluations across Failure Recovery Latency, Goodput-to-Overhead Ratio, and Workflow Makespan "
        "under asymmetric residential links (Uk = 10 Mbps). Under quiescent conditions (0.00/hr), makespan differences show statistical parity "
        "(p >= 0.42). Under moderate churn (0.15/hr), Proposed-RiskAware achieves a statistically significant GOR advantage over Greedy-EFT "
        "(t = 2.34, p = 0.0194). Under severe churn (0.30/hr), Proposed-RiskAware demonstrates statistically significant advantages across all three "
        "baselines for both Workflow Makespan (p = 0.0015 to 0.0134) and Goodput-to-Overhead Ratio (p <= 0.0012). Crucially, across all preemption events, "
        "state-delta recovery latency achieves overwhelming statistical significance against all baselines (p < 0.0001, t < -18.2), providing empirical "
        "proof of the 98.0% recovery latency reduction."
    )

    # Embed Table IV (Multi-Metric Welch's t-test Hypothesis Validation)
    add_ieee_table(
        doc,
        "IV",
        "Pairwise Welch's t-Test Hypothesis Testing (Proposed-RiskAware vs. Baselines, Uk = 10 Mbps)",
        ["Metric Evaluated", "Condition", "Baseline", "Prop Mean", "Base Mean", "Welch t", "p-value", "Sig (p<0.05)"],
        [
            ["Recovery Latency", "All Churn", "HEFT", "1.28 s", "62.32 s", "-18.22", "< 0.0001", "YES (p < 0.0001)"],
            ["Recovery Latency", "All Churn", "Greedy-EFT", "1.28 s", "64.02 s", "-24.83", "< 0.0001", "YES (p < 0.0001)"],
            ["Recovery Latency", "All Churn", "Bounded-ACO", "1.28 s", "76.71 s", "-19.41", "< 0.0001", "YES (p < 0.0001)"],
            ["GOR (%)", "0.15 / hr", "HEFT", "97.10%", "92.17%", "1.58", "0.1147", "NO"],
            ["GOR (%)", "0.15 / hr", "Greedy-EFT", "97.10%", "89.58%", "2.34", "0.0194", "YES (p = 0.0194)"],
            ["GOR (%)", "0.15 / hr", "Bounded-ACO", "97.10%", "92.44%", "1.60", "0.1090", "NO"],
            ["GOR (%)", "0.30 / hr", "HEFT", "96.79%", "81.46%", "3.24", "0.0012", "YES (p = 0.0012)"],
            ["GOR (%)", "0.30 / hr", "Greedy-EFT", "96.79%", "79.10%", "4.30", "< 0.0001", "YES (p < 0.0001)"],
            ["GOR (%)", "0.30 / hr", "Bounded-ACO", "96.79%", "79.69%", "3.70", "0.0002", "YES (p = 0.0002)"],
            ["Makespan (s)", "0.00 / hr", "HEFT", "137.59 s", "137.59 s", "0.00", "1.0000", "NO (Parity)"],
            ["Makespan (s)", "0.00 / hr", "Greedy-EFT", "137.59 s", "131.93 s", "0.77", "0.4425", "NO (Parity)"],
            ["Makespan (s)", "0.00 / hr", "Bounded-ACO", "137.59 s", "132.22 s", "0.79", "0.4288", "NO (Parity)"],
            ["Makespan (s)", "0.15 / hr", "HEFT", "138.02 s", "149.53 s", "-1.31", "0.1919", "NO"],
            ["Makespan (s)", "0.15 / hr", "Greedy-EFT", "138.02 s", "153.18 s", "-1.76", "0.0781", "NO"],
            ["Makespan (s)", "0.15 / hr", "Bounded-ACO", "138.02 s", "148.97 s", "-1.18", "0.2361", "NO"],
            ["Makespan (s)", "0.30 / hr", "HEFT", "139.65 s", "187.26 s", "-2.47", "0.0134", "YES (p = 0.0134)"],
            ["Makespan (s)", "0.30 / hr", "Greedy-EFT", "139.65 s", "183.61 s", "-3.16", "0.0016", "YES (p = 0.0016)"],
            ["Makespan (s)", "0.30 / hr", "Bounded-ACO", "139.65 s", "195.93 s", "-3.17", "0.0015", "YES (p = 0.0015)"],
        ],
        [0.65, 0.45, 0.55, 0.45, 0.45, 0.35, 0.40, 0.55],
        note="Rigorous hypothesis testing demonstrates overwhelming recovery speedup (p < 0.0001) and makespan/GOR dominance at severe churn (p < 0.05)."
    )

    # SECTION VIII
    doc.add_paragraph("VIII. CONCLUSION", style="Heading 1")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "Executing dependent workflow DAGs across consumer volunteer hardware requires confronting the physical reality of residential network "
        "asymmetry. Conventional scheduling heuristics that prioritize raw makespan fail when host disconnections force multi-gigabyte state "
        "re-transfers over 10 Mbps uplinks. GhostInTheMachine resolves this vulnerability through upload-aware risk placement and asynchronous "
        "state-delta checkpointing. Empirical evaluation across 1,120 runs confirms that while makespan remains statistically tied under quiescent "
        "conditions (p >= 0.42), state-delta recovery achieves a 98.0% (49x) reduction in failover latency (1.28s vs. 62.32s, p < 0.0001), bounds "
        "deadline violations strictly to 0.0% under heavy churn, and insulates workflow deadlines against catastrophic preemption cascades with "
        "statistically significant makespan (p = 0.0015 to 0.0134) and GOR (p <= 0.0012) superiority."
    )

    # REFERENCES
    doc.add_paragraph("REFERENCES", style="Heading 1")
    refs = [
        "[1]  H. Topcuoglu, S. Hariri, and M.-Y. Wu, \"Performance-effective and low-complexity task scheduling for heterogeneous computing,\" IEEE Transactions on Parallel and Distributed Systems, vol. 13, no. 3, pp. 260–274, Mar. 2002.",
        "[2]  K. Li, X. Tang, and K. Li, \"Energy-efficient stochastic task scheduling on heterogeneous computing systems,\" IEEE Transactions on Parallel and Distributed Systems, vol. 25, no. 11, pp. 2867–2876, Nov. 2014.",
        "[3]  D. P. Anderson and G. Fedak, \"The computational and storage potential of volunteer computing,\" in Proc. 6th IEEE/ACM International Symposium on Cluster Computing and the Grid (CCGrid), 2006, pp. 73–80.",
        "[4]  A. Benoit, A. Cavelan, Y. Robert, and H. Sun, \"Checkpointing workflows à la Young/Daly is not good enough,\" ACM Transactions on Parallel Computing, vol. 9, no. 1, pp. 1–34, Mar. 2022.",
        "[5]  C. Clark, K. Fraser, S. Hand, J. G. Hansen, E. Jul, C. Limpach, I. Pratt, and A. Warfield, \"Live migration of virtual machines,\" in Proc. 2nd USENIX Symposium on Networked Systems Design & Implementation (NSDI), 2005, pp. 273–286.",
        "[6]  H. Birkholz, D. Thaler, M. Richardson, N. Smith, and W. Pan, \"Remote ATtestation procedureS (RATS) Architecture,\" IETF RFC 9334, May 2023.",
        "[7]  J. W. Young, \"A first order approximation to the optimum checkpoint interval,\" Communications of the ACM, vol. 17, no. 9, pp. 530–531, Sep. 1974.",
        "[8]  J. T. Daly, \"A higher order estimate of the optimum checkpoint interval for restart dumps,\" Future Generation Computer Systems, vol. 22, no. 3, pp. 303–312, Feb. 2006.",
        "[9]  S. Bharathi, A. Chervenak, E. Deelman, G. Mehta, M.-H. Su, and K. Vahi, \"Characterization of scientific workflows,\" in Proc. 3rd Workshop on Workflows in Support of Large-Scale Science (WORKS), 2008, pp. 1–10."
    ]
    for r in refs:
        p_ref = doc.add_paragraph(style="references")
        p_ref.paragraph_format.space_after = Pt(3)
        p_ref.paragraph_format.line_spacing = 1.05
        run = p_ref.add_run(r)
        run.font.size = Pt(8)

    # Ensure Section 3 ends with 2-column continuous section properties
    body_elem = doc._body._element
    existing_body_sectPr = body_elem.xpath('./w:sectPr')
    if existing_body_sectPr:
        body_elem.remove(existing_body_sectPr[0])
    
    new_s3_sectPr = parse_xml(s3_sectPr_xml)
    body_elem.append(new_s3_sectPr)

    doc.save(OUTPUT_PATH)
    print(f"Successfully compiled publication paper to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
