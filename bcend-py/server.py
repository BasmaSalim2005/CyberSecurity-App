from flask import Flask, request, jsonify
import joblib
import os

app = Flask(__name__)

# Load the saved model and 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to your model folder and file
MODEL_PATH = os.path.join(BASE_DIR, "model", "spam_model.joblib")
model = joblib.load("/model/spam_model.joblib")
vectorizer = joblib.load("/model/vectorizer.joblib")

@app.route("/analyze", methods=["POST"])
def analyze_text():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    X = vectorizer.transform([text])
    pred = model.predict(X)[0]
    prob = model.predict_proba(X)[0].max() * 100

    return jsonify({
        "classification": "spam" if pred == "spam" else "safe",
        "confidence": round(prob, 2)
    })

if __name__ == "__main__":
    app.run(port=5000)
