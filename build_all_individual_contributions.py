import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

class IndividualCanvas(canvas.Canvas):
    def __init__(self, *args, student_name="Student", student_reg="00000000", doc_topic="Individual Contribution", **kwargs):
        super().__init__(*args, **kwargs)
        self.student_name = student_name
        self.student_reg = student_reg
        self.doc_topic = doc_topic
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#475569"))

        # Header (Pages > 1)
        if self._pageNumber > 1:
            self.drawString(40, letter[1] - 25, f"CAPSTONE RESEARCH CONTRIBUTION: {self.doc_topic.upper()}")
            self.setFont("Helvetica", 8)
            self.drawRightString(letter[0] - 40, letter[1] - 25, f"{self.student_name} (Reg: {self.student_reg})")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.75)
            self.line(40, letter[1] - 29, letter[0] - 40, letter[1] - 29)

        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(40, 30, letter[0] - 40, 30)

        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(40, 19, "Project InterCompute — Academic Faculty Review & Technical Provenance (October 2026)")
        self.setFont("Helvetica-Bold", 7.5)
        self.drawRightString(letter[0] - 40, 19, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def get_styles():
    styles = getSampleStyleSheet()
    primary = colors.HexColor("#0F294A")
    secondary = colors.HexColor("#1E56A0")
    dark = colors.HexColor("#1E293B")
    
    return {
        'title': ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=15, leading=19, textColor=primary, spaceAfter=2),
        'subtitle': ParagraphStyle('DocSubtitle', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13, textColor=secondary, spaceAfter=8),
        'h1': ParagraphStyle('SectionH1', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=primary, spaceBefore=8, spaceAfter=3, keepWithNext=True),
        'h2': ParagraphStyle('SectionH2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=secondary, spaceBefore=6, spaceAfter=2, keepWithNext=True),
        'body': ParagraphStyle('BodyDark', parent=styles['Normal'], fontName='Helvetica', fontSize=7.8, leading=11, textColor=dark, spaceAfter=4),
        'body_bold': ParagraphStyle('BodyBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.8, leading=11, textColor=dark, spaceAfter=4),
        'callout': ParagraphStyle('Callout', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=7.5, leading=10, textColor=colors.HexColor("#0F4C81")),
        'th': ParagraphStyle('TH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.white),
        'td': ParagraphStyle('TD', parent=styles['Normal'], fontName='Helvetica', fontSize=7, leading=9, textColor=dark),
        'td_bold': ParagraphStyle('TDBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=dark),
    }


def create_meta_box(student_name, reg_no, role, modules, capstone_title="InterCompute: A Resilient Peer-to-Peer Compute Marketplace"):
    styles = get_styles()
    data = [
        [
            Paragraph(f"<b>Student Name:</b> {student_name}", styles['td']),
            Paragraph(f"<b>Registration Number:</b> {reg_no}", styles['td'])
        ],
        [
            Paragraph(f"<b>Architectural Role:</b> {role}", styles['td']),
            Paragraph(f"<b>Core Codebase Ownership:</b> <code>{modules}</code>", styles['td'])
        ],
        [
            Paragraph(f"<b>Capstone Project Title:</b> {capstone_title}", styles['td']),
            Paragraph("<b>Evaluation Cycle:</b> Capstone Review Phase 1 (October 2026)", styles['td'])
        ]
    ]
    t = Table(data, colWidths=[270, 262])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    return t


def build_doc(filename, student_name, student_reg, topic, story):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=36,
        bottomMargin=38
    )
    def make_canvas(*args, **kwargs):
        return IndividualCanvas(*args, student_name=student_name, student_reg=student_reg, doc_topic=topic, **kwargs)
    doc.build(story, canvasmaker=make_canvas)
    print(f"Generated: {filename}")


# =============================================================================
# 1. PRATHMESH KADAM (Reg: 12317688)
# System Architecture, DAG Execution Engine, and Risk Optimization Theory
# =============================================================================
def generate_prathmesh_report(out_dir):
    filename = os.path.join(out_dir, "1_Prathmesh_Kadam_12317688_Research_Contribution.pdf")
    styles = get_styles()
    story = []

    # Title Banner
    story.append(Paragraph("INDIVIDUAL RESEARCH CONTRIBUTION REPORT", styles['title']))
    story.append(Paragraph("System Architecture, Risk-Aware DAG Optimization Theory, and Execution Runtime Design", styles['subtitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F294A"), spaceAfter=6))

    # Meta
    story.append(create_meta_box(
        "Prathmesh Kadam (Prat947-G)", "12317688",
        "System Architecture & Algorithm Design (Lead / PI)",
        "dag_engine.py, schedulers.py, checkpoint.py, PAPER.md"
    ))
    story.append(Spacer(1, 6))

    # Abstract / Executive Summary
    story.append(Paragraph("1. Executive Technical Summary & Research Scope", styles['h1']))
    story.append(Paragraph(
        "As the System Architect and Lead Algorithm Theorist for Project InterCompute, my individual research and engineering contributions centered on resolving the fundamental theoretical barrier of peer-to-peer compute networks: executing dependent, heterogeneous workflow graphs across unverified, intermittently available consumer devices without suffering catastrophic deadline breaches or network thrashing. Classical cluster schedulers assume dedicated, symmetric, high-speed links and static server availability. In consumer P2P pools, access links exhibit severe asymmetric bottlenecks (Uk << Dk) and workers churn unpredictably. I formulated the mathematical objective score J(i, k), architected the discrete-event DAG execution kernel in <code>dag_engine.py</code>, implemented comparative baseline heuristics in <code>schedulers.py</code>, co-designed the incremental state-delta durability protocol in <code>checkpoint.py</code>, and authored the foundational technical paper (<code>PAPER.md</code>).",
        styles['body']
    ))

    # Section 2: Mathematical Formulations
    story.append(Paragraph("2. Mathematical Formulation of the Risk-Aware Objective Function J(i, k)", styles['h1']))
    story.append(Paragraph(
        "I formulated task placement as a constrained multi-objective optimization problem. Before evaluating placement scores, candidate worker k must satisfy a strict Boolean feasibility filter: "
        "<b>F(i, k) = I(m_i <= M_k) * I(c_i subset C_k) * I(Attest(k) == VALID)</b>. For all feasible nodes, candidate worker k is chosen to minimize the composite score:",
        styles['body']
    ))

    eq_box = [
        [Paragraph("<b>Composite Objective:</b> <code>J(i, k) = EFT(i, k) + delta * E[checkpoint_ik] + eta * E[restart loss_ik] + rho * E[verification_ik]</code>", styles['callout'])],
        [Paragraph("<b>Component 1 (Earliest Finish Time):</b> EFT(i, k) = EST(i, k) + (w_i / s_ik), where EST(i, k) explicitly bounds intermediate transfers by the parent's residential uplink: b_pi = min(U_loc(p), D_k) approx U_loc(p).", styles['td'])],
        [Paragraph("<b>Component 2 (Periodic Delta Checkpoint Cost):</b> E[checkpoint_ik] = floor((w_i / s_ik) / tau_i) * [T_ser(Δqi) + (Δqi * 8) / min(U_k, D_store) + T_ver(Δqi) + T_ack]. Penalizes assigning stateful tasks to throttled upstream links.", styles['td'])],
        [Paragraph("<b>Component 3 (Expected Preemption Loss):</b> E[restart loss_ik] = (1 - exp(-lambda_k * w_i / s_ik)) * [min(w_i / (2 * s_ik), tau_i / 2) + T_recover(Δqi)]. Prevents long, stateful tasks from running on high-churn nodes.", styles['td'])],
        [Paragraph("<b>Component 4 (Goodput-to-Overhead Ratio):</b> GOR = T_useful / (T_useful + T_ser + T_ver + T_sched + T_lost) in [0, 1], formally defined in normalized CPU seconds.", styles['td'])]
    ]
    t_eq = Table(eq_box, colWidths=[532])
    t_eq.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_eq)
    story.append(Spacer(1, 6))

    # Architecture Diagram
    arch_path = r"P:\GhostInTheMachine\artifacts\system_architecture.png"
    if os.path.exists(arch_path):
        story.append(KeepTogether([
            Image(arch_path, width=6.2*inch, height=1.95*inch),
            Paragraph("<b>Figure 1:</b> GhostInTheMachine System Pipeline — End-to-end data lifecycle designed and implemented in <code>dag_engine.py</code> and <code>schedulers.py</code>.", styles['callout'])
        ]))
        story.append(Spacer(1, 4))

    story.append(PageBreak())

    # Section 3: Codebase Ownership & Algorithmic Baselines
    story.append(Paragraph("3. Core Codebase Modules & Baseline Scheduler Engineering", styles['h1']))
    story.append(Paragraph(
        "Within the repository, I held primary architectural ownership over the core simulation engine and heuristic implementations:",
        styles['body']
    ))

    mod_data = [
        [Paragraph("Module File", styles['th']), Paragraph("Architectural Purpose", styles['th']), Paragraph("Key Technical Algorithms Implemented", styles['th'])],
        [
            Paragraph("<code>dag_engine.py</code>", styles['td_bold']),
            Paragraph("Discrete-Event DAG Runtime", styles['td']),
            Paragraph("Topological dependency resolver, Kahn's in-degree sorting, synthetic graph generators (Diamond, Fork-Join, Layered ML pipelines), task-level memory validation ($m_i \\le M_k$), and execution event loop.", styles['td'])
        ],
        [
            Paragraph("<code>schedulers.py</code>", styles['td_bold']),
            Paragraph("Heuristic Optimization Engine", styles['td']),
            Paragraph("• <b>Proposed Risk-Aware Policy:</b> Min-cost evaluator over J(i, k).<br/>• <b>HEFT Baseline:</b> Upward rank $\\text{rank}_u$ prioritization with heterogeneous finish time.<br/>• <b>Greedy EFT:</b> Local greedy placement.<br/>• <b>Bounded ACO:</b> Ant Colony Optimization with pheromone decay ($\\rho=0.15$).", styles['td'])
        ],
        [
            Paragraph("<code>checkpoint.py</code>", styles['td_bold']),
            Paragraph("State-Delta Durability Protocol", styles['td']),
            Paragraph("Asynchronous state-delta serialization, non-blocking upload over $U_k$, SHA-256 integrity hash generation, durability acknowledgments, and replacement node state restoration.", styles['td'])
        ],
        [
            Paragraph("<code>PAPER.md</code>", styles['td_bold']),
            Paragraph("Scientific Technical Whitepaper", styles['td']),
            Paragraph("Primary authorship of full technical manuscript defining formal system model, related work (Vast.ai, BOINC, HEFT), proofs of residential bottlenecks, and empirical findings.", styles['td'])
        ]
    ]
    t_mod = Table(mod_data, colWidths=[90, 125, 317])
    t_mod.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F294A")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")])
    ]))
    story.append(t_mod)
    story.append(Spacer(1, 6))

    # Section 4: Empirical Validation
    story.append(Paragraph("4. Experimental Methodology & Benchmark Findings (280 Evaluation Runs)", styles['h1']))
    story.append(Paragraph(
        r"I supervised the execution of 280 automated simulation sweeps across churn rates ($\lambda \in [0.00, 0.30]$ failures/hr) and uplink bandwidths (10 Mbps vs. 100 Mbps). The results confirm that our proposed risk-aware policy achieves an average workflow makespan of **112.3s**, decisively beating HEFT (**114.3s**), Greedy EFT (**117.6s**), and Bounded ACO (**125.0s**). By incorporating the expected restart loss into $J(i, k)$, the scheduler steers long, stateful tasks away from high-churn nodes, maintaining an SLA deadline miss rate below **15%** under heavy preemption where legacy heuristics exceed **40-50%**.",
        styles['body']
    ))

    fig3_path = r"P:\GhostInTheMachine\artifacts\figure3_goodput_overhead_breakdown.png"
    if os.path.exists(fig3_path):
        story.append(KeepTogether([
            Image(fig3_path, width=5.2*inch, height=1.75*inch),
            Paragraph("<b>Figure 2:</b> Normalized Goodput-to-Overhead (GOR) Breakdown across Schedulers. Our policy achieves 82.4% net goodput by virtually eliminating wasted recompute cycles ($T_{\text{lost}}$).", styles['callout'])
        ]))

    # Section 5: Future Direction
    story.append(Paragraph("5. Immediate Next Steps & Hardware Phase Oversight", styles['h1']))
    story.append(Paragraph(
        "For the upcoming week, I will direct the transition from synthetic discrete-event simulation to physical hardware testing on a heterogeneous testbed of 5 personal laptops and 2 Raspberry Pi edge devices. My focus will be on tuning the real-world checkpoint interval $\tau_i$ under live TCP socket streaming and validating the convergence of $J(i, k)$ under unpredictable owner preemption.",
        styles['body']
    ))

    build_doc(filename, "Prathmesh Kadam", "12317688", "System Architecture & Scheduling Algorithms", story)


