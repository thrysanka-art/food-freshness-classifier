"""
model.py — Food Freshness Classifier
Lazy-loads the ViT model on first call so uvicorn starts up instantly.
"""

from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch

MODEL_NAME = "google/vit-base-patch16-224"

# Module-level singletons — populated on first predict call
_processor = None
_model     = None


def _load_model():
    """Load model and processor once, cache in module globals."""
    global _processor, _model
    if _processor is None or _model is None:
        print("[model] Loading ViT model…")
        _processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
        _model     = AutoModelForImageClassification.from_pretrained(MODEL_NAME)
        _model.eval()
        print("[model] Model ready ✓")


def predict_freshness(image: Image.Image) -> dict:
    """
    Run an image through the ViT model and return a freshness label + confidence.

    Returns:
        dict: { "label": "Fresh"|"Okay"|"Avoid", "confidence": float 0-1 }
    """
    _load_model()   # no-op after first call

    if image.mode != "RGB":
        image = image.convert("RGB")

    inputs = _processor(images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = _model(**inputs)

    probs      = torch.softmax(outputs.logits, dim=1)
    confidence = float(probs.max().item())

    if confidence > 0.85:
        label = "Fresh"
    elif confidence > 0.60:
        label = "Okay"
    else:
        label = "Avoid"

    return {"label": label, "confidence": round(confidence, 4)}