from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

# --- MongoDB Configuration ---
# NOTE: Replace with your actual MongoDB connection string
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "DataRedaction"
COLLECTION_NAME = "EmployeeData"

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

## Flask Route for Redaction Demo

@app.route('/data/<persona_id>', methods=['GET'])
def get_redacted_data(persona_id):
    """
    Fetches data using the $redact pipeline based on the provided persona_id.
    """
    
    # 1. Input Validation (Ensure it's a valid persona)
    if persona_id not in ["P1", "P2", "P3"]:
        return jsonify({"error": "Invalid persona ID. Use P1, P2, or P3."}), 400

    print(f"\n--- Running query for Persona: {persona_id} ---")

    # 2. Define the MongoDB Aggregation Pipeline
    pipeline = [
        {
            "$redact": {
                "$cond": {
                    # Check if the user's persona ID is present in the current level's access_roles
                    "if": { "$in": [ persona_id, "$access_roles" ] },
                    
                    # If true: Keep this level and check sub-levels
                    "then": "$$DESCEND", 
                    
                    # If false: Prune (redact) this level and all contents
                    "else": "$$PRUNE"
                }
            }
        }
    ]

    # 3. Execute the Pipeline
    try:
        # Use .aggregate() which returns a cursor
        results_cursor = collection.aggregate(pipeline)
        
        # Convert the cursor results to a Python list
        redacted_data = list(results_cursor)
        
        # Convert MongoDB's ObjectId back to string for JSON serialization
        # (Though our sample uses integer IDs, it's good practice for real data)
        for doc in redacted_data:
            if '_id' in doc and not isinstance(doc['_id'], (int, str)):
                doc['_id'] = str(doc['_id'])

        # 4. Return the Redacted Data as JSON
        return jsonify({
            "persona": persona_id,
            "description": f"Redacted data view for {persona_id}",
            "data": redacted_data
        })

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "Database query failed.", "details": str(e)}), 500

if __name__ == '__main__':
    print("\n--- Flask Server Running ---")
    print("Try accessing these URLs in your browser:")
    print("Standard User (P1): http://127.0.0.1:5000/data/P1")
    print("Analyst (P2):       http://127.0.0.1:5000/data/P2")
    print("Administrator (P3): http://127.0.0.1:5000/data/P3")
    app.run(debug=True)
