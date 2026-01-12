# backend.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import google.generativeai as genai
import password
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=".gitignore/.env")

app = FastAPI()

# Allow local frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # localhost frontend allowed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Configure Gemini API
genai.configure(api_key=os.getenv('my_key'))
MODEL_API_URL = "http://127.0.0.1:5000/analyze"  # Flask model

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "active_page": "home"})

@app.get("/phishing-detector", response_class=HTMLResponse)
async def phishing_detector(request: Request):
    return templates.TemplateResponse("phishing_detector.html", {"request": request, "active_page": "phishing-detector"})

@app.get("/password-checker", response_class=HTMLResponse)
async def password_checker(request: Request):
    return templates.TemplateResponse("password_checker.html", {"request": request, "active_page": "password-checker"})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "active_page": "about"})

@app.post("/analyze_full")
async def analyze_full(request: Request):
    data = await request.json()
    text = data.get("text", "")
    if not text:
        return {"error": "No text provided"}

    # Step 1 — Call Flask spam model
    try:
        model_res = requests.post(MODEL_API_URL, json={"text": text})
        model_json = model_res.json()
        classification = model_json.get("classification", "safe")
        confidence = model_json.get("confidence", 0)
    except Exception as e:
        return {"error": f"Flask API call failed: {e}"}

    # Step 2 — Gemini explanation
    prompt = (
        f"The following message was classified as '{classification}' "
        f"with {confidence}% confidence:\n\n{text}\n\n"
        "Explain in 2 lines and in simple terms why it might be considered spam or safe."
    )
    try:
        gemini_model = genai.GenerativeModel("gemini-2.5-flash")
        explanation_resp = gemini_model.generate_content(prompt)
        explanation = explanation_resp.text if hasattr(explanation_resp, "text") else str(explanation_resp)
    except Exception as e:
        explanation = f"Could not get explanation: {e}"

    return {
        "classification": classification,
        "confidence": confidence,
        "explanation": explanation,
    }

@app.post("/check_password")
async def check_password(request: Request):
    data = await request.json()
    pwd = data.get("password", "")
    if not pwd:
        return {"error": "No password provided"}

    # Step 1 — Calculate strength and entropy
    try:
        strength, entropy = password.check_pw_strength(pwd)
    except Exception as e:
        return {"error": f"Password check failed: {e}"}

    # Step 2 — Gemini explanation
    prompt = (
        f"The password has strength '{strength}' "
        f"with entropy {entropy:.2f}.\n\n"
        "Explain in 2 lines and in simple terms why this password is secure or not, "
        "and provide brief suggestions for improvement if needed."
    )
    try:
        gemini_model = genai.GenerativeModel("gemini-2.5-flash")
        explanation_resp = gemini_model.generate_content(prompt)
        explanation = explanation_resp.text if hasattr(explanation_resp, "text") else str(explanation_resp)
    except Exception as e:
        explanation = f"Could not get explanation: {e}"

    return {
        "strength": strength,
        "entropy": entropy,
        "explanation": explanation,
    }
