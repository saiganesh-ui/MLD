import os
import uuid
import time
import pandas as pd
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
from config import Config
from database.models import Customer, Account, Transaction, AuditLog
from database.database import db
from preprocessing.data_cleaning import DataCleaner
from preprocessing.transaction_processor import TransactionProcessor
from ontology.ontology_manager import OntologyManager

import_bp = Blueprint('import_data', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@import_bp.route('/import')
@login_required
def index():
    return render_template('import.html')

@import_bp.route('/api/upload', methods=['POST'])
@login_required
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part provided.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Invalid file format. Only CSV files are allowed.'}), 400

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    filepath = os.path.join(Config.UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(filepath)

    try:
        start_time = time.time()
        raw_df = pd.read_csv(filepath)
        total_records = len(raw_df)

        cleaned_df = DataCleaner.clean_transactions_df(raw_df)
        valid_records = len(cleaned_df)
        invalid_records = total_records - valid_records

        processor = TransactionProcessor(db.session)
        suspicious_count = 0
        alerts_generated = 0

        # Process cleaned rows into DB
        for _, row in cleaned_df.iterrows():
            s_acc_num = str(row['sender_account'])
            r_acc_num = str(row['receiver_account'])

            # Ensure accounts exist or create stub
            s_acc = Account.query.filter_by(account_number=s_acc_num).first()
            if not s_acc:
                # Find or create dummy customer
                cust = Customer.query.first()
                cust_id = cust.customer_id if cust else "CUST-1001"
                s_acc = Account(account_number=s_acc_num, customer_id=cust_id, country=str(row['sender_country']))
                db.session.add(s_acc)

            r_acc = Account.query.filter_by(account_number=r_acc_num).first()
            if not r_acc:
                cust = Customer.query.first()
                cust_id = cust.customer_id if cust else "CUST-1001"
                r_acc = Account(account_number=r_acc_num, customer_id=cust_id, country=str(row['receiver_country']))
                db.session.add(r_acc)

            tx_id = str(row.get('transaction_id', f"TXN-{uuid.uuid4().hex[:8].upper()}"))

            t = Transaction(
                transaction_id=tx_id,
                sender_account=s_acc_num,
                receiver_account=r_acc_num,
                amount=float(row['amount']),
                currency=str(row.get('currency', 'USD')),
                transaction_type=str(row.get('transaction_type', 'WIRE')),
                transaction_date=pd.to_datetime(row['transaction_date']),
                sender_country=str(row['sender_country']),
                receiver_country=str(row['receiver_country']),
                description=str(row.get('description', 'CSV Uploaded Transaction'))
            )
            db.session.add(t)

            res = processor.process_transaction(t, commit=False)
            if res['suspicious']:
                suspicious_count += 1
            if res['alert_generated']:
                alerts_generated += 1

        db.session.commit()

        # Audit log
        audit = AuditLog(
            user=session.get('username', 'admin'),
            action='CSV_DATA_IMPORTED',
            entity='Transaction',
            entity_id=f"Records_{valid_records}",
            timestamp=datetime.utcnow()
        )
        db.session.add(audit)
        db.session.commit()

        duration = round(time.time() - start_time, 2)

        return jsonify({
            'success': True,
            'message': 'CSV processed successfully.',
            'summary': {
                'records_uploaded': total_records,
                'valid_records': valid_records,
                'invalid_records': invalid_records,
                'suspicious_records': suspicious_count,
                'alerts_generated': alerts_generated,
                'duration_seconds': duration
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to process CSV file: {str(e)}'}), 500
