from database.models import Customer, Account, Transaction, Alert
from config import Config

class KnowledgeGraphBuilder:
    def __init__(self, db_session):
        self.session = db_session

    def get_graph_data(self, limit=100, customer_filter=None, transaction_filter=None, entity_type_filter=None):
        """
        Builds a JSON-serializable graph structure (nodes & edges)
        for UI visualization in Vis.js / D3.
        """
        nodes = []
        edges = []
        node_ids = set()

        def add_node(nid, label, group, title="", val=10, props=None):
            if nid not in node_ids:
                node_ids.add(nid)
                nodes.append({
                    'id': nid,
                    'label': label,
                    'group': group,
                    'title': title,
                    'value': val,
                    'properties': props or {'entity_id': nid, 'type': group, 'name': label}
                })

        def add_edge(source, target, label, color=None):
            edges.append({
                'from': source,
                'to': target,
                'label': label,
                'arrows': 'to',
                'color': color or '#97C2FC'
            })

        # Base High Risk Countries
        if not entity_type_filter or entity_type_filter in ['Country', 'HighRiskCountry']:
            for country in Config.HIGH_RISK_COUNTRIES[:5]:
                add_node(
                    f"Country_{country}", 
                    country, 
                    "HighRiskCountry", 
                    f"High Risk Country: {country}", 
                    15,
                    props={'entity_id': country, 'type': 'HighRiskCountry', 'name': country, 'rdf_uri': f'mld:Country_{country.replace(" ", "_")}', 'risk_level': 'High'}
                )

        # Customers query
        cust_query = self.session.query(Customer)
        if customer_filter:
            cust_query = cust_query.filter(Customer.customer_id == customer_filter)
        customers = cust_query.limit(limit).all()

        for c in customers:
            c_id = f"Cust_{c.customer_id}"
            if not entity_type_filter or entity_type_filter in ['Customer', 'All']:
                add_node(
                    c_id, 
                    c.name, 
                    "Customer", 
                    f"Customer: {c.name}<br>Risk Level: {c.risk_level}<br>Score: {c.risk_score}", 
                    20,
                    props={'entity_id': c.customer_id, 'type': 'Customer', 'name': c.name, 'country': c.country, 'occupation': c.occupation, 'risk_level': c.risk_level, 'risk_score': c.risk_score, 'rdf_uri': f'mld:Customer_{c.customer_id}'}
                )
            
            # Add country node
            cntry_id = f"Country_{c.country}"
            if not entity_type_filter or entity_type_filter in ['Country', 'All']:
                add_node(
                    cntry_id, 
                    c.country, 
                    "Country", 
                    f"Country: {c.country}", 
                    12,
                    props={'entity_id': c.country, 'type': 'Country', 'name': c.country, 'rdf_uri': f'mld:Country_{c.country.replace(" ", "_")}'}
                )
                if c_id in node_ids:
                    add_edge(c_id, cntry_id, "locatedIn")

            for acc in c.accounts:
                a_id = f"Acc_{acc.account_number}"
                if not entity_type_filter or entity_type_filter in ['Account', 'All']:
                    add_node(
                        a_id, 
                        f"Acc-{acc.account_number[-4:]}", 
                        "Account", 
                        f"Account: {acc.account_number}<br>Type: {acc.account_type}<br>Balance: ${acc.balance:,.2f}", 
                        15,
                        props={'entity_id': acc.account_number, 'type': 'Account', 'account_type': acc.account_type, 'balance': f"${acc.balance:,.2f}", 'country': acc.country, 'rdf_uri': f'mld:Account_{acc.account_number}'}
                    )
                    if c_id in node_ids:
                        add_edge(c_id, a_id, "ownsAccount")

        # Transactions query
        tx_query = self.session.query(Transaction)
        if transaction_filter:
            tx_query = tx_query.filter(Transaction.transaction_id == transaction_filter)
        elif customer_filter:
            # Filter txs belonging to customer's accounts
            acc_nums = [a.account_number for c in customers for a in c.accounts]
            tx_query = tx_query.filter((Transaction.sender_account.in_(acc_nums)) | (Transaction.receiver_account.in_(acc_nums)))
        
        transactions = tx_query.limit(limit * 2).all()

        for tx in transactions:
            t_id = f"Tx_{tx.transaction_id}"
            group = "SuspiciousTransaction" if tx.suspicious else "Transaction"
            if not entity_type_filter or entity_type_filter in [group, 'Transaction', 'SuspiciousTransaction', 'All']:
                add_node(
                    t_id, 
                    f"${tx.amount:,.0f}", 
                    group, 
                    f"Tx ID: {tx.transaction_id}<br>Amount: ${tx.amount:,.2f}<br>Type: {tx.transaction_type}<br>Risk: {tx.risk_level} ({tx.risk_score})", 
                    12,
                    props={'entity_id': tx.transaction_id, 'type': group, 'amount': f"${tx.amount:,.2f}", 'currency': tx.currency, 'transaction_type': tx.transaction_type, 'sender_account': tx.sender_account, 'receiver_account': tx.receiver_account, 'sender_country': tx.sender_country, 'receiver_country': tx.receiver_country, 'risk_score': tx.risk_score, 'risk_level': tx.risk_level, 'suspicious': tx.suspicious, 'date': str(tx.transaction_date), 'rdf_uri': f'mld:Transaction_{tx.transaction_id}'}
                )

            s_acc = f"Acc_{tx.sender_account}"
            r_acc = f"Acc_{tx.receiver_account}"

            if s_acc in node_ids and t_id in node_ids:
                add_edge(s_acc, t_id, "sendsTransaction")
            if r_acc in node_ids and t_id in node_ids:
                add_edge(t_id, r_acc, "transfersTo")

            if tx.suspicious:
                risk_id = f"Risk_{tx.risk_level}"
                if not entity_type_filter or entity_type_filter in ['RiskLevel', 'All']:
                    add_node(
                        risk_id, 
                        tx.risk_level, 
                        "RiskLevel", 
                        f"Risk Level: {tx.risk_level}", 
                        18,
                        props={'entity_id': tx.risk_level, 'type': 'RiskLevel', 'name': tx.risk_level, 'rdf_uri': f'mld:{tx.risk_level}Risk'}
                    )
                    if t_id in node_ids:
                        add_edge(t_id, risk_id, "hasRiskLevel", color='#F5A623')

                pattern_name = tx.description or "Suspicious Pattern"
                pat_id = f"Pat_{tx.transaction_id}"
                if not entity_type_filter or entity_type_filter in ['Pattern', 'TransactionPattern', 'All']:
                    add_node(
                        pat_id, 
                        pattern_name[:20], 
                        "Pattern", 
                        f"Pattern: {pattern_name}", 
                        14,
                        props={'entity_id': pattern_name, 'type': 'TransactionPattern', 'name': pattern_name, 'rdf_uri': 'mld:TransactionPattern'}
                    )
                    if t_id in node_ids:
                        add_edge(t_id, pat_id, "exhibitsPattern", color='#A78BFA')

                # Add Alert node if alerts exist for this transaction
                if tx.alerts:
                    for al in tx.alerts[:2]:
                        al_id = f"Alert_{al.alert_id}"
                        if not entity_type_filter or entity_type_filter in ['Alert', 'All']:
                            add_node(
                                al_id,
                                f"Alert-{al.alert_id[-4:]}",
                                "Alert",
                                f"Alert: {al.alert_type}<br>Severity: {al.severity}<br>Status: {al.status}",
                                14,
                                props={'entity_id': al.alert_id, 'type': 'Alert', 'alert_type': al.alert_type, 'severity': al.severity, 'status': al.status, 'description': al.description, 'risk_score': al.risk_score, 'rdf_uri': f'mld:Alert_{al.alert_id}'}
                            )
                            if t_id in node_ids:
                                add_edge(t_id, al_id, "generatesAlert", color='#FF526A')

        return {
            'nodes': nodes,
            'edges': edges
        }
