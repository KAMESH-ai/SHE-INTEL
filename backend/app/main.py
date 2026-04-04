from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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


@app.get("/")
def root():
    return {"message": "SHE-INTEL INDIA API", "status": "running"}
