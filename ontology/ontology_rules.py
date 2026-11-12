"""
Ontology Rule Definitions and Concepts.
Provides formal semantic rule descriptions and mapping for money laundering patterns.
"""

ONTOLOGY_RULES = [
    {
        "id": "RULE_ONT_01",
        "name": "High-Risk Cross-Border Rapid Transfer Inference",
        "description": "IF Transaction amount > $10,000 AND involves HighRiskCountry AND rapid transfer chain THEN infer SuspiciousTransaction & HighRisk.",
        "antecedents": ["Transaction(t)", "hasAmount(t, >10k)", "involves(t, HighRiskCountry)", "exhibitsPattern(t, RapidTransfer)"],
        "consequent": "SuspiciousTransaction(t) ^ HighRisk(t)"
    },
    {
        "id": "RULE_ONT_02",
        "name": "Structuring / Smurfing Pattern Inference",
        "description": "IF multiple transactions from single account within 24h are between $8,000 and $9,999 THEN infer SmurfingPattern.",
        "antecedents": ["Account(a)", "sends(a, t1)", "sends(a, t2)", "amount(t1, 8k..10k)", "amount(t2, 8k..10k)", "timeDiff(t1,t2, <24h)"],
        "consequent": "exhibitsPattern(t1, SmurfingPattern) ^ SuspiciousTransaction(t1)"
    },
    {
        "id": "RULE_ONT_03",
        "name": "Circular Transaction Cycle Inference",
        "description": "IF funds transfer A -> B -> C -> A within window THEN infer CircularTransactionPattern & LayeringPattern.",
        "antecedents": ["transfersTo(A, B)", "transfersTo(B, C)", "transfersTo(C, A)"],
        "consequent": "exhibitsPattern(t, CircularTransactionPattern) ^ LayeringPattern(t)"
    },
    {
        "id": "RULE_ONT_04",
        "name": "Dormant Account Spike Inference",
        "description": "IF Account inactive > 90 days AND performs transaction > $25,000 THEN infer RapidSpike & MediumToHighRisk.",
        "antecedents": ["Account(a)", "inactiveDays(a, >90)", "transactionAmount(t, >25k)"],
        "consequent": "HighRisk(a) ^ SuspiciousTransaction(t)"
    }
]