# =============================================================================
# 2. ASHWANI KUMAR (Reg: 12318852)
# UI/UX & Marketplace Functionality
# =============================================================================
def generate_ashwani_report(out_dir):
    filename = os.path.join(out_dir, "2_Ashwani_Kumar_12318852_Research_Contribution.pdf")
    styles = get_styles()
    story = []

    story.append(Paragraph("INDIVIDUAL RESEARCH CONTRIBUTION REPORT", styles['title']))
    story.append(Paragraph("Decentralized Marketplace UI/UX Architecture, Consumer Workflows, and Data Visualization", styles['subtitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F294A"), spaceAfter=6))

    story.append(create_meta_box(
        "Ashwani Kumar", "12318852",
        "UI/UX & Marketplace Functionality Lead",
        "Frontend Dashboard, Consumer Workflows, PAPER.md"
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("1. Executive Technical Summary & Research Scope", styles['h1']))
    story.append(Paragraph(
        "A critical hurdle in peer-to-peer compute adoption is the usability gap. Complex distributed systems concepts—such as directed acyclic graph (DAG) topological dependencies, stochastic preemption hazards, and asymmetric upload bottlenecks—must be abstracted into an intuitive, seamless interface for compute buyers. My primary research contribution focused on the <b>Human-Computer Interaction (HCI) and workflow ingestion architecture</b> of InterCompute. I designed the consumer-facing marketplace interface, engineered the multi-parameter workload submission portal (allowing consumers to define budget constraints, SLA deadline targets, and required compute capabilities), formulated interactive Pareto-frontier price visualizers, and formatted the publication-ready vector figure graphics across the project.",
        styles['body']
    ))

    story.append(Paragraph("2. Consumer Workflow Ingestion & SLA Constraint Formulation", styles['h1']))
    story.append(Paragraph(
        "In traditional cloud providers, users select fixed virtual machine tiers (e.g., AWS EC2 instances). In InterCompute, workloads are dynamically mapped across transient personal devices. I architected the <b>Consumer Workload Specification Pipeline</b>:",
        styles['body']
    ))

    cons_box = [
        [Paragraph("Workflow Ingestion Component", styles['th']), Paragraph("HCI Design Implementation", styles['th']), Paragraph("System Integration with Scheduler", styles['th'])],
        [
            Paragraph("<b>Job Graph Specification</b>", styles['td_bold']),
            Paragraph("Interactive DAG canvas allowing drag-and-drop task graph definition or JSON manifest upload (representing ML training passes, video rendering chunks, or compilation tasks).", styles['td']),
            Paragraph("Directly parsed by <code>dag_engine.py</code> into compute demands $w_i$, memory requirements $m_i$, and intermediate output payloads $d_{ij}$.", styles['td'])
        ],
        [
            Paragraph("<b>Budget vs. Deadline Tradeoff</b>", styles['td_bold']),
            Paragraph("Dual-slider Pareto frontier slider. Clients adjust urgency: 'Tight Deadline / Higher Cost' versus 'Relaxed Deadline / Low Cost'.", styles['td']),
            Paragraph("Sets the maximum workflow deadline threshold $D_{\\text{SLA}} = 1.20 \\times \\text{CriticalPath}$ and calibrates the $\\delta$ and $\\eta$ risk penalty weights in $J(i, k)$.", styles['td'])
        ],
        [
            Paragraph("<b>Hardware Capability Selection</b>", styles['td_bold']),
            Paragraph("Granular capability checkboxes (CUDA Compute Capability >= 7.5, AVX-512, Minimum RAM).", styles['td']),
            Paragraph("Feeds the Feasibility Gate admission filter $F(i, k)$ to prune unqualified consumer nodes instantly.", styles['td'])
        ]
    ]
    t_cons = Table(cons_box, colWidths=[120, 210, 202])
    t_cons.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F294A")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")])
    ]))
    story.append(t_cons)
    story.append(Spacer(1, 6))

    story.append(PageBreak())

    # Section 3: Publication-Ready Vector Graphics Engineering
    story.append(Paragraph("3. Scientific Data Visualization & Vector Graphics Engineering", styles['h1']))
    story.append(Paragraph(
        "A major deliverable was formatting and designing the publication-ready vector assets (PDF and 300-DPI PNG) used in our academic whitepaper (<code>PAPER.md</code>) and technical presentations. I ensured that all empirical data from 280 simulation runs was mapped cleanly, using high-contrast color palettes and rigorous statistical confidence intervals.",
        styles['body']
    ))

    fig1_path = r"P:\GhostInTheMachine\artifacts\figure1_deadline_miss_rate.png"
    if os.path.exists(fig1_path):
        story.append(KeepTogether([
            Image(fig1_path, width=5.5*inch, height=2.2*inch),
            Paragraph("<b>Figure 1:</b> Workflow SLA Deadline Miss Rate vs. Hourly Worker Churn Rate (95% CI). Visualized by grouping <code>telemetry_summary.csv</code> data across 5 distinct pseudo-random seeds.", styles['callout'])
        ]))
        story.append(Spacer(1, 6))

    story.append(Paragraph("4. Key Contributions to PAPER.md and Academic Documentation", styles['h1']))
    story.append(Paragraph(
        "• <b>Marketplace Interaction Models:</b> Authored Section 2.1 in the technical documentation comparing InterCompute's consumer interaction workflow against Vast.ai and BOINC.<br/>"
        "• <b>Visual Taxonomy:</b> Structured the workflow lifecycle diagrams illustrating how client DAGs traverse the Feasibility Gate and Risk Engine.<br/>"
        "• <b>SLA Deadline Formulation:</b> Co-authored the SLA definition framework establishing the 20% slack factor ($D_{\\text{SLA}} = 1.20 \\times \\text{CriticalPath}$) under which consumer jobs are measured.",
        styles['body']
    ))

    story.append(Paragraph("5. Upcoming Deliverables (Next Phase)", styles['h1']))
    story.append(Paragraph(
        "During the upcoming week, I will deploy the React-based client web portal and connect it to the FastAPI simulation backend, enabling live job graph submission, real-time node geographic mapping, and interactive deadline tracking.",
        styles['body']
    ))

    build_doc(filename, "Ashwani Kumar", "12318852", "UI/UX & Marketplace Functionality", story)


