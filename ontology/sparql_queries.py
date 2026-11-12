# SPARQL Query Templates for Money Laundering Detection Ontology

GET_ALL_SUSPICIOUS_TRANSACTIONS = """
PREFIX mld: <http://www.semanticweb.org/ontologies/2026/MoneyLaunderingDetectionOntology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?tx ?txId ?amount WHERE {
    ?tx rdf:type mld:SuspiciousTransaction .
    ?tx mld:transactionId ?txId .
    ?tx mld:transactionAmount ?amount .
}
"""

GET_HIGH_RISK_CROSS_BORDER = """
PREFIX mld: <http://www.semanticweb.org/ontologies/2026/MoneyLaunderingDetectionOntology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?tx ?senderAccount ?receiverAccount ?amount WHERE {
    ?tx rdf:type mld:Transaction .
    ?senderAccount mld:sendsTransaction ?tx .
    ?receiverAccount mld:receivesTransaction ?tx .
    ?tx mld:transactionAmount ?amount .
    FILTER(?amount > 10000)
}
"""

GET_CUSTOMER_KNOWLEDGE_GRAPH = """
PREFIX mld: <http://www.semanticweb.org/ontologies/2026/MoneyLaunderingDetectionOntology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?customer ?account ?transaction ?receiverAccount WHERE {
    ?customer mld:ownsAccount ?account .
    ?account mld:sendsTransaction ?transaction .
    ?transaction mld:transfersTo ?receiverAccount .
}
"""

GET_RAPID_TRANSFER_CHAINS = """
PREFIX mld: <http://www.semanticweb.org/ontologies/2026/MoneyLaunderingDetectionOntology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?accA ?tx1 ?accB ?tx2 ?accC WHERE {
    ?accA mld:sendsTransaction ?tx1 .
    ?accB mld:receivesTransaction ?tx1 .
    ?accB mld:sendsTransaction ?tx2 .
    ?accC mld:receivesTransaction ?tx2 .
    FILTER(?accA != ?accC)
}
"""
