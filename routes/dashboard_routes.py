from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from sqlalchemy import func
from datetime import datetime
from config import Config
from database.models import Customer, Account, Transaction, Alert, AuditLog
from database.database import db

dashboard_bp = Blueprint('dashboard', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    return render_template('dashboard.html')

@dashboard_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@dashboard_bp.route('/api/settings', methods=['GET', 'POST'])
@login_required
def api_settings():
    if request.method == 'POST':
        data = request.get_json() or {}
        
        # 1. Validate & update risk weights if provided
        weights = data.get('weights')
        if weights:
            try:
                amt = float(weights.get('amount_anomaly', Config.RISK_WEIGHTS['amount_anomaly']))
                freq = float(weights.get('frequency_anomaly', Config.RISK_WEIGHTS['frequency_anomaly']))
                pat = float(weights.get('transaction_pattern', Config.RISK_WEIGHTS['transaction_pattern']))
                geo = float(weights.get('geographic_factor', Config.RISK_WEIGHTS['geographic_factor']))
                hist = float(weights.get('historical_behavior', Config.RISK_WEIGHTS['historical_behavior']))
            except (ValueError, TypeError):
                return jsonify({'success': False, 'error': 'All weights must be valid numeric values.'}), 400

            if any(w < 0 for w in [amt, freq, pat, geo, hist]):
                return jsonify({'success': False, 'error': 'Weights cannot be negative numbers.'}), 400

            total_weight = round(amt + freq + pat + geo + hist, 1)
            if total_weight != 100.0:
                return jsonify({'success': False, 'error': f'Total weights must equal exactly 100% (Current sum: {total_weight}%).'}), 400

            Config.RISK_WEIGHTS['amount_anomaly'] = amt
            Config.RISK_WEIGHTS['frequency_anomaly'] = freq
            Config.RISK_WEIGHTS['transaction_pattern'] = pat
            Config.RISK_WEIGHTS['geographic_factor'] = geo
            Config.RISK_WEIGHTS['historical_behavior'] = hist

        # 2. Validate & update thresholds if provided
        thresholds = data.get('thresholds')
        if thresholds:
            try:
                large_tx = float(thresholds.get('large_transaction', Config.LARGE_TRANSACTION_THRESHOLD))
                struct_min = float(thresholds.get('structuring_min', Config.STRUCTURING_MIN_AMOUNT))
                struct_max = float(thresholds.get('structuring_max', Config.STRUCTURING_MAX_AMOUNT))
                freq_win = int(thresholds.get('frequency_window', Config.HIGH_FREQUENCY_WINDOW_HOURS))
                rapid_win = int(thresholds.get('rapid_transfer_window', Config.RAPID_TRANSFER_WINDOW_HOURS))
                dormant = int(thresholds.get('dormant_days', Config.DORMANT_DAYS_THRESHOLD))
            except (ValueError, TypeError):
                return jsonify({'success': False, 'error': 'All threshold parameters must be valid numeric values.'}), 400

            if struct_min < 0 or struct_max < 0 or large_tx < 0:
                return jsonify({'success': False, 'error': 'Monetary thresholds cannot be negative.'}), 400

            if struct_min >= struct_max:
                return jsonify({'success': False, 'error': 'Structuring minimum must be strictly less than structuring maximum.'}), 400

            if freq_win < 1 or rapid_win < 1 or dormant < 1:
                return jsonify({'success': False, 'error': 'Time windows and dormant days must be at least 1.'}), 400

            Config.LARGE_TRANSACTION_THRESHOLD = large_tx
            Config.STRUCTURING_MIN_AMOUNT = struct_min
            Config.STRUCTURING_MAX_AMOUNT = struct_max
            Config.HIGH_FREQUENCY_WINDOW_HOURS = freq_win
            Config.RAPID_TRANSFER_WINDOW_HOURS = rapid_win
            Config.DORMANT_DAYS_THRESHOLD = dormant

        # Audit log entry
        audit = AuditLog(
            user=session.get('username', 'admin'),
            action='ENGINE_SETTINGS_UPDATED',
            entity='DetectionConfig',
            entity_id='WeightsAndThresholds',
            timestamp=datetime.utcnow()
        )
        db.session.add(audit)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Engine configuration successfully updated and loaded into active reasoning engines.',
            'weights': Config.RISK_WEIGHTS,
            'thresholds': {
                'large_transaction': Config.LARGE_TRANSACTION_THRESHOLD,
                'structuring_min': Config.STRUCTURING_MIN_AMOUNT,
                'structuring_max': Config.STRUCTURING_MAX_AMOUNT,
                'frequency_window': Config.HIGH_FREQUENCY_WINDOW_HOURS,
                'rapid_transfer_window': Config.RAPID_TRANSFER_WINDOW_HOURS,
                'dormant_days': Config.DORMANT_DAYS_THRESHOLD
            },
            'last_updated': audit.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')
        })

    # GET request
    last_log = AuditLog.query.filter_by(action='ENGINE_SETTINGS_UPDATED').order_by(AuditLog.timestamp.desc()).first()
    last_updated_str = last_log.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC') if last_log else "Default Configuration"

    return jsonify({
        'weights': Config.RISK_WEIGHTS,
        'thresholds': {
            'large_transaction': Config.LARGE_TRANSACTION_THRESHOLD,
            'structuring_min': Config.STRUCTURING_MIN_AMOUNT,
            'structuring_max': Config.STRUCTURING_MAX_AMOUNT,
            'frequency_window': Config.HIGH_FREQUENCY_WINDOW_HOURS,
            'rapid_transfer_window': Config.RAPID_TRANSFER_WINDOW_HOURS,
            'dormant_days': Config.DORMANT_DAYS_THRESHOLD
        },
        'last_updated': last_updated_str,
        'status': 'Saved'
    })