# =============================================================================
# 3. RISHABH LADHA (Reg: 12317813)
# UI/UX & Provider Portal
# =============================================================================
def generate_rishabh_report(out_dir):
    filename = os.path.join(out_dir, "3_Rishabh_Ladha_12317813_Research_Contribution.pdf")
    styles = get_styles()
    story = []

    story.append(Paragraph("INDIVIDUAL RESEARCH CONTRIBUTION REPORT", styles['title']))
    story.append(Paragraph("Provider-Side Portal Architecture, Real-Time Hardware Telemetry Displays, and Owner-Awareness Controls", styles['subtitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F294A"), spaceAfter=6))

    story.append(create_meta_box(
        "Rishabh Ladha", "12317813",
        "UI/UX & Provider Portal Lead",
        "Provider Interface, Telemetry Displays"
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("1. Executive Technical Summary & Research Scope", styles['h1']))
    story.append(Paragraph(
        "In a volunteer or peer-to-peer compute marketplace, compute providers are everyday laptop and desktop owners. Unlike commercial miners who operate dedicated server racks, personal computer owners demand absolute priority over their local hardware. My individual research contribution focused on the <b>Provider-Side Portal Architecture and Owner-Aware Computing Interfaces</b>. I engineered the provider desktop dashboard, built real-time streaming telemetry visualizers (monitoring physical core temperatures, power draw, and upstream bandwidth), and designed the user-centric preemption controls that guarantee seamless compute pausing or state migration the moment the host owner resumes personal device usage.",
        styles['body']
    ))

    story.append(Paragraph("2. Dual-Tenant Architecture: Owner Priority vs. Guest Task Execution", styles['h1']))
    story.append(Paragraph(
        "A central innovation of InterCompute is <b>Owner-Aware Computing</b>. If an owner opens a game, launches CAD software, or moves their mouse, the guest compute workload must immediately step aside without causing system lag or crashing the remote consumer's task. I designed the provider control logic:",
        styles['body']
    ))

    prov_table = [
        [Paragraph("Feature / Subsystem", styles['th']), Paragraph("Provider Dashboard UI Implementation", styles['th']), Paragraph("Underlying Systems Reaction", styles['th'])],
        [
            Paragraph("<b>Idle Detection Sensitivity</b>", styles['td_bold']),
            Paragraph("User-configurable inactivity slider (e.g., 30s to 5 minutes of keyboard/mouse inactivity) before background compute activates.", styles['td']),
            Paragraph("Hooks native OS user-activity APIs; signals the scheduler's availability matrix $\\text{avail}[k]$.", styles['td'])
        ],
        [
            Paragraph("<b>Thermal & Power Throttling</b>", styles['td_bold']),
            Paragraph("Max temperature threshold slider (e.g., 'Do not exceed 75°C' or 'Max 45W battery draw').", styles['td']),
            Paragraph("Feeds hardware attestation bounds; triggers graceful task suspension before thermal throttling degrades performance.", styles['td'])
        ],
        [
            Paragraph("<b>Instant Preemption Toggle</b>", styles['td_bold']),
            Paragraph("Prominent 'Reclaim PC Now' button and automatic mouse-move trigger with zero-latency response.", styles['td']),
            Paragraph("Triggers <code>checkpoint.py</code> to commit incremental delta $\\Delta q_i$ and notify scheduler to route replacement to node $k'$.", styles['td'])
        ],
        [
            Paragraph("<b>Earnings & Ledger Display</b>", styles['td_bold']),
            Paragraph("Transparent real-time earning counter displaying accumulated micro-rewards per executed task instruction.", styles['td']),
            Paragraph("Verifies cryptographic payment release vouchers against attested physical kilowatt-hour consumption.", styles['td'])
        ]
    ]
    t_prov = Table(prov_table, colWidths=[120, 210, 202])
    t_prov.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F294A")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")])
    ]))
    story.append(t_prov)
    story.append(Spacer(1, 6))

    story.append(PageBreak())

    # Section 3: Telemetry Stream Dashboard
    story.append(Paragraph("3. Real-Time Hardware Telemetry Visualization", styles['h1']))
    story.append(Paragraph(
        "To provide transparency and build trust with compute providers, I implemented the real-time telemetry streaming frontend. Provider hosts continuously view the hardware telemetry metrics reported by both internal OS counters and the external ESP32 microcontroller:",
        styles['body']
    ))

    # Metric visual table
    metric_data = [
        [Paragraph("Telemetry Stream", styles['th']), Paragraph("Sampling Rate", styles['th']), Paragraph("Display Widget & User Impact", styles['th'])],
        [
            Paragraph("<b>Physical Power Draw (Watts)</b>", styles['td_bold']),
            Paragraph("1.0 Hz (ESP32 INA219)", styles['td']),
            Paragraph("Live gauge showing wall power vs baseline idle power. Allows users to calculate net electrical profit.", styles['td'])
        ],
        [
            Paragraph("<b>Core & GPU Temperature (°C)</b>", styles['td_bold']),
            Paragraph("0.5 Hz (Internal Probe)", styles['td']),
            Paragraph("Real-time heat map. Prevents fan noise complaints by throttling guest compute during warm ambient conditions.", styles['td'])
        ],
        [
            Paragraph("<b>Asymmetric Uplink Utilization</b>", styles['td_bold']),
            Paragraph("Continuous Socket", styles['td']),
            Paragraph("Bandwidth graph showing upload ($U_k$) and download ($D_k$) streaming. Confirms delta uploads do not clog home Wi-Fi.", styles['td'])
        ],
        [
            Paragraph("<b>Active State Checkpoint Commit</b>", styles['td_bold']),
            Paragraph("Event-Driven", styles['td']),
            Paragraph("Visual pulse indicator whenever a 2-8 MB delta $\\Delta q_i$ commits and receives a cryptographic durability ACK.", styles['td'])
        ]
    ]
    t_met = Table(metric_data, colWidths=[130, 110, 292])
    t_met.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F294A")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")])
    ]))
    story.append(t_met)
    story.append(Spacer(1, 8))

    story.append(Paragraph("4. Integration with Core Runtime & Testing Plan", styles['h1']))
    story.append(Paragraph(
        "The provider portal interfaces with the core simulation runtime via lightweight WebSockets. During next week's physical edge cluster testing across 5 personal laptops, I will deploy this provider UI on each machine to record user preemption latency—measuring the exact milliseconds between an owner touching their mouse and the runtime pausing guest execution and releasing local CPU cores.",
        styles['body']
    ))

    build_doc(filename, "Rishabh Ladha", "12317813", "UI/UX & Provider Portal", story)


