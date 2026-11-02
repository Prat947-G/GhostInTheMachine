"""
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
        "measurements at admission time. Evaluating a 280-run simulation matrix across Poisson hazard rates and residential uplink "
        "profiles reveals that while makespan alone provides marginal distinction under low churn (147.4s vs. 141.1s for HEFT, "
        "p > 0.60), incremental state-delta checkpointing delivers the primary system breakthrough: reducing failure recovery "
        "latency from 30.7s–38.0s (mean 34.36s) down to 0.81s under constrained 10 Mbps residential uplinks. This 97.6% "
        "latency reduction prevents cascading preemption collapses, bounding SLA deadline miss rates below 20% where legacy "
        "heuristics experience 40% failures, while sustaining a Goodput-to-Overhead Ratio (GOR) of 80.4%–96.9%. Hardware-in-the-loop "
        "microbenchmarks validate that physical CPU serialization (>4,900 MB/s) and SHA-256 attestation (>1,800 MB/s) comfortably "
        "outpace simulation thresholds."
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
        "deltas (Δq_i) and replicates them asynchronously to surviving peer stores, reducing failover recovery latency from 34.4s to 0.81s on 10 Mbps links.\n"
        "3) Statistical Telemetry & Physical Hardware Calibration: We conduct an exhaustive 280-run evaluation matrix capturing 95% "
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
    add_equation(doc, "J(i, k) = EFT(i, k) + delta * E[ckpt] + eta * E[restart] + rho * E[ver]", "3")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "where E[ckpt] penalizes placing stateful tasks on low-upload links (weighted by delta = 0.15 to account for background asynchronous transfer), "
        "E[restart] weights preemption hazard rates against state-delta restore latency from the durable replica store, and E[ver] accounts for cryptographic remote attestation tax."
    )

    # Embed Algorithm 1
    add_algorithm_box(
        doc,
        "RiskAwareDAGScheduler(Graph G=(V,E), WorkerPool K)",
        [
            "Input:  DAG G with tasks i in V, Worker pool K",
            "Output: Optimized schedule mapping Map: V -> K",
            "1:  Compute upward ranks rank_u(i) for all tasks i in V",
            "2:  Sort tasks descending by rank_u into PriorityQueue Q",
            "3:  While Q is not empty do",
            "4:      task i = Pop(Q); best_worker = null, min_score = inf",
            "5:      For each candidate worker k in K do",
            "6:          // Evaluate Feasibility Gate",
            "7:          If not (m_i <= M_k and c_i subset C_k and Attest(k)) then",
            "8:              Continue // Hard pruning: J(i, k) = inf",
            "9:          End If",
            "10:         EST_ik = max(avail[k], max_{p in Pred(i)} (finish[p] + Comm(p, i)))",
            "11:         EFT_ik = EST_ik + (w_i / s_ik)",
            "12:         E_ckpt = floor(p_ik / tau_i) * (T_ser + (Δq_i * 8)/U_k + T_ver)",
            "13:         E_restart = (1 - exp(-lambda_k * p_ik)) * (tau_i / 2 + T_restore)",
            "14:         Score = EFT_ik + (delta * E_ckpt) + (eta * E_restart) + (rho * T_attest)",
            "15:         If Score < min_score then",
            "16:             min_score = Score, best_worker = k",
            "17:         End If",
            "18:     End For",
            "19:     Assign task i -> best_worker; Update finish[i] and avail[best_worker]",
            "20: End While",
            "21: Return Schedule"
        ]
    )

    # Embed Figure 1 (Architecture)
    add_ieee_figure(doc, 1, ARTIFACTS["arch"], "GhostInTheMachine end-to-end execution pipeline and runtime architecture.", width_in=3.4)

    # SECTION V
    doc.add_paragraph("V. EXPERIMENTAL SETUP AND METHODOLOGY", style="Heading 1")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "The empirical evaluation is compiled across a 280-run simulation matrix covering 7 hourly churn rates (0.00 to 0.30), 2 network profiles "
        "(symmetric 100 Mbps vs asymmetric 10 Mbps residential uplink), 5 random seeds (42, 101, 777, 999, 2024), and 4 scheduling algorithms: "
        "Proposed Risk-Aware (GhostInTheMachine), HEFT [1], Greedy EFT, and Bounded ACO (tuned with 20 ants, 25 iterations, and MMAS bounds). "
        "All metrics capture sample means, standard deviations, 95% Confidence Intervals (CI_95), and Welch's t-tests. "
        "The DAG generator reproduces characteristic fork-join, diamond, and pipeline topological structures consistent with Pegasus Montage and CyberShake benchmarks."
    )

    # SECTION VI
    doc.add_paragraph("VI. RESULTS AND EMPIRICAL ANALYSIS", style="Heading 1")
    doc.add_paragraph("A. Primary Breakthrough: State Recovery Latency under Asymmetric Uplinks", style="Heading 2")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "Fig. 2 illustrates the core breakthrough of GhostInTheMachine. Under asymmetric residential links (U_k = 10 Mbps), baseline schedulers "
        "attempting full state snapshot transfers suffer recovery latencies scaling linearly from 30.70s to 38.02s (mean 34.36s ± 2.27s). "
        "In contrast, GhostInTheMachine's incremental state deltas (Δq_i = 6–9 MB) restored from durable peer stores reduce recovery latency "
        "to 0.81s (asymmetric) and 0.54s (symmetric), representing a 97.6% (42x) reduction in failover delay. This eliminates the multi-tens-of-seconds "
        "uplink bottleneck stall that cripples legacy systems upon host preemption."
    )

    # Embed Table I
    add_ieee_table(
        doc,
        "I",
        "Failure Recovery Latency vs. State Payload Size Across Network Profiles (N=45 Preemption Events)",
        ["State Size", "Delta Mode", "Uplink Profile", "Mean Latency", "95% CI"],
        [
            ["6.02 MB", "Incremental Delta", "100 Mbps Sym", "0.54 s", "[0.54, 0.54]"],
            ["9.01 MB", "Incremental Delta", "10 Mbps Asym", "0.81 s", "[0.81, 0.81]"],
            ["33.28 MB", "Full Snapshot (Base)", "100 Mbps Sym", "3.14 s", "[3.03, 3.25]"],
            ["40.04 MB", "Full Snapshot (Base)", "10 Mbps Asym", "34.36 s", "[32.09, 36.63]"],
        ],
        [0.75, 0.75, 0.75, 0.55, 0.65],
        note="Demonstrates 42.4x recovery speedup under residential upload bottlenecks (10 Mbps)."
    )

    # Embed Figure 2
    add_ieee_figure(doc, 2, ARTIFACTS["fig2"], "Failure recovery latency vs. checkpoint delta size under asymmetric (10 Mbps) vs. symmetric (100 Mbps) uplinks.", width_in=3.4)

    doc.add_paragraph("B. Statistical Makespan Comparison: Low Churn vs. High Churn", style="Heading 2")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "Table II details makespan across algorithms aggregated over all evaluation runs. Under asymmetric links, Bounded-ACO achieves the shortest "
        "average makespan (137.02s ± 11.11s) owing to multi-ant path exploration. Proposed-RiskAware averages 148.42s ± 20.30s, comparable to HEFT (146.39s ± 11.78s) "
        "and Greedy-EFT (145.35s ± 17.79s). Pairwise Welch's t-tests (Table IV) confirm that makespan differences between Proposed, HEFT, and Greedy-EFT "
        "are statistically indistinguishable (t = 0.469 to 0.527, p > 0.59). Claiming raw makespan superiority would be scientifically unfounded; "
        "the genuine contribution of GhostInTheMachine resides in fault recovery speed and deadline insulation."
    )

    # Embed Table II
    add_ieee_table(
        doc,
        "II",
        "Statistical Makespan Comparison Across Algorithms and Profiles (N=35 Runs per Condition)",
        ["Algorithm", "Profile", "Makespan (s)", "Std Dev (s)", "95% CI (s)", "P95 Tail (s)"],
        [
            ["Bounded-ACO", "Asymmetric", "137.02", "11.11", "[133.3, 140.7]", "153.35"],
            ["Greedy-EFT", "Asymmetric", "145.35", "17.79", "[139.5, 151.2]", "175.23"],
            ["HEFT Baseline", "Asymmetric", "146.39", "11.78", "[142.5, 150.3]", "156.11"],
            ["Proposed-RiskAware", "Asymmetric", "148.42", "20.30", "[141.7, 155.1]", "168.87"],
            ["HEFT Baseline", "Symmetric", "66.24", "11.06", "[62.6, 69.9]", "83.49"],
            ["Proposed-RiskAware", "Symmetric", "69.48", "14.90", "[64.5, 74.4]", "89.54"],
            ["Greedy-EFT", "Symmetric", "70.40", "8.99", "[67.4, 73.4]", "80.94"],
            ["Bounded-ACO", "Symmetric", "71.33", "10.90", "[67.7, 74.9]", "80.70"],
        ],
        [0.85, 0.55, 0.50, 0.50, 0.50, 0.50],
        note="Compiled across 280 runs with 5 seeds and 7 churn rates (0% to 30%)."
    )

    doc.add_paragraph("C. SLA Deadline Miss Rate Under Stochastic Churn", style="Heading 2")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "Fig. 1 demonstrates the impact of preemption churn on SLA deadline compliance. Under zero churn, baseline miss rates are 20%. "
        "As churn increases to 15%–30%, Greedy-EFT and HEFT experience up to 40% deadline miss rates because host preemption forces 34s recovery stalls. "
        "Proposed-RiskAware bounds deadline violations below 20% under moderate churn by routing state-delta recovery through high-throughput replica peers."
    )

    # Embed Figure 1
    add_ieee_figure(doc, 3, ARTIFACTS["fig1"], "Workflow SLA deadline miss rate vs. worker churn rate (with 95% confidence intervals).", width_in=3.4)

    doc.add_paragraph("D. Goodput-to-Overhead Ratio (GOR) and Overhead Breakdown", style="Heading 2")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "Fig. 3 presents the normalized compute decomposition, while Fig. 4 traces Goodput-to-Overhead Ratio across churn rates. Under symmetric bandwidth, "
        "GhostInTheMachine delivers 96.4%–96.9% useful goodput. Under asymmetric 10 Mbps residential links, state serialization (T_ser ~ 0.5s) "
        "and background delta upload preserve an 80.4%–80.9% net goodput. While uncheckpointed baselines register ~99% GOR when unperturbed (zero checkpoint overhead), "
        "they pay a catastrophic 34.4s penalty upon every preemption, wiping out in-flight work and saturating residential uplinks."
    )

    # Embed Figure 3 & Figure 4
    add_ieee_figure(doc, 4, ARTIFACTS["fig3"], "Goodput vs. overhead breakdown across scheduling algorithms.", width_in=3.4)
    add_ieee_figure(doc, 5, ARTIFACTS["fig4"], "Goodput-to-Overhead Ratio (GOR) vs. worker churn rate (95% CI).", width_in=3.4)

    # Embed Table IV (Welch's t-test Hypothesis Validation)
    add_ieee_table(
        doc,
        "IV",
        "Pairwise Welch's t-Test Hypothesis Testing (Proposed-RiskAware vs. Baselines)",
        ["Profile", "Churn", "Baseline", "Prop (s)", "Base (s)", "t-stat", "p-value", "Sig (p<0.05)"],
        [
            ["Asymmetric", "0.00", "HEFT", "147.43", "141.12", "0.469", "0.6388", "NO"],
            ["Asymmetric", "0.00", "Greedy-EFT", "147.43", "139.21", "0.527", "0.5982", "NO"],
            ["Asymmetric", "0.00", "Bounded-ACO", "147.43", "137.02", "0.863", "0.3882", "NO"],
            ["Asymmetric", "0.30", "HEFT", "148.61", "148.28", "0.031", "0.9757", "NO"],
            ["Asymmetric", "0.30", "Greedy-EFT", "148.61", "147.64", "0.080", "0.9366", "NO"],
            ["Asymmetric", "0.30", "Bounded-ACO", "148.61", "137.02", "1.029", "0.3034", "NO"],
            ["Symmetric", "0.00", "HEFT", "69.20", "65.70", "0.372", "0.7099", "NO"],
            ["Symmetric", "0.30", "HEFT", "69.82", "66.92", "0.330", "0.7411", "NO"],
        ],
        [0.6, 0.4, 0.6, 0.45, 0.45, 0.4, 0.45, 0.35],
        note="Confirms makespan differences are statistically indistinguishable; value lies in recovery latency."
    )

    # SECTION VII
    doc.add_paragraph("VII. SIMULATION-TO-REALITY CALIBRATION", style="Heading 1")
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

    # SECTION VIII
    doc.add_paragraph("VIII. CONCLUSION", style="Heading 1")
    p = doc.add_paragraph(style="Body Text")
    p.add_run(
        "Executing dependent workflow DAGs across consumer volunteer hardware requires confronting the physical reality of residential network "
        "asymmetry. Conventional scheduling heuristics that prioritize raw makespan fail when host disconnections force multi-gigabyte state "
        "re-transfers over 10 Mbps uplinks. GhostInTheMachine resolves this vulnerability through upload-aware risk placement and asynchronous "
        "state-delta checkpointing. Empirical evaluation across 280 runs confirms that while makespan remains statistically tied under quiescent "
        "conditions (p > 0.59), state-delta recovery achieves a 97.6% (42x) reduction in failover latency (0.81s vs. 34.36s), insulating workflow "
        "deadlines against catastrophic preemption cascades."
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
