
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# In-memory data storage
patients = []
patient_id_counter = 1

class Symptom:
    def __init__(self, name, severity):
        self.name = name
        self.severity = severity

class Patient:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.symptoms = []

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "symptoms": [{"name": s.name, "severity": s.severity} for s in self.symptoms]
        }

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/patients", methods=["GET"])
def get_patients():
    return jsonify([p.to_dict() for p in patients])

@app.route("/patients", methods=["POST"])
def add_patient():
    global patient_id_counter
    data = request.get_json()
    name = data.get("name")
    if name:
        patient = Patient(patient_id_counter, name)
        patients.append(patient)
        patient_id_counter += 1
        return jsonify(patient.to_dict()), 201
    return jsonify({"error": "Name is required"}), 400

@app.route("/patients/<int:patient_id>/symptoms", methods=["POST"])
def add_symptom(patient_id):
    data = request.get_json()
    name = data.get("name")
    severity = data.get("severity")
    patient = next((p for p in patients if p.id == patient_id), None)
    if patient and name and severity is not None:
        symptom = Symptom(name, severity)
        patient.symptoms.append(symptom)
        return jsonify({"message": "Symptom added"}), 200
    return jsonify({"error": "Invalid input"}), 400

@app.route("/patients/<int:patient_id>", methods=["DELETE"])
def delete_patient(patient_id):
    global patients
    patients = [p for p in patients if p.id != patient_id]
    return jsonify({"message": f"Patient {patient_id} deleted"}), 200

@app.route("/evaluate/<int:patient_id>", methods=["GET"])
def evaluate_patient(patient_id):
    patient = next((p for p in patients if p.id == patient_id), None)
    if patient:
        if any(s.severity >= 7 for s in patient.symptoms):
            return jsonify({"status": "Critical - needs immediate attention"})
        return jsonify({"status": "Stable"})
    return jsonify({"error": "Patient not found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
