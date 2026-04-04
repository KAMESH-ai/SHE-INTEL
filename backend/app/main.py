from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.database import engine, Base
from app.ml.xgb_model import load_model
from app.routers import analysis, auth, periods, symptoms

Base.metadata.create_all(bind=engine)
load_model()

app = FastAPI(
    title="SHE-INTEL INDIA",
    description="Context-Aware Predictive Health Intelligence for Indian Women",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(periods.router)
app.include_router(symptoms.router)
app.include_router(analysis.router)

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


@app.get("/app", include_in_schema=False)
def frontend_app():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Frontend not found"}


@app.get("/app.js", include_in_schema=False)
def frontend_js():
    app_js = FRONTEND_DIR / "app.js"
    if app_js.exists():
        return FileResponse(app_js)
    return {"message": "Frontend asset not found"}


@app.get("/styles.css", include_in_schema=False)
def frontend_css():
    styles = FRONTEND_DIR / "styles.css"
    if styles.exists():
        return FileResponse(styles)
    return {"message": "Frontend asset not found"}


@app.get("/")
def root():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "message": "SHE-INTEL INDIA API",
        "status": "running",
        "frontend": "/app",
    }


@app.get("/api")
def api_root():
    return {
        "message": "SHE-INTEL INDIA API",
        "status": "running",
        "frontend": "/",
    }
