import os
import random
import uuid
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from database.database import db
from database.models import User, Customer, Account, Transaction
from preprocessing.transaction_processor import TransactionProcessor
from ontology.ontology_manager import OntologyManager
from ml.train import train_anomaly_model

COUNTRIES = [
    'United States', 'United Kingdom', 'Germany', 'France', 'Canada',
    'Australia', 'Japan', 'Singapore', 'Switzerland', 'Brazil',
    'Cayman Islands', 'Panama', 'Seychelles', 'Bahamas', 'British Virgin Islands'
]

HIGH_RISK_LIST = ['Cayman Islands', 'Panama', 'Seychelles', 'Bahamas', 'British Virgin Islands']

OCCUPATIONS = [
    'Software Engineer', 'Financial Analyst', 'Consultant', 'Real Estate Agent',
    'Business Executive', 'Accountant', 'Physician', 'Attorney', 'Merchant', 'Investor'
]

TRANSACTION_TYPES = ['WIRE', 'ACH', 'CASH_DEPOSIT', 'ATM', 'CARD']

FIRST_NAMES = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 'William', 'Elizabeth',
               'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica', 'Thomas', 'Sarah', 'Charles', 'Karen',
               'Christopher', 'Nancy', 'Daniel', 'Lisa', 'Matthew', 'Betty', 'Anthony', 'Margaret', 'Donald', 'Sandra',
               'Mark', 'Ashley', 'Paul', 'Kimberly', 'Steven', 'Emily', 'Andrew', 'Donna', 'Kenneth', 'Michelle',
               'Joshua', 'Dorothy', 'Kevin', 'Carol', 'Brian', 'Amanda', 'George', 'Melissa', 'Edward', 'Deborah']

LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
              'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
              'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson',
              'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores']

