# Money Laundering Detection System using Ontology

A full-stack, enterprise-grade academic research web application for financial crime analytics, transaction pattern detection, and ontology-based automated reasoning.

---

## 1. Project Overview

The **Money Laundering Detection System using Ontology** analyzes financial transaction streams and flags potentially suspicious activities using a hybrid multi-engine architecture:
- **Rule-Based Detection Engine** (10 modular rules)
- **Ontology Reasoning Engine** (OWL/RDF semantic inferences)
- **Knowledge Graph Visualizer** (Vis.js interactive network)
- **Machine Learning Anomaly Detector** (Isolation Forest)
- **Transparent Risk Engine** (0-100 score breakdown with explicit explainability)
- **Automated Case Alert & Workflow System**
- **PDF & CSV Regulatory Reporting Engine**

> **Academic Disclaimer:** This system is built for academic and research evaluation purposes. Detected transactions are explicitly classified as **potentially suspicious** for review and do not represent legally confirmed criminal activity.

---

## 2. Key Features

- **Multi-Engine Hybrid Analytics:** Combines deterministic rules, machine learning statistical anomaly detection, and OWL semantic reasoning.
- **Explainable AI (XAI):** Clear breakdown explaining *WHY* every transaction received its risk score, including rule evidence, score factors, and ontology antecedents.
- **Protégé-Compatible OWL Ontology:** Fully valid `MoneyLaunderingDetectionOntology` loaded via RDFLib and Owlready2.
- **Interactive Knowledge Graph:** Explore nodes (`Customer`, `Account`, `Transaction`, `Pattern`, `RiskLevel`, `Country`) and directed RDF relationship links.
- **Full Case Triage & Alerts:** Triage alerts through workflow statuses (*Open*, *Under Review*, *Resolved*, *False Positive*) with audit logging.
- **Batch CSV Import Pipeline:** Drag-and-drop CSV upload with validation, data cleaning, database persistence, and live import summary metrics.
- **Regulatory PDF & CSV Reports:** Download PDF Suspicious Activity Reports (SAR), Customer Risk Audits (ReportLab), and CSV datasets.
- **Professional Cybersecurity UI:** Built with Bootstrap 5 in a dark navy financial analytics theme with interactive Chart.js charts.

---

## 3. Technology Stack

- **Backend Framework:** Python 3.11+ / 3.14+, Flask
- **ORM & Database:** SQLAlchemy, SQLite (MySQL compatible)
- **Ontology & RDF Processing:** Owlready2, RDFLib, SPARQL, Protégé OWL 2 XML
- **Machine Learning & Analytics:** Scikit-learn (Isolation Forest), Pandas, NumPy
- **Report Generation:** ReportLab (PDF), CSV
- **Frontend UI & Visualizations:** HTML5, CSS3, Bootstrap 5, FontAwesome 6, Chart.js, Vis.js Network
- **Testing Suite:** Pytest / Unittest

---

## 4. System Architecture

```
CSV / Transaction Data ──► Data Cleaner ──► SQLite Database ──► RDF Ontology Graph
                                                 │                   │
                                                 ▼                   ▼
                                      Rule Engine (10 Rules)   Ontology Reasoner
                                      + ML Isolation Forest
                                                 │                   │
                                                 └─────────┬─────────┘
                                                           ▼
                                                Transparent Risk Engine
                                                           │
                                                           ▼
                                                Alert Generation Engine
                                                           │
                                                           ▼
                                          Executive Dashboard & PDF/CSV Reports
```

---

## 5. Installation & Setup

### Prerequisites
- Python 3.11 or higher
- Git

### 1. Clone & Environment Setup
```bash
# Clone the repository
git clone https://github.com/example/Money-Laundering-Detection-System.git
cd Money-Laundering-Detection-System

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 6. Running the Application

To start the Flask application:

```bash
python app.py
```

The system automatically initializes:
1. SQLite database tables (`money_laundering.db`).
2. Synthetic demo data (500 customers, 700 accounts, 5,000 transactions, realistic suspicious patterns).
3. Trains the Isolation Forest ML model (`ml/model.pkl`).
4. Loads and populates the RDF/OWL knowledge graph (`ontology/laundering_ontology.owl`).
5. Launches Flask web server at `http://127.0.0.1:5000`.

---

## 7. Demo Credentials

- **URL:** `http://127.0.0.1:5000/login`
- **Username:** `admin`
- **Password:** `admin123`

---

## 8. CSV Upload Format

When importing transaction data via `/import`, your CSV should follow this header structure:

```csv
transaction_id,sender_account,receiver_account,amount,currency,transaction_type,transaction_date,sender_country,receiver_country,description
TXN-90001,ACC100001,ACC100002,1250.00,USD,WIRE,2026-10-01 10:15:00,United States,United States,Consulting Payment
TXN-90002,ACC100003,ACC100004,9500.00,USD,WIRE,2026-10-01 11:00:00,United States,Panama,Structured transfer
```

Sample file included at: `data/transactions.csv`.

---

## 9. API Endpoints Reference

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/api/dashboard/stats` | Returns executive summary metrics and chart datasets. |
| `GET` | `/api/transactions` | Paginated and filtered transactions registry. |
| `GET` | `/api/transactions/<id>` | Single transaction detail payload. |
| `POST` | `/api/analyze/<id>` | Re-evaluates detection pipeline on transaction. |
| `GET` | `/api/customers` | Paginated customer profiles with risk ratings. |
| `GET` | `/api/customers/<id>` | Customer profile details. |
| `GET` | `/api/alerts` | Paginated alert queue. |
| `POST` | `/api/alerts/<id>/status` | Updates alert workflow status (*Under Review*, *Resolved*, *False Positive*). |
| `GET` | `/api/ontology/classes` | Returns OWL ontology class taxonomy. |
| `GET` | `/api/ontology/graph` | Returns JSON nodes and edges for Vis.js knowledge graph. |
| `POST` | `/api/upload` | Processes uploaded CSV transaction file. |

---

## 10. Automated Testing

Run unit and integration tests:

```bash
python -m unittest discover tests
# or using pytest
pytest
```

Includes 15+ automated unit tests covering detection rules, ontology loading, semantic reasoning, risk scoring, database models, and web route APIs.

---

## 11. Screenshots Overview

1. **Executive Dashboard:** 7 stat cards and 7 interactive charts (Timeline, Suspicious Pie, Risk Dist, Alert Severity, Transaction Types, Jurisdiction Activity, Top Risky Customers).
2. **Transaction Investigation Page:** Clear explainability section showing why a transaction was flagged, score breakdown, rule matrix, and ontology inferences.
3. **Ontology Knowledge Graph Explorer:** Vis.js interactive network rendering node links (`Customer` -> `Account` -> `Transaction` -> `Pattern` -> `RiskLevel`).
4. **Alerts Triage Queue:** Filterable case table with status update actions and audit logging.

---

## 12. Limitations & Future Enhancements

### Limitations
- Protégé OWL reasoning runs in-memory using RDFLib graph bindings.
- ML Anomaly detection utilizes unsupervised Isolation Forest; supervised training requires labelled real-world bank datasets (e.g. Elliptic / PaySim).

### Future Enhancements
- Integration with Neo4j graph database for billion-node graph traversals.
- SWRL rule engine integration via Pellet or HermiT.
- Real-time Kafka / WebSockets transaction stream ingestion.
