from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for, abort
from database.models import Transaction, Account, Customer, Alert
from database.database import db
from preprocessing.transaction_processor import TransactionProcessor

transaction_bp = Blueprint('transaction', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@transaction_bp.route('/transactions')
@login_required
def list_transactions():
    return render_template('transactions.html')

@transaction_bp.route('/transactions/<tx_id>')
@login_required
def view_transaction(tx_id):
    tx = Transaction.query.filter_by(transaction_id=tx_id).first_or_404()
    sender_acc = Account.query.filter_by(account_number=tx.sender_account).first()
    receiver_acc = Account.query.filter_by(account_number=tx.receiver_account).first()

    sender_cust = Customer.query.filter_by(customer_id=sender_acc.customer_id).first() if sender_acc else None
    receiver_cust = Customer.query.filter_by(customer_id=receiver_acc.customer_id).first() if receiver_acc else None

    alerts = Alert.query.filter_by(transaction_id=tx.transaction_id).all()

    # Re-run processor to get full explainability breakdown
    processor = TransactionProcessor(db.session)
    analysis = processor.process_transaction(tx, commit=False)

    return render_template(
        'transaction_detail.html',
        transaction=tx,
        sender_acc=sender_acc,
        receiver_acc=receiver_acc,
        sender_cust=sender_cust,
        receiver_cust=receiver_cust,
        alerts=alerts,
        analysis=analysis
    )

@transaction_bp.route('/api/transactions')
@login_required
def api_transactions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    search = request.args.get('search', '')
    suspicious_only = request.args.get('suspicious', '') == 'true'
    risk_level = request.args.get('risk_level', '')
    country = request.args.get('country', '')

    query = Transaction.query

    if search:
        query = query.filter(
            (Transaction.transaction_id.ilike(f"%{search}%")) |
            (Transaction.sender_account.ilike(f"%{search}%")) |
            (Transaction.receiver_account.ilike(f"%{search}%"))
        )

    if suspicious_only:
        query = query.filter_by(suspicious=True)

    if risk_level:
        query = query.filter_by(risk_level=risk_level)

    if country:
        query = query.filter((Transaction.sender_country == country) | (Transaction.receiver_country == country))

    pagination = query.order_by(Transaction.transaction_date.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'transactions': [t.to_dict() for t in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    })

@transaction_bp.route('/api/transactions/<tx_id>')
@login_required
def api_get_transaction(tx_id):
    tx = Transaction.query.filter_by(transaction_id=tx_id).first_or_404()
    return jsonify(tx.to_dict())

@transaction_bp.route('/api/analyze/<tx_id>', methods=['POST'])
@login_required
def analyze_transaction(tx_id):
    tx = Transaction.query.filter_by(transaction_id=tx_id).first_or_404()
    processor = TransactionProcessor(db.session)
    result = processor.process_transaction(tx, commit=True)
    return jsonify(result)
