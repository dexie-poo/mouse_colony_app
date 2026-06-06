from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from .models import Analysis, Cage, Mating, Mouse, User
from .routes import analyses, auth, cages, matings, mice
from .schema_upgrades import apply_v3_schema_upgrades


Base.metadata.create_all(bind=engine)
apply_v3_schema_upgrades(engine)

app = FastAPI(title="Mouse Colony Management API", version="0.3.0")
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
app.include_router(analyses.router)
app.include_router(auth.router)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/api/health")
def read_health():
    return {"message": "Mouse Colony Management API"}


@app.get("/")
def read_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")
