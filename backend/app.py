"""
app.py — FastAPI backend for Food Freshness Classifier
Run from project root:  uvicorn backend.app:app --reload
"""
#uvicorn backend.app:app --reload

import sys
import os

# Ensure the backend folder is on the Python path so `model` can be imported
# regardless of where uvicorn is launched from.
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import io

from model import predict_freshness   # local import (path fixed above)
from chatbot import get_chat_response  # built-in food-safety chatbot

# ── App setup ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Food Freshness Classifier API",
    description="Classifies food freshness using a pretrained ViT model.",
    version="2.0.0",
)

# Allow Streamlit (any localhost origin) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "healthy", "model": "google/vit-base-patch16-224"}


# ── Predict endpoint ───────────────────────────────────────────────────────────
@app.post("/predict")
async def predict_api(file: UploadFile = File(...)):
    """
    Accepts an image upload and returns a freshness prediction.

    Response JSON:
        {
            "label":      "Fresh" | "Okay" | "Avoid",
            "confidence": 0.0 – 1.0
        }
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type — please upload an image (JPG/PNG).")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        result = predict_freshness(image)
        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")


# ── Chat models ────────────────────────────────────────────────────────────────
class ChatMessage(BaseModel):
    role: str   # "user" | "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


# ── Chat endpoint ──────────────────────────────────────────────────────────────
@app.post("/chat")
def chat_api(req: ChatRequest):
    """
    Returns a food-safety chatbot reply.
    No external API required — fully self-contained knowledge base.
    """
    if not req.message.strip():
        return JSONResponse(content={"reply": "Please type a message!"})
    try:
        history = [{"role": m.role, "content": m.content} for m in req.history]
        reply = get_chat_response(req.message, history)
        return JSONResponse(content={"reply": reply})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat error: {exc}")