@dashboard_bp.route('/api/dashboard/stats')
@login_required
def get_stats():
    total_customers = Customer.query.count()
    total_accounts = Account.query.count()
    total_transactions = Transaction.query.count()
    suspicious_transactions = Transaction.query.filter_by(suspicious=True).count()
    open_alerts = Alert.query.filter_by(status='Open').count()
    high_risk_customers = Customer.query.filter_by(risk_level='High').count()

    avg_score = db.session.query(func.avg(Transaction.risk_score)).scalar() or 0.0

    # Risk distribution for charts
    low_risk = Customer.query.filter_by(risk_level='Low').count()
    med_risk = Customer.query.filter_by(risk_level='Medium').count()
    high_risk = Customer.query.filter_by(risk_level='High').count()

    # Alert severity distribution
    info_alerts = Alert.query.filter_by(severity='INFO').count()
    warn_alerts = Alert.query.filter_by(severity='WARNING').count()
    high_alerts = Alert.query.filter_by(severity='HIGH').count()
    crit_alerts = Alert.query.filter_by(severity='CRITICAL').count()

    # Top risky customers
    top_customers = Customer.query.order_by(Customer.risk_score.desc()).limit(5).all()

    # Country activity breakdown
    country_stats = db.session.query(
        Transaction.sender_country, func.count(Transaction.id)
    ).group_by(Transaction.sender_country).order_by(func.count(Transaction.id).desc()).limit(6).all()

    # Transaction types breakdown
    type_stats = db.session.query(
        Transaction.transaction_type, func.count(Transaction.id)
    ).group_by(Transaction.transaction_type).all()

    return jsonify({
        'total_customers': total_customers,
        'total_accounts': total_accounts,
        'total_transactions': total_transactions,
        'suspicious_transactions': suspicious_transactions,
        'open_alerts': open_alerts,
        'high_risk_customers': high_risk_customers,
        'average_risk_score': round(float(avg_score), 1),
        'risk_distribution': {
            'low': low_risk,
            'medium': med_risk,
            'high': high_risk
        },
        'alert_severity': {
            'INFO': info_alerts,
            'WARNING': warn_alerts,
            'HIGH': high_alerts,
            'CRITICAL': crit_alerts
        },
        'top_risky_customers': [c.to_dict() for c in top_customers],
        'country_activity': [{'country': c[0], 'count': c[1]} for c in country_stats],
        'transaction_types': [{'type': t[0], 'count': t[1]} for t in type_stats]
    })

@dashboard_bp.route('/api/risk-distribution')
@login_required
def get_risk_distribution():
    low = Transaction.query.filter(Transaction.risk_score <= 30).count()
    med = Transaction.query.filter(Transaction.risk_score > 30, Transaction.risk_score <= 70).count()
    high = Transaction.query.filter(Transaction.risk_score > 70).count()
    return jsonify({'Low': low, 'Medium': med, 'High': high})
