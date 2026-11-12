from flask import Blueprint, render_template, Response, request, session, redirect, url_for, make_response
from database.models import Customer, Account, Transaction, Alert
from database.database import db
from reports.report_generator import ReportGenerator
from reports.pdf_generator import PDFReportGenerator
from reports.csv_exporter import CSVExporter

report_bp = Blueprint('report', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@report_bp.route('/reports')
@login_required
def index():
    search = request.args.get('search', '').strip()
    risk_level = request.args.get('risk_level', '').strip()

    query = Customer.query
    if search:
        query = query.filter((Customer.customer_id.ilike(f'%{search}%')) | (Customer.name.ilike(f'%{search}%')))
    if risk_level and risk_level.lower() != 'all':
        query = query.filter(Customer.risk_level.ilike(risk_level))

    customers = query.order_by(Customer.risk_score.desc()).limit(200).all()
    return render_template('reports.html', customers=customers, search=search, risk_level=risk_level)

@report_bp.route('/reports/download/pdf/system-summary')
@login_required
def download_system_summary_pdf():
    generator = ReportGenerator(db.session)
    stats, recent_txs, alerts = generator.get_system_summary_data()
    pdf_bytes = PDFReportGenerator.generate_system_summary_report(stats, recent_txs, alerts)

    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=System_Summary_SAR_Report.pdf'
    return response

@report_bp.route('/reports/download/pdf/customer/<cust_id>')
@login_required
def download_customer_pdf(cust_id):
    customer = Customer.query.filter_by(customer_id=cust_id).first_or_404()
    accounts = Account.query.filter_by(customer_id=customer.customer_id).all()
    acc_nums = [a.account_number for a in accounts]

    transactions = Transaction.query.filter(
        (Transaction.sender_account.in_(acc_nums)) |
        (Transaction.receiver_account.in_(acc_nums))
    ).order_by(Transaction.transaction_date.desc()).all() if acc_nums else []

    alerts = Alert.query.filter_by(customer_id=customer.customer_id).all()

    pdf_bytes = PDFReportGenerator.generate_customer_risk_report(customer, accounts, transactions, alerts)

    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Customer_Risk_{customer.customer_id}.pdf'
    return response

@report_bp.route('/reports/download/csv/transactions')
@login_required
def download_transactions_csv():
    transactions = Transaction.query.order_by(Transaction.transaction_date.desc()).limit(2000).all()
    csv_data = CSVExporter.export_transactions(transactions)

    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=transactions_export.csv'
    return response

@report_bp.route('/reports/download/csv/alerts')
@login_required
def download_alerts_csv():
    alerts = Alert.query.order_by(Alert.created_at.desc()).all()
    csv_data = CSVExporter.export_alerts(alerts)

    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=alerts_export.csv'
    return response
