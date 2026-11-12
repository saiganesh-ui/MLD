from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from datetime import datetime
from database.models import Alert, Transaction, Customer, Account, AuditLog
from database.database import db

alert_bp = Blueprint('alert', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@alert_bp.route('/alerts')
@login_required
def list_alerts():
    return render_template('alerts.html')

@alert_bp.route('/alerts/<alert_id>')
@login_required
def view_alert(alert_id):
    alert = Alert.query.filter_by(alert_id=alert_id).first_or_404()
    transaction = Transaction.query.filter_by(transaction_id=alert.transaction_id).first()
    customer = Customer.query.filter_by(customer_id=alert.customer_id).first()
    accounts = Account.query.filter_by(customer_id=alert.customer_id).all() if customer else []

    return render_template(
        'alert_detail.html',
        alert=alert,
        transaction=transaction,
        customer=customer,
        accounts=accounts
    )

@alert_bp.route('/api/alerts')
@login_required
def api_alerts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    severity = request.args.get('severity', '')
    status = request.args.get('status', '')
    search = request.args.get('search', '')

    query = Alert.query
    if severity:
        query = query.filter_by(severity=severity)
    if status:
        query = query.filter_by(status=status)
    if search:
        query = query.filter(
            (Alert.alert_id.ilike(f"%{search}%")) |
            (Alert.customer_id.ilike(f"%{search}%")) |
            (Alert.transaction_id.ilike(f"%{search}%"))
        )

    pagination = query.order_by(Alert.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'alerts': [a.to_dict() for a in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    })

@alert_bp.route('/api/alerts/<alert_id>')
@login_required
def api_get_alert(alert_id):
    alert = Alert.query.filter_by(alert_id=alert_id).first_or_404()
    return jsonify(alert.to_dict())

@alert_bp.route('/api/alerts/<alert_id>/status', methods=['POST'])
@login_required
def update_alert_status(alert_id):
    alert = Alert.query.filter_by(alert_id=alert_id).first_or_404()
    data = request.get_json() or {}
    new_status = data.get('status')

    if new_status not in ['Open', 'Under Review', 'Resolved', 'False Positive']:
        return jsonify({'error': 'Invalid status'}), 400

    old_status = alert.status
    alert.status = new_status
    if new_status in ['Resolved', 'False Positive']:
        alert.resolved_at = datetime.utcnow()

    # Log audit entry
    audit = AuditLog(
        user=session.get('username', 'analyst'),
        action=f"ALERT_STATUS_CHANGED_{old_status}_TO_{new_status}",
        entity='Alert',
        entity_id=alert.alert_id,
        timestamp=datetime.utcnow()
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({'message': f'Alert status updated to {new_status}', 'alert': alert.to_dict()})