def seed_database(app, num_customers=500, num_accounts=700, num_transactions=5000):
    with app.app_context():
        print("Initializing database tables...")
        db.create_all()

        # Check if already seeded
        if User.query.filter_by(username='admin').first():
            print("Database already contains admin user. Skipping seed.")
            return

        print("Creating admin user...")
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)

        print(f"Generating {num_customers} synthetic customers...")
        customers = []
        for i in range(1, num_customers + 1):
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            country = random.choice(COUNTRIES)
            c = Customer(
                customer_id=f"CUST-{1000 + i}",
                name=name,
                age=random.randint(21, 75),
                occupation=random.choice(OCCUPATIONS),
                country=country,
                risk_level='Low',
                risk_score=random.uniform(5.0, 25.0)
            )
            customers.append(c)
            db.session.add(c)
        db.session.commit()

        print(f"Generating {num_accounts} accounts...")
        accounts = []
        for i in range(1, num_accounts + 1):
            owner = random.choice(customers)
            acc_num = f"ACC{100000 + i}"
            acc = Account(
                account_number=acc_num,
                customer_id=owner.customer_id,
                account_type=random.choice(['Savings', 'Checking', 'Corporate', 'Offshore']),
                balance=round(random.uniform(5000, 250000), 2),
                country=owner.country
            )
            accounts.append(acc)
            db.session.add(acc)
        db.session.commit()

        print("Training ML Anomaly Detection Model...")
        train_anomaly_model()

        print(f"Generating {num_transactions} transactions with synthetic normal & suspicious patterns...")
        tx_list = []
        base_time = datetime.utcnow() - timedelta(days=30)

        # 1. Generate normal transactions (85%)
        normal_count = int(num_transactions * 0.85)
        for i in range(normal_count):
            s_acc = random.choice(accounts)
            r_acc = random.choice([a for a in accounts if a.account_number != s_acc.account_number])
            
            amount = round(float(random.expovariate(1.0 / 1200.0) + 10), 2)
            tx_date = base_time + timedelta(minutes=random.randint(1, 43200))
            
            t = Transaction(
                transaction_id=f"TXN-{10000 + len(tx_list) + 1}",
                sender_account=s_acc.account_number,
                receiver_account=r_acc.account_number,
                amount=amount,
                currency='USD',
                transaction_type=random.choice(TRANSACTION_TYPES),
                transaction_date=tx_date,
                sender_country=s_acc.country,
                receiver_country=r_acc.country,
                description='Standard Account Transfer',
                risk_score=random.uniform(0.0, 20.0),
                suspicious=False
            )
            tx_list.append(t)
            db.session.add(t)

        # 2. Inject Pattern 1: Smurfing / Structuring (Multiple transfers $8,000–$9,999)
        smurf_senders = random.sample(accounts, 15)
        for acc in smurf_senders:
            rec = random.choice([a for a in accounts if a.account_number != acc.account_number])
            burst_time = base_time + timedelta(days=random.randint(1, 25))
            for k in range(random.randint(4, 7)):
                amt = round(random.uniform(8500, 9950), 2)
                t = Transaction(
                    transaction_id=f"TXN-{10000 + len(tx_list) + 1}",
                    sender_account=acc.account_number,
                    receiver_account=rec.account_number,
                    amount=amt,
                    currency='USD',
                    transaction_type='WIRE',
                    transaction_date=burst_time + timedelta(minutes=k * 25),
                    sender_country=acc.country,
                    receiver_country=rec.country,
                    description='Structured wire transfer below threshold',
                    suspicious=True
                )
                tx_list.append(t)
                db.session.add(t)

        # 3. Inject Pattern 2: Rapid Transfers / Layering Chain (A -> B -> C -> D)
        for _ in range(10):
            chain_accs = random.sample(accounts, 4)
            chain_time = base_time + timedelta(days=random.randint(1, 28))
            amt = round(random.uniform(45000, 120000), 2)
            for idx in range(3):
                t = Transaction(
                    transaction_id=f"TXN-{10000 + len(tx_list) + 1}",
                    sender_account=chain_accs[idx].account_number,
                    receiver_account=chain_accs[idx+1].account_number,
                    amount=amt,
                    currency='USD',
                    transaction_type='WIRE',
                    transaction_date=chain_time + timedelta(minutes=(idx+1)*30),
                    sender_country=chain_accs[idx].country,
                    receiver_country=chain_accs[idx+1].country,
                    description='Rapid pass-through layering transaction',
                    suspicious=True
                )
                tx_list.append(t)
                db.session.add(t)

        # 4. Inject Pattern 3: Circular Transfers (A -> B -> C -> A)
        for _ in range(8):
            circ_accs = random.sample(accounts, 3)
            circ_time = base_time + timedelta(days=random.randint(1, 28))
            amt = round(random.uniform(60000, 150000), 2)
            steps = [(circ_accs[0], circ_accs[1]), (circ_accs[1], circ_accs[2]), (circ_accs[2], circ_accs[0])]
            for idx, (s, r) in enumerate(steps):
                t = Transaction(
                    transaction_id=f"TXN-{10000 + len(tx_list) + 1}",
                    sender_account=s.account_number,
                    receiver_account=r.account_number,
                    amount=amt,
                    currency='USD',
                    transaction_type='WIRE',
                    transaction_date=circ_time + timedelta(hours=(idx+1)*2),
                    sender_country=s.country,
                    receiver_country=r.country,
                    description='Circular transfer chain loop',
                    suspicious=True
                )
                tx_list.append(t)
                db.session.add(t)

        # 5. Inject Pattern 4: High-Risk Cross Border
        offshore_accs = [a for a in accounts if a.country in HIGH_RISK_LIST]
        if not offshore_accs:
            offshore_accs = accounts[:10]
        for acc in random.sample(offshore_accs, min(10, len(offshore_accs))):
            rec = random.choice([a for a in accounts if a.account_number != acc.account_number])
            t = Transaction(
                transaction_id=f"TXN-{10000 + len(tx_list) + 1}",
                sender_account=acc.account_number,
                receiver_account=rec.account_number,
                amount=round(random.uniform(75000, 300000), 2),
                currency='USD',
                transaction_type='WIRE',
                transaction_date=base_time + timedelta(days=random.randint(1, 28)),
                sender_country=acc.country,
                receiver_country=rec.country,
                description='High-value cross border transfer to high-risk jurisdiction',
                suspicious=True
            )
            tx_list.append(t)
            db.session.add(t)

        db.session.commit()
        print("Database commit successful. Running detection & risk scoring pipeline...")

        # Process transactions through Detection Engine to compute actual scores & alerts
        processor = TransactionProcessor(db.session)
        sample_eval_count = 0
        for tx in tx_list:
            if tx.suspicious or random.random() < 0.05:
                processor.process_transaction(tx, commit=False)
                sample_eval_count += 1

        db.session.commit()
        print(f"Processed {sample_eval_count} transactions through Detection & Alert Engines.")

        # Populate RDF Knowledge Graph
        print("Populating RDF / OWL Ontology Knowledge Graph...")
        ont_mgr = OntologyManager()
        ont_mgr.populate_from_db(customers, accounts, tx_list[:500])
        ont_mgr.save_ontology()

        print("Demo data seed completed successfully!")

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    seed_database(app)
