import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

class PDFReportGenerator:
    @staticmethod
    def generate_system_summary_report(stats, transactions, alerts):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1A365D'),
            spaceAfter=12
        )
        heading2_style = ParagraphStyle(
            'H2Style',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2B6CB0'),
            spaceBefore=12,
            spaceAfter=6
        )
        normal_style = styles['Normal']

        # Header
        story.append(Paragraph("Financial Crime Analytics — System Summary Report", title_style))
        story.append(Paragraph(f"Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", normal_style))
        story.append(Paragraph("<b>Disclaimer:</b> Detected transactions are classified as potentially suspicious for research review, not confirmed criminal activity.", normal_style))
        story.append(Spacer(1, 15))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0'), spaceAfter=15))

        # Executive Summary Table
        story.append(Paragraph("Executive Metrics", heading2_style))
        summary_data = [
            ["Metric", "Value"],
            ["Total Customers", str(stats.get('total_customers', 0))],
            ["Total Accounts", str(stats.get('total_accounts', 0))],
            ["Total Transactions", str(stats.get('total_transactions', 0))],
            ["Suspicious Transactions", str(stats.get('suspicious_count', 0))],
            ["Open Alerts", str(stats.get('open_alerts', 0))],
            ["High Risk Customers", str(stats.get('high_risk_customers', 0))],
            ["Average System Risk Score", f"{stats.get('avg_risk_score', 0):.1f} / 100"]
        ]
        t_summary = Table(summary_data, colWidths=[240, 240])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F7FAFC')]),
            ('PADDING', (0,0), (-1,-1), 6)
        ]))
        story.append(t_summary)
        story.append(Spacer(1, 15))

        # Recent Alerts Table
        story.append(Paragraph("High Risk & Critical Alerts", heading2_style))
        alert_data = [["Alert ID", "Customer", "Severity", "Risk Score", "Status"]]
        for a in alerts[:10]:
            alert_data.append([a.alert_id, a.customer_id, a.severity, f"{a.risk_score:.1f}", a.status])

        if len(alert_data) == 1:
            alert_data.append(["No alerts found", "-", "-", "-", "-"])

        t_alerts = Table(alert_data, colWidths=[100, 100, 90, 80, 110])
        t_alerts.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F7FAFC')]),
            ('PADDING', (0,0), (-1,-1), 5)
        ]))
        story.append(t_alerts)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def generate_customer_risk_report(customer, accounts, transactions, alerts):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1A365D'))
        heading2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#2B6CB0'))
        normal_style = styles['Normal']

        story.append(Paragraph(f"Customer Risk Profile — {customer.name} ({customer.customer_id})", title_style))
        story.append(Paragraph(f"Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", normal_style))
        story.append(Spacer(1, 10))

        # Customer Details Table
        c_info = [
            ["Customer ID", customer.customer_id, "Risk Level", customer.risk_level],
            ["Name", customer.name, "Risk Score", f"{customer.risk_score:.1f} / 100"],
            ["Country", customer.country, "Occupation", customer.occupation or "N/A"],
            ["Age", str(customer.age), "Accounts Owned", str(len(accounts))]
        ]
        t_cinfo = Table(c_info, colWidths=[110, 130, 110, 130])
        t_cinfo.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#EDF2F7')),
            ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#EDF2F7')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('PADDING', (0,0), (-1,-1), 6)
        ]))
        story.append(t_cinfo)
        story.append(Spacer(1, 15))

        # Recent Transactions
        story.append(Paragraph("Transaction Activity History", heading2_style))
        tx_data = [["Tx ID", "Type", "Amount", "Sender Country", "Receiver Country", "Risk Score"]]
        for t in transactions[:15]:
            tx_data.append([t.transaction_id, t.transaction_type, f"${t.amount:,.2f}", t.sender_country, t.receiver_country, f"{t.risk_score:.1f}"])

        if len(tx_data) == 1:
            tx_data.append(["No transactions", "-", "-", "-", "-", "-"])

        t_tx = Table(tx_data, colWidths=[90, 75, 95, 105, 105, 75])
        t_tx.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F7FAFC')]),
            ('PADDING', (0,0), (-1,-1), 5)
        ]))
        story.append(t_tx)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