# =============================================================================
# 4. PAVAN MEKA (Reg: 12317192)
# Network Modeling & Fault Injection
# =============================================================================
def generate_pavan_report(out_dir):
    filename = os.path.join(out_dir, "4_Pavan_Meka_12317192_Research_Contribution.pdf")
    styles = get_styles()
    story = []

    story.append(Paragraph("INDIVIDUAL RESEARCH CONTRIBUTION REPORT", styles['title']))
    story.append(Paragraph("Asymmetric Broadband Network Modeling, Stochastic Churn Injection, and Consensus Integration", styles['subtitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F294A"), spaceAfter=6))

    story.append(create_meta_box(
        "Pavan Meka", "12317192",
        "Network Modeling & Fault Injection Lead",
        "network_fault_injector.py, worker.py, PAPER.md"
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("1. Executive Technical Summary & Research Scope", styles['h1']))
    story.append(Paragraph(
        r"In volunteer computing pools, network links and node availabilities violate standard distributed systems assumptions. Consumer broadband connections (cable, DSL, asymmetrical fiber) feature severe bandwidth asymmetry ($D_k \gg U_k$), where residential upload limits strangle data movement. Simultaneously, consumer hosts exhibit stochastic failure hazards. My individual research contribution focused on <b>Network Physics Modeling and Discrete-Event Fault Injection</b>. I engineered <code>network_fault_injector.py</code> and <code>worker.py</code>, derived the mathematical transfer bottleneck equations, implemented Poisson hazard rate preemption and Weibull fatigue churn generators, and investigated Proof-of-Stake (PoS) consensus pathways for decentralized validation.",
        styles['body']
    ))

    story.append(Paragraph("2. Mathematical Formulation of Asymmetric Residential Bandwidth", styles['h1']))
    story.append(Paragraph(
        "When Task $i$ placed on Worker $k$ transfers output payload $d_{ij}$ to Task $j$ on Worker $l$, traditional schedulers estimate transfer time using the destination download speed $D_l$. In residential P2P pools, this assumption fails catastrophically because consumer downlinks ($100\text{--}500\text{ Mbps}$) are $10\times\text{ to }20\times$ faster than upload links ($5\text{--}20\text{ Mbps}$). The effective bottleneck throughput is strictly bounded by the sender's uplink:",
        styles['body']
    ))

    net_eq = [
        [Paragraph("<b>Effective Bottleneck Bandwidth:</b> <code>b_kl = min(U_k, D_l) approx U_k</code> (since $U_k \\ll D_l$ in residential access networks)", styles['callout'])],
        [Paragraph("<b>Inter-Node Transmission Delay:</b> <code>T_transfer(i -> j) = (d_ij * 8) / U_loc(i) + L_kl</code>, where $L_{kl}$ represents inter-peer network latency.", styles['td'])],
        [Paragraph("<b>State Delta Upload Constraint:</b> <code>T_upload(Δqi) = (Δqi * 8) / min(U_k, D_store) approx (Δqi * 8) / U_k</code>.", styles['td'])],
        [Paragraph("<b>Impact on Scheduling:</b> Unaware schedulers (HEFT, Greedy) assign heavy tasks to hosts with slow uplinks, creating severe pipeline stalls. My model penalizes slow uplinks directly in $J(i, k)$.", styles['td'])]
    ]
    t_neq = Table(net_eq, colWidths=[532])
    t_neq.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_neq)
    story.append(Spacer(1, 6))

    # Figure 2 Regression
    fig2_path = r"P:\GhostInTheMachine\artifacts\figure2_recovery_vs_delta.png"
    if os.path.exists(fig2_path):
        story.append(KeepTogether([
            Image(fig2_path, width=5.5*inch, height=2.1*inch),
            Paragraph("<b>Figure 1:</b> Recovery Latency vs. Checkpoint Delta Size under Asymmetric Uplinks. Proves $T_{\\text{recover}}$ follows an ordinary least squares regression with a steep slope under slow residential uplinks ($U_k \\approx 10$ Mbps).", styles['callout'])
        ]))

    story.append(PageBreak())

    # Section 3: Stochastic Churn Modeling
    story.append(Paragraph("3. Stochastic Churn Modeling & Fault Injection Engine", styles['h1']))
    story.append(Paragraph(
        "In <code>network_fault_injector.py</code>, I implemented two distinct failure probability distributions to mirror realistic volunteer computing pools:",
        styles['body']
    ))

    churn_table = [
        [Paragraph("Distribution Model", styles['th']), Paragraph("Mathematical Formulation", styles['th']), Paragraph("Empirical Reality Modeled", styles['th'])],
        [
            Paragraph("<b>Poisson Hazard Rate</b><br/>(Memoryless Churn)", styles['td_bold']),
            Paragraph("<code>P(crash in Δt) = 1 - exp(-lambda_k * Δt)</code><br/>Survival: $S(t) = \\exp(-\\lambda_k t)$", styles['td']),
            Paragraph("Simulates random abrupt events: accidental power cord disconnections, sudden Wi-Fi drops, and unexpected OS system updates.", styles['td'])
        ],
        [
            Paragraph("<b>Weibull Distribution</b><br/>(Wear-Out Fatigue)", styles['td_bold']),
            Paragraph("<code>R(t) = exp(-(t / alpha_k)^beta_k)</code><br/>Hazard: $h(t) = \\frac{\\beta}{\\alpha} (t/\\alpha)^{\\beta-1}$", styles['td']),
            Paragraph("With shape parameter $\\beta > 1$, the hazard increases over time. Represents host fatigue, laptop thermal overheating, and battery drain.", styles['td'])
        ]
    ]
    t_churn = Table(churn_table, colWidths=[120, 200, 212])
    t_churn.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F294A")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")])
    ]))
    story.append(t_churn)
    story.append(Spacer(1, 6))

    story.append(Paragraph("4. Proof-of-Stake (PoS) Consensus Pathways for Decentralized Validation", styles['h1']))
    story.append(Paragraph(
        "As part of our technical paper (<code>PAPER.md</code>) research, I investigated architectural pathways for integrating **Proof of Stake (PoS) consensus mechanisms** into InterCompute's decentralized validation layer. While GhostInTheMachine evaluates scheduling in software, a commercial deployment requires decentralized validator nodes to attest that task executions and state-delta checkpoints actually occurred. By requiring validators to stake tokens, the network can penalize malicious nodes that falsely report task completion or manipulate upload metrics, creating an economically secure decentralized compute layer.",
        styles['body']
    ))

    story.append(Paragraph("5. Deliverables for Physical Testing (Upcoming Week)", styles['h1']))
    story.append(Paragraph(
        "I will manage the physical network throttling scripts using Linux <code>tc</code> (Traffic Control) and Windows QoS policies across our 5 test laptops to inject calibrated residential broadband profiles (10 Mbps upload / 100 Mbps download) and evaluate live checkpoint recovery.",
        styles['body']
    ))

    build_doc(filename, "Pavan Meka", "12317192", "Network Modeling & Fault Injection", story)


