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
            self.drawString(40, letter[1] - 25, f"INTERCOMPUTE RESEARCH: {self.doc_topic.upper()}")
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
        self.drawString(40, 19, "InterCompute Capstone Project — Departmental Academic Evaluation (October 2026)")
        self.setFont("Helvetica-Bold", 7.5)
        self.drawRightString(letter[0] - 40, 19, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def get_styles():
    styles = getSampleStyleSheet()
    primary = colors.HexColor("#0F294A")
    secondary = colors.HexColor("#1E56A0")
    dark = colors.HexColor("#1E293B")
    
    return {
        'title': ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=primary, spaceAfter=2),
        'subtitle': ParagraphStyle('DocSubtitle', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=13, textColor=secondary, spaceAfter=8),
        'h1': ParagraphStyle('SectionH1', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11.5, leading=15, textColor=primary, spaceBefore=10, spaceAfter=4, keepWithNext=True),
        'h2': ParagraphStyle('SectionH2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, leading=12, textColor=secondary, spaceBefore=7, spaceAfter=3, keepWithNext=True),
        'body': ParagraphStyle('BodyDark', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=11, textColor=dark, spaceAfter=4),
        'body_bold': ParagraphStyle('BodyBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=11, textColor=dark, spaceAfter=4),
        'callout': ParagraphStyle('Callout', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=7.5, leading=10.5, textColor=colors.HexColor("#0F4C81")),
        'th': ParagraphStyle('TH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.white),
        'td': ParagraphStyle('TD', parent=styles['Normal'], fontName='Helvetica', fontSize=7, leading=9, textColor=dark),
        'td_bold': ParagraphStyle('TDBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=dark),
    }


def create_meta_box(student_name, reg_no, role, modules, capstone_title="InterCompute: A Resilient Peer-to-Peer Compute Marketplace"):
    styles = get_styles()
    data = [
        [
            Paragraph(f"<b>Researcher Name:</b> {student_name}", styles['td']),
            Paragraph(f"<b>Registration Number:</b> {reg_no}", styles['td'])
        ],
        [
            Paragraph(f"<b>Architectural Specialization:</b> {role}", styles['td']),
            Paragraph(f"<b>Core Codebase Ownership:</b> <code>{modules}</code>", styles['td'])
        ],
        [
            Paragraph(f"<b>Project Title:</b> {capstone_title}", styles['td']),
            Paragraph("<b>Evaluation Period:</b> Capstone Review Phase 1 (Oct 2026)", styles['td'])
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

print("Base setup loaded.")

