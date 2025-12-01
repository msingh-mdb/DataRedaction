# 🔒 MongoDB Field-Level Security Demo using $redact

This project demonstrates how to implement dynamic field-level security (FLS) in MongoDB using the powerful **`$redact`** aggregation pipeline operator.

The security logic is entirely embedded within the data itself, ensuring that only users with the appropriate permissions (roles) can view sensitive fields or sub-documents.

## ✨ Features

* **Dynamic Redaction:** Documents are filtered and fields are pruned based on the requesting user's role ID.
* **Role-Based Access Control (RBAC):** Three distinct user roles (`P1`, `P2`, `P3`) are defined, each with different visibility rules.
* **Embedded ACLs:** Access Control Lists (`access_roles` array) are embedded at various levels of the document structure (top-level, sub-document, array elements).
* **Python/Flask Interface:** A simple web application interface to easily test and visualize the redaction for each role.

## 👥 User Personas and Access Levels

The project uses three distinct personas to simulate different organizational roles:

| Persona ID | Role | Access Level Summary |
| :--- | :--- | :--- |
| **P1** | **Standard User** | Basic, non-sensitive public information only. |
| **P2** | **Analyst** | All P1 data plus internal summaries, financial data (but not secrets). |
| **P3** | **Administrator** | Full access to all fields, including highly sensitive and confidential data. |

## 🛠️ Requirements

* Python 3.x
* MongoDB
* Import Data into collection using data.json 

### Python Dependencies

Install the required Python packages:

```bash
pip install flask pymongo
```

### Update your MongoDB Config in the file app.py

```# --- MongoDB Configuration ---
# NOTE: Replace with your actual MongoDB connection string
MONGO_URI = 'mongodb+srv://user:password@mydbmongodb.net/'
DATABASE_NAME = "DataRedaction"
COLLECTION_NAME = "EmployeeData"
```

## 🔎 The Core Logic: The $redact Pipeline
Data redaction happens in the single ```$redact``` stage within the MongoDB aggregation pipeline.

The pipeline dynamically constructs an access check based on the persona ID passed from the backend:
``` // Example used in app.py (where [persona_id] is 'P1', 'P2', etc.)
[
  {
    "$redact": {
      "$cond": {
        // CONDITION: Does the persona ID exist in the document's 'access_roles' array?
        "if": { "$in": [ "[persona_id]", "$access_roles" ] },
        
        // THEN: Keep the current level, but continue checking lower levels (sub-documents/arrays)
        "then": "$$DESCEND", 
        
        // ELSE: Prune (remove) this field/sub-document and stop checking its contents
        "else": "$$PRUNE"
      }
    }
  }
]
```

## 🖥️ Execute and Test the Demo
Run the application and test the different persona views to observe the redaction effect.

### Run the App
In your terminal, navigate to the directory containing app.py and execute:

```bash
python app.py
```

### Test Endpoints
The server will start on port 5000. Open your web browser or use a REST client and navigate to the following URLs to see the data retrieved for each persona:
* **P1 (Standard User)**: http://127.0.0.1:5000/data/P1 (Expect sensitive fields like financial_data to be entirely missing.)
* **P2 (Analyst)**: http://127.00.1:5000/data/P2 (Expect to see financial figures, but highly sensitive fields like internal_code will be removed/redacted.)
* **P3 (Administrator)**: http://127.0.0.1:5000/data/P3 (Expect to see the complete, unredacted JSON for all 10 documents.)

### Sample test Document
```
{
    "_id": 1,
    "title": "Q3 Sales Report",
    "access_roles": ["P1", "P2", "P3"], // P1 can see the title
    "status": "Final",
    "year": 2025,
    "general_summary": "Sales exceeded targets by 5%.",
    "financial_data": {
      "access_roles": ["P2", "P3"], // Only P2/P3 can view this section
      "gross_revenue": 1500000,
      "net_profit": 450000,
      "internal_code": {
        "access_roles": ["P3"], // Only P3 can view this
        "secret": "S-12345"
      }
    }
  }
```
## Output for P1 would be:
```
{
     "_id": 1,
      "access_roles": ["P1","P2", "P3"],
      "general_summary": "Sales exceeded targets by 5%.",
      "status": "Final",
      "title": "Q3 Sales Report",
      "year": 2025
}
```
## Output for P2 would be:
```
{
      "_id": 1,
      "access_roles": ["P1","P2", "P3"],
      "financial_data": {
        "access_roles": ["P2", "P3"],
        "gross_revenue": 1500000,
        "net_profit": 450000
      },
      "general_summary": "Sales exceeded targets by 5%.",
      "status": "Final",
      "title": "Q3 Sales Report",
      "year": 2025
}
```

## Output for P3 would be:
```
{
      "_id": 1,
      "access_roles": ["P1","P2", "P3"],
      "financial_data": {
        "access_roles": ["P2", "P3"],
        "gross_revenue": 1500000,
        "internal_code": {
          "access_roles": ["P3"],
          "secret": "S-12345"
        },
        "net_profit": 450000
      },
      "general_summary": "Sales exceeded targets by 5%.",
      "status": "Final",
      "title": "Q3 Sales Report",
      "year": 2025
}
```
