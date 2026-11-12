# MoneyLaunderingDetectionOntology Documentation

## 1. Overview
The **MoneyLaunderingDetectionOntology** is a formal Web Ontology Language (OWL 2) taxonomy developed for semantic financial crime reasoning and automated pattern inference in money laundering detection systems. It is fully compatible with Protégé 5.x.

**Ontology IRI:** `http://www.semanticweb.org/ontologies/2026/MoneyLaunderingDetectionOntology#`

---

## 2. Class Hierarchy

```
owl:Thing
├── Customer
│   └── ShellEntity
├── Account
├── Transaction
│   ├── SuspiciousTransaction
│   └── NormalTransaction
├── Alert
├── RiskLevel
│   ├── LowRisk
│   ├── MediumRisk
│   └── HighRisk
├── Country
│   └── HighRiskCountry
└── TransactionPattern
    ├── SmurfingPattern
    ├── LayeringPattern
    ├── CircularTransactionPattern
    ├── RapidTransferPattern
    └── CrossBorderPattern
```

---

## 3. Object Properties

| Property Name | Domain | Range | Description |
|:---|:---|:---|:---|
| `ownsAccount` | `Customer` | `Account` | Relates a customer to an account they hold. |
| `performsTransaction` | `Customer` | `Transaction` | Relates a customer to executed transactions. |
| `sendsTransaction` | `Account` | `Transaction` | Relates originating account to outbound transaction. |
| `receivesTransaction` | `Account` | `Transaction` | Relates beneficiary account to inbound transaction. |
| `transfersTo` | `Account` | `Account` | Directed relationship indicating monetary flow between accounts. |
| `locatedIn` | `Customer` | `Country` | Geographic jurisdiction of the entity. |
| `hasRiskLevel` | `Transaction` / `Customer` | `RiskLevel` | Risk classification binding. |
| `generatesAlert` | `Transaction` | `Alert` | Binds triggered alert to suspicious transaction. |
| `exhibitsPattern` | `Transaction` | `TransactionPattern` | Links transaction to detected money laundering topology. |
| `involvesCountry` | `Transaction` | `Country` | Binds transaction to involved foreign jurisdiction. |

---

## 4. Data Properties

- `customerId` (`xsd:string`)
- `accountNumber` (`xsd:string`)
- `transactionId` (`xsd:string`)
- `transactionAmount` (`xsd:double`)
- `transactionDate` (`xsd:string`)
- `currency` (`xsd:string`)
- `transactionType` (`xsd:string`)
- `riskScore` (`xsd:double`)
- `countryName` (`xsd:string`)
- `alertStatus` (`xsd:string`)

---

## 5. Reasoning Rules & Semantic Inferences

### Rule 1: High-Risk Jurisdiction Rapid Transfer
```
Transaction(?t) ^ transactionAmount(?t, ?a) ^ (?a >= 10000) ^ sendsTransaction(?acc1, ?t) ^ receivesTransaction(?acc2, ?t) ^ locatedIn(?cust1, ?c) ^ HighRiskCountry(?c) -> SuspiciousTransaction(?t) ^ HighRisk(?t)
```

### Rule 2: Structuring / Smurfing Pattern
```
Account(?a) ^ sendsTransaction(?a, ?t1) ^ sendsTransaction(?a, ?t2) ^ transactionAmount(?t1, ?am1) ^ (?am1 >= 8000) ^ (?am1 <= 9999) -> exhibitsPattern(?t1, SmurfingPattern) ^ SuspiciousTransaction(?t1)
```

---

## 6. SPARQL Sample Query

```sparql
PREFIX mld: <http://www.semanticweb.org/ontologies/2026/MoneyLaunderingDetectionOntology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?tx ?senderAccount ?receiverAccount ?amount WHERE {
    ?tx rdf:type mld:SuspiciousTransaction .
    ?senderAccount mld:sendsTransaction ?tx .
    ?receiverAccount mld:receivesTransaction ?tx .
    ?tx mld:transactionAmount ?amount .
}
```
