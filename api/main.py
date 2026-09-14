# ================================================
# Phase 6 — FastAPI Campaign Response API
# ================================================

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import joblib
import numpy as np
import pandas as pd
import os

# ================================================
# Load models
# ================================================

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH  = os.path.join(BASE_DIR, '..', 'models', 'campaign_model_v1.joblib')
SCALER_PATH = os.path.join(BASE_DIR, '..', 'models', 'scaler_v1.joblib')

try:
    model  = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    print("✅ Models loaded!")
except Exception as e:
    print(f"❌ Error loading models: {e}")
    model  = None
    scaler = None

# ================================================
# Create FastAPI app
# ================================================

app = FastAPI(
    title="Retail Customer Analytics API",
    description="Predicts if a customer will respond to a marketing campaign",
    version="1.0.0"
)

# Serve static files
app.mount("/static",
          StaticFiles(directory=os.path.join(BASE_DIR, '..', 'app', 'static')),
          name="static")

# ================================================
# Input schema
# ================================================

class CustomerData(BaseModel):
    Total_Spending:     float = Field(..., example=1500.0)
    Purchase_Frequency: float = Field(..., example=4.0)
    Recency:            float = Field(..., example=30.0)
    Unique_Products:    float = Field(..., example=25.0)
    Avg_Basket_Size:    float = Field(..., example=375.0)
    nps:                float = Field(..., example=7.0)
    n_comp:             float = Field(..., example=1.0)
    n_communications:   float = Field(..., example=5.0)
    loyalty:            int   = Field(..., example=1)

# ================================================
# Routes
# ================================================

@app.get("/")
def home():
    return {
        "message":   "Retail Customer Analytics API",
        "version":   "1.0.0",
        "dashboard": "/dashboard",
        "docs":      "/docs"
    }

@app.get("/health")
def health():
    return {
        "status":        "healthy",
        "model_loaded":  model is not None,
        "scaler_loaded": scaler is not None
    }

@app.get("/dashboard", response_class=FileResponse)
def dashboard():
    html_path = os.path.join(BASE_DIR, '..', 'app', 'static', 'index.html')
    return FileResponse(html_path)

@app.post("/segment")
def segment():
    return {"message": "Customer segmentation endpoint - coming soon"}

@app.post("/predict")
def predict(customer: CustomerData):
    if model is None or scaler is None:
        raise HTTPException(
            status_code=500,
            detail="Models not loaded!"
        )

    try:
        # Validate inputs
        if not (0 <= customer.nps <= 10):
            raise HTTPException(status_code=422, 
                              detail="NPS must be between 0 and 10")
        if customer.loyalty not in [0, 1]:
            raise HTTPException(status_code=422, 
                              detail="Loyalty must be 0 or 1")
        if customer.Total_Spending < 0:
            raise HTTPException(status_code=422, 
                              detail="Total Spending cannot be negative")

        # Create dataframe
        input_df = pd.DataFrame([customer.dict()])

        # Scale and predict
        input_scaled = scaler.transform(input_df)
        prediction   = model.predict(input_scaled)[0]
        probability  = model.predict_proba(input_scaled)[0]

        return {
            "prediction":      int(prediction),
            "predicted_class": "Will Respond" if prediction == 1 else "Will Not Respond",
            "probability_yes": round(float(probability[1]), 4),
            "probability_no":  round(float(probability[0]), 4),
            "confidence":      f"{max(probability)*100:.1f}%"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))