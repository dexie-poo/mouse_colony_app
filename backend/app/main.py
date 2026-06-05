from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from .models import Cage, Mating, Mouse
from .routes import cages, matings, mice


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mouse Colony Management API", version="0.2.0")
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mice.router)
app.include_router(cages.router)
app.include_router(matings.router)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/api/health")
def read_health():
    return {"message": "Mouse Colony Management API"}


@app.get("/")
def read_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")