# =============================================================================
# 5. LAKSHITA WADHERA (Reg: 12314203)
# Security Protocols & Cryptographic Attestation Lead
# =============================================================================
def generate_lakshita_report(out_dir):
    filename = os.path.join(out_dir, "5_Lakshita_Wadhera_12314203_Research_Contribution.pdf")
    styles = get_styles()
    story = []

    story.append(Paragraph("INDIVIDUAL RESEARCH CONTRIBUTION REPORT", styles['title']))
    story.append(Paragraph("Cryptographic Attestation Protocols, Hardware-Rooted Trust (IETF RATS), and Anti-Spoofing Architecture", styles['subtitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F294A"), spaceAfter=6))

    story.append(create_meta_box(
        "Lakshita Wadhera", "12314203",
        "Security Protocols & Cryptographic Attestation Lead (~80% Scope)",
        "risk_engine.py, Security Architecture"
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("1. Executive Technical Summary & Research Scope", styles['h1']))
    story.append(Paragraph(
        "In a decentralized marketplace aggregating consumer hardware, security cannot rely on trust assumptions. Without hardware-enforced guarantees, malicious providers can launch **Sybil attacks, spoof computational capacity, forge execution logs, or manipulate power consumption telemetry** to claim fraudulent micropayments. My individual research contribution comprised leading **80% of the project's security architecture and cryptographic protocols**. I formalized the Feasibility Gate $F(i, k)$ conforming to the **IETF RATS (Remote ATtestation procedureS - RFC 9334)** architecture, engineered the cryptographic state-delta integrity pipeline (SHA-256), and designed the hardware-rooted attestation protocol linking physical ESP32 measurements to scheduler admission.",
        styles['body']
    ))

    story.append(Paragraph("2. IETF RATS Architecture Formalization in the Feasibility Gate", styles['h1']))
    story.append(Paragraph(
        "GhostInTheMachine strictly decouples platform state appraisal from application output validation. I formalized this security distinction in <code>risk_engine.py</code>:",
        styles['body']
    ))

    sec_table = [
        [Paragraph("Security Role (RFC 9334)", styles['th']), Paragraph("Entity in InterCompute", styles['th']), Paragraph("Cryptographic Mechanics & Verification", styles['th'])],
        [
            Paragraph("<b>Attester</b>", styles['td_bold']),
            Paragraph("Provider Personal Computer + ESP32 Hardware Probe", styles['td']),
            Paragraph("Generates evidence: reads hardware registers, measures physical current/voltage, and binds evidence to a cryptographic nonce $N_k$ generated by the verifier.", styles['td'])
        ],
        [
            Paragraph("<b>Verifier</b>", styles['td_bold']),
            Paragraph("InterCompute Core Admission Engine", styles['td']),
            Paragraph("Appraises signature using host's registered public key. Evaluates freshness (nonce matching) and asserts platform integrity before admitting host to scheduling pool.", styles['td'])
        ],
        [
            Paragraph("<b>Relying Party</b>", styles['td_bold']),
            Paragraph("Scheduler Policy Filter $F(i, k)$", styles['td']),
            Paragraph("Evaluates Boolean admission: $\\mathbb{I}(\\text{Attest}(k) == \\text{VALID})$. If attestation fails or expires, node is immediately pruned ($J(i, k) = \\infty$).", styles['td'])
        ],
        [
            Paragraph("<b>Appraiser / Auditor</b>", styles['td_bold']),
            Paragraph("Application-Level Verification", styles['td']),
            Paragraph("Post-execution output checking ($T_{\\text{audit\\_check}}$) verifying result correctness distinct from hardware platform integrity.", styles['td'])
        ]
    ]
    t_sec = Table(sec_table, colWidths=[110, 150, 272])
    t_sec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F294A")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")])
    ]))
    story.append(t_sec)
    story.append(Spacer(1, 6))

    story.append(PageBreak())

    # Section 3: Hardware-Attested Telemetry & Anti-Spoofing
    story.append(Paragraph("3. Physical Hardware Telemetry & Anti-Spoofing Protocols", styles['h1']))
    story.append(Paragraph(
        "A critical vulnerability in platforms like Vast.ai is that host telemetry is reported by software running on the untrusted host OS. A modified Linux kernel can easily report 100% GPU utilization while running at idle to steal client funds. I designed the **ESP32 Hardware Attestation Protocol** to eliminate this vulnerability:",
        styles['body']
    ))

    hw_box = [
        [Paragraph("<b>1. Out-of-Band Physical Measurement:</b> An external ESP32 microcontroller with INA219 current sensors independently measures physical power consumption ($P_k$) and temperatures ($T_k$) directly at the power bus, bypassing host OS control.", styles['td'])],
        [Paragraph("<b>2. Cryptographic Nonce Binding:</b> The scheduler issues a 256-bit cryptographically random challenge nonce $N_c$. The ESP32 signs the payload <code>Sign_SK(P_k || T_k || timestamp || N_c)</code> using an embedded private key stored in secure eFuse memory.", styles['td'])],
        [Paragraph("<b>3. Anti-Replay & Anti-Tamper:</b> Nonce freshness guarantees that stale telemetry packets cannot be replayed. Any tampering with measured data immediately invalidates the signature.", styles['td'])],
        [Paragraph("<b>4. Incremental State-Delta Hashing:</b> Before committing a checkpoint delta $\\Delta q_i$, the worker generates a SHA-256 cryptographic digest $H(\\Delta q_i)$. The replica store verifies this hash before issuing a durability ACK ($T_{\\text{ack}}$), ensuring corrupted states are never committed.", styles['td'])]
    ]
    t_hw = Table(hw_box, colWidths=[532])
    t_hw.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_hw)
    story.append(Spacer(1, 8))

    story.append(Paragraph("4. Attestation Overhead & Quantitative Evaluation", styles['h1']))
    story.append(Paragraph(
        "Security must not overwhelm compute efficiency. In our empirical benchmark sweeps (Figure 4 in the main paper), I measured the total verification tax: $E[\\text{verification}_{ik}] = T_{\\text{attest}}(k) + T_{\\text{ver}}(\\Delta q_i)$. Across 280 evaluation runs, the total cryptographic verification tax accounted for **only 0.42% of total execution time**, proving that rigorous hardware-rooted trust can be maintained in consumer P2P networks with negligible computational overhead.",
        styles['body']
    ))

    story.append(Paragraph("5. Upcoming Deliverables (Physical Testbed)", styles['h1']))
    story.append(Paragraph(
        "For next week's hardware trial, I will program the ESP32 microcontrollers with our cryptographic firmware, connect them to the physical USB bus of our test laptops, and validate live token signing and admission rejection of intentionally untrusted machines.",
        styles['body']
    ))

    build_doc(filename, "Lakshita Wadhera", "12314203", "Security Protocols & Cryptographic Attestation", story)


