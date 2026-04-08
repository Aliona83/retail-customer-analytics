from fastapi import FastAPI

app = FastAPI(title="Retail Customer Analytics API")

@app.get("/")
def home():
    return {"message": "Retail Customer Analytics API is running!"}

@app.post("/segment")
def segment():
    return {"message": "Customer segmentation endpoint - coming soon"}

@app.post("/campaign")
def campaign():
    return {"message": "Campaign response endpoint - coming soon"}
