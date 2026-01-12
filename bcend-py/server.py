from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)

# Load the saved model and vectorizer
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