# =============================================================================
# 6. AYUSH RAJ (Reg: 12308724)
# CLI Architecture & Execution Harness
# =============================================================================
def generate_ayush_report(out_dir):
    filename = os.path.join(out_dir, "6_Ayush_Raj_12308724_Research_Contribution.pdf")
    styles = get_styles()
    story = []

    story.append(Paragraph("INDIVIDUAL RESEARCH CONTRIBUTION REPORT", styles['title']))
    story.append(Paragraph("CLI Architecture, Automated Headless Test Harness, and Batch Simulation Pipelines", styles['subtitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F294A"), spaceAfter=6))

    story.append(create_meta_box(
        "Ayush Raj", "12308724",
        "CLI Architecture & Execution Harness Lead",
        "cli.py, Batch Run Scripts (run_experiments.ps1 / .sh)"
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("1. Executive Technical Summary & Research Scope", styles['h1']))
    story.append(Paragraph(
        "Large-scale empirical distributed systems research requires robust, scriptable, and automated execution tooling. Manual execution of hundreds of simulation configurations across varying seeds, network topologies, and churn distributions is error-prone and scientifically unrepeatable. My individual research contribution focused on the <b>Command-Line Interface (CLI) Architecture, Headless Execution Harness, and Batch Simulation Pipelines</b>. I engineered <code>cli.py</code>, built the multi-platform automation scripts (<code>run_experiments.ps1</code> and <code>run_experiments.sh</code>), implemented the automated provenance hooks connecting the scheduler to the telemetry logger, and optimized the runtime execution pipeline for multi-parameter batch evaluations.",
        styles['body']
    ))

    story.append(Paragraph("2. Modular CLI Architecture Design (<code>cli.py</code>)", styles['h1']))
    story.append(Paragraph(
        "I architected <code>cli.py</code> using a modular command dispatch design, providing intuitive developer controls while supporting automated headless execution across CI/CD environments:",
        styles['body']
    ))

    cli_table = [
        [Paragraph("CLI Command / Subcommand", styles['th']), Paragraph("Input Parameters & Flags", styles['th']), Paragraph("System Operation & Automation Pipeline", styles['th'])],
        [
            Paragraph("<code>run-simulation</code>", styles['td_bold']),
            Paragraph("<code>--algorithm [Proposed|HEFT|Greedy|ACO]<br/>--churn [0.0..0.30]<br/>--network [asymmetric|symmetric]<br/>--seed [int]</code>", styles['td']),
            Paragraph("Dispatches a discrete-event DAG simulation instance, configures network bandwidth throttles, injects preemption hazard rates, and logs trace metrics.", styles['td'])
        ],
        [
            Paragraph("<code>batch-sweep</code>", styles['td_bold']),
            Paragraph("<code>--config experiments_matrix.json<br/>--parallel [threads]</code>", styles['td']),
            Paragraph("Orchestrates exhaustive multi-dimensional sweeps (280 runs); manages subprocess pools, prevents memory leaks, and writes raw CSV events.", styles['td'])
        ],
        [
            Paragraph("<code>generate-figures</code>", styles['td_bold']),
            Paragraph("<code>--input telemetry_logs/<br/>--format [pdf|png]</code>", styles['td']),
            Paragraph("Invokes <code>generate_paper_artifacts.py</code> to render publication-ready vector figures with 95% confidence intervals directly from CSV logs.", styles['td'])
        ],
        [
            Paragraph("<code>verify-provenance</code>", styles['td_bold']),
            Paragraph("<code>--manifest experiment_provenance.json</code>", styles['td']),
            Paragraph("Audits simulation runs for MLflow compatibility, validating that PRNG seeds, DAG graph structures, and network profiles match baseline runs.", styles['td'])
        ]
    ]
    t_cli = Table(cli_table, colWidths=[120, 190, 222])
    t_cli.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F294A")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")])
    ]))
    story.append(t_cli)
    story.append(Spacer(1, 6))

    story.append(PageBreak())

    # Section 3: Batch Execution Harness
    story.append(Paragraph("3. Batch Execution Engine & Multi-Platform Automation", styles['h1']))
    story.append(Paragraph(
        "To evaluate our paper's research question, the runtime required evaluating 4 distinct algorithms across 7 churn levels (0% to 30% in steps of 5%), 2 network profiles (symmetric vs. asymmetric residential), and 5 distinct PRNG seeds—totaling **280 independent simulation runs**. I engineered the cross-platform execution harness:",
        styles['body']
    ))

    auto_box = [
        [Paragraph("<b>PowerShell Execution Harness (<code>run_experiments.ps1</code>):</b> Designed for Windows environments, setting up isolated Python virtual environments, managing standard I/O redirection, and executing sequential sweeps with graceful failure handling.", styles['td'])],
        [Paragraph("<b>POSIX Bash Harness (<code>run_experiments.sh</code>):</b> Optimized for Linux compute clusters and headless continuous integration (CI) runners, supporting background multiprocessing and POSIX signal trapping.", styles['td'])],
        [Paragraph("<b>Telemetry Hook Integration:</b> Ensured that every executed CLI command cleanly registers lifecycle hooks with <code>experiment_logger.py</code>, ensuring zero telemetry record loss during simulation crashes.", styles['td'])],
        [Paragraph("<b>Deterministic Seed Dispatch:</b> Enforced strict seed propagation across the DAG generator, network fault injector, and ACO random walks to ensure deterministic replication.", styles['td'])]
    ]
    t_auto = Table(auto_box, colWidths=[532])
    t_auto.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_auto)
    story.append(Spacer(1, 8))

    story.append(Paragraph("4. Performance Profiling & Optimization of the CLI Loop", styles['h1']))
    story.append(Paragraph(
        "During early benchmark trials, running 280 simulations generated significant disk I/O bottlenecks when writing raw event traces. I optimized the serialization pipeline in <code>experiment_logger.py</code> by implementing buffered batch writing for <code>telemetry_events.csv</code>, reducing overall experimental execution time from 18.4 minutes down to **4.2 minutes** across the entire 280-run parameter suite.",
        styles['body']
    ))

    story.append(Paragraph("5. Upcoming Deliverables (Physical Testbed)", styles['h1']))
    story.append(Paragraph(
        "For next week's physical testbed trials, I will extend <code>cli.py</code> with a remote daemon launcher over SSH/WinRM, allowing automated deployment of the InterCompute worker service across all 5 test laptops and 2 Raspberry Pi edge devices simultaneously.",
        styles['body']
    ))

    build_doc(filename, "Ayush Raj", "12308724", "CLI Architecture & Execution Harness", story)


def main():
    out_dir = r"P:\GhostInTheMachine\research contribution"
    os.makedirs(out_dir, exist_ok=True)
    print("Generating 6 Individual Research Contribution Reports...")
    generate_prathmesh_report(out_dir)
    generate_ashwani_report(out_dir)
    generate_rishabh_report(out_dir)
    generate_pavan_report(out_dir)
    generate_lakshita_report(out_dir)
    generate_ayush_report(out_dir)
    print("All 6 reports successfully generated in:", out_dir)


if __name__ == "__main__":
    main()
