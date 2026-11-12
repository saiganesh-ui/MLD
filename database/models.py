from datetime import datetime
from database.database import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='analyst')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    occupation = db.Column(db.String(100))
    country = db.Column(db.String(100), nullable=False)
    risk_level = db.Column(db.String(20), default='Low')  # Low, Medium, High
    risk_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    accounts = db.relationship('Account', backref='customer', lazy=True, cascade="all, delete-orphan")
    alerts = db.relationship('Alert', backref='customer', lazy=True)
    risk_histories = db.relationship('RiskHistory', backref='customer', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'name': self.name,
            'age': self.age,
            'occupation': self.occupation,
            'country': self.country,
            'risk_level': self.risk_level,
            'risk_score': self.risk_score,
            'account_count': len(self.accounts),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.String(50), db.ForeignKey('customers.customer_id'), nullable=False)
    account_type = db.Column(db.String(50), default='Savings')  # Savings, Checking, Corporate, Offshore
    balance = db.Column(db.Float, default=0.0)
    country = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'account_number': self.account_number,
            'customer_id': self.customer_id,
            'account_type': self.account_type,
            'balance': self.balance,
            'country': self.country,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    sender_account = db.Column(db.String(50), db.ForeignKey('accounts.account_number'), nullable=False)
    receiver_account = db.Column(db.String(50), db.ForeignKey('accounts.account_number'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    transaction_type = db.Column(db.String(50), default='WIRE')  # WIRE, ACH, CASH_DEPOSIT, ATM, CARD
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    sender_country = db.Column(db.String(100), nullable=False)
    receiver_country = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    risk_score = db.Column(db.Float, default=0.0)
    risk_level = db.Column(db.String(20), default='Low')
    suspicious = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    alerts = db.relationship('Alert', backref='transaction', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'sender_account': self.sender_account,
            'receiver_account': self.receiver_account,
            'amount': self.amount,
            'currency': self.currency,
            'transaction_type': self.transaction_type,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'sender_country': self.sender_country,
            'receiver_country': self.receiver_country,
            'description': self.description,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'suspicious': self.suspicious,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Alert(db.Model):
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    transaction_id = db.Column(db.String(50), db.ForeignKey('transactions.transaction_id'), nullable=False)
    customer_id = db.Column(db.String(50), db.ForeignKey('customers.customer_id'), nullable=False)
    alert_type = db.Column(db.String(100), nullable=False)  # Smurfing, Rapid Transfer, Large Tx, etc.
    severity = db.Column(db.String(20), default='WARNING')  # INFO, WARNING, HIGH, CRITICAL
    description = db.Column(db.Text, nullable=False)
    risk_score = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), default='Open', index=True)  # Open, Under Review, Resolved, False Positive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'alert_id': self.alert_id,
            'transaction_id': self.transaction_id,
            'customer_id': self.customer_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'description': self.description,
            'risk_score': self.risk_score,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }

class RiskHistory(db.Model):
    __tablename__ = 'risk_history'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(50), db.ForeignKey('customers.customer_id'), nullable=False)
    risk_score = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'reason': self.reason,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    entity = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user,
            'action': self.action,
            'entity': self.entity,
            'entity_id': self.entity_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
