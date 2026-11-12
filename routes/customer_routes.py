from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from database.models import Customer, Account, Transaction, Alert, RiskHistory
from database.database import db

customer_bp = Blueprint('customer', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@customer_bp.route('/customers')
@login_required
def list_customers():
    return render_template('customers.html')

@customer_bp.route('/customers/<cust_id>')
@login_required
def view_customer(cust_id):
    customer = Customer.query.filter_by(customer_id=cust_id).first_or_404()
    accounts = Account.query.filter_by(customer_id=customer.customer_id).all()
    acc_numbers = [a.account_number for a in accounts]

    transactions = Transaction.query.filter(
        (Transaction.sender_account.in_(acc_numbers)) |
        (Transaction.receiver_account.in_(acc_numbers))
    ).order_by(Transaction.transaction_date.desc()).all() if acc_numbers else []

    alerts = Alert.query.filter_by(customer_id=customer.customer_id).all()
    risk_history = RiskHistory.query.filter_by(customer_id=customer.customer_id).order_by(RiskHistory.timestamp.asc()).all()

    total_volume = sum(t.amount for t in transactions)
    avg_tx = total_volume / len(transactions) if transactions else 0.0

    # Counterparty count
    counterparties = set()
    for t in transactions:
        if t.sender_account in acc_numbers:
            counterparties.add(t.receiver_account)
        else:
            counterparties.add(t.sender_account)

    return render_template(
        'customer_detail.html',
        customer=customer,
        accounts=accounts,
        transactions=transactions,
        alerts=alerts,
        risk_history=risk_history,
        total_volume=total_volume,
        avg_tx=avg_tx,
        counterparty_count=len(counterparties)
    )

@customer_bp.route('/api/customers')
@login_required
def api_customers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    search = request.args.get('search', '')
    risk_level = request.args.get('risk_level', '')

    query = Customer.query
    if search:
        query = query.filter((Customer.name.ilike(f"%{search}%")) | (Customer.customer_id.ilike(f"%{search}%")))
    if risk_level:
        query = query.filter_by(risk_level=risk_level)

    pagination = query.order_by(Customer.risk_score.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'customers': [c.to_dict() for c in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    })

@customer_bp.route('/api/customers/<cust_id>')
@login_required
def api_get_customer(cust_id):
    c = Customer.query.filter_by(customer_id=cust_id).first_or_404()
    return jsonify(c.to_dict())
