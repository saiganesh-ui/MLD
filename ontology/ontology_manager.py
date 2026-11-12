import os
import rdflib
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD
from config import Config

NS = Namespace("http://www.semanticweb.org/ontologies/2026/MoneyLaunderingDetectionOntology#")

class OntologyManager:
    def __init__(self, ontology_path=None):
        self.ontology_path = ontology_path or Config.ONTOLOGY_PATH
        self.graph = Graph()
        self.ns = NS
        self.graph.bind("", self.ns)
        self.graph.bind("mld", self.ns)
        self.graph.bind("owl", OWL)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.load_ontology()

    def load_ontology(self):
        if os.path.exists(self.ontology_path):
            try:
                self.graph.parse(self.ontology_path, format="xml")
            except Exception as e:
                print(f"Error parsing ontology file: {e}")
        else:
            print(f"Ontology file not found at {self.ontology_path}, creating blank graph.")

    def save_ontology(self):
        os.makedirs(os.path.dirname(self.ontology_path), exist_ok=True)
        self.graph.serialize(destination=self.ontology_path, format="xml")

    def populate_from_db(self, customers, accounts, transactions, high_risk_countries=None):
        """Populates RDF graph from DB entities."""
        high_risk_countries = high_risk_countries or Config.HIGH_RISK_COUNTRIES

        # Add High Risk Countries
        for country in high_risk_countries:
            country_uri = URIRef(self.ns[f"Country_{country.replace(' ', '_')}"])
            self.graph.add((country_uri, RDF.type, self.ns.HighRiskCountry))
            self.graph.add((country_uri, self.ns.countryName, Literal(country, datatype=XSD.string)))

        # Customers
        for c in customers:
            c_uri = URIRef(self.ns[f"Customer_{c.customer_id}"])
            self.graph.add((c_uri, RDF.type, self.ns.Customer))
            self.graph.add((c_uri, self.ns.customerId, Literal(c.customer_id, datatype=XSD.string)))
            country_uri = URIRef(self.ns[f"Country_{c.country.replace(' ', '_')}"])
            self.graph.add((c_uri, self.ns.locatedIn, country_uri))

        # Accounts
        for a in accounts:
            a_uri = URIRef(self.ns[f"Account_{a.account_number}"])
            c_uri = URIRef(self.ns[f"Customer_{a.customer_id}"])
            self.graph.add((a_uri, RDF.type, self.ns.Account))
            self.graph.add((a_uri, self.ns.accountNumber, Literal(a.account_number, datatype=XSD.string)))
            self.graph.add((c_uri, self.ns.ownsAccount, a_uri))

        # Transactions
        for t in transactions:
            t_uri = URIRef(self.ns[f"Transaction_{t.transaction_id}"])
            sender_uri = URIRef(self.ns[f"Account_{t.sender_account}"])
            receiver_uri = URIRef(self.ns[f"Account_{t.receiver_account}"])

            self.graph.add((t_uri, RDF.type, self.ns.Transaction))
            self.graph.add((t_uri, self.ns.transactionId, Literal(t.transaction_id, datatype=XSD.string)))
            self.graph.add((t_uri, self.ns.transactionAmount, Literal(float(t.amount), datatype=XSD.double)))
            self.graph.add((t_uri, self.ns.transactionDate, Literal(str(t.transaction_date), datatype=XSD.string)))

            self.graph.add((sender_uri, self.ns.sendsTransaction, t_uri))
            self.graph.add((receiver_uri, self.ns.receivesTransaction, t_uri))
            self.graph.add((sender_uri, self.ns.transfersTo, receiver_uri))

            if t.suspicious:
                self.graph.add((t_uri, RDF.type, self.ns.SuspiciousTransaction))

    def execute_sparql(self, query_str):
        """Executes raw SPARQL query against the graph."""
        return self.graph.query(query_str)
