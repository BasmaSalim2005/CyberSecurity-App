from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import joblib
import os
from dotenv import load_dotenv
import google.generativeai as genai
import password

# =====================
# ENV & APP SETUP
# =====================

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================
# PATHS
# =====================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "bcend-py", "model", "spam_model.joblib")
VECTORIZER_PATH = os.path.join(BASE_DIR, "bcend-py", "model", "vectorizer.joblib")

# =====================
# LOAD ML MODEL
# =====================

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

# =====================
# STATIC + TEMPLATES
# =====================

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# =====================
# GEMINI CONFIG
# =====================

genai.configure(api_key=os.getenv("my_key"))

# =====================
# ROUTES
# =====================

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

    try:
        X = vectorizer.transform([text])
        pred = model.predict(X)[0]
        prob = model.predict_proba(X)[0].max() * 100
        classification = "spam" if pred == "spam" else "safe"
        confidence = round(prob, 2)
    except Exception as e:
        return {"error": f"ML model failed: {e}"}

    prompt = (
        f"The following message was classified as '{classification}' "
        f"with {confidence}% confidence:\n\n{text}\n\n"
        "Explain in 2 lines and in simple terms why it might be considered spam or safe."
    )

    try:
        gemini_model = genai.GenerativeModel("gemini-2.5-flash")
        explanation_resp = gemini_model.generate_content(prompt)
        explanation = explanation_resp.text
    except Exception as e:
        explanation = f"Gemini error: {e}"

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

    strength, entropy = password.check_pw_strength(pwd)

    prompt = (
        f"The password has strength '{strength}' "
        f"with entropy {entropy:.2f}.\n\n"
        "Explain in 2 lines and in simple terms why this password is secure or not."
    )

    try:
        gemini_model = genai.GenerativeModel("gemini-2.5-flash")
        explanation_resp = gemini_model.generate_content(prompt)
        explanation = explanation_resp.text
    except Exception as e:
        explanation = f"Gemini error: {e}"

    return {
        "strength": strength,
        "entropy": entropy,
        "explanation": explanation,
    }
