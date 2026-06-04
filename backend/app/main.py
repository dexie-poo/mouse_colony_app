from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.models import Cage, Mouse
from app.routes import cages, mice


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mouse Colony Management API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mice.router)
app.include_router(cages.router)


@app.get("/")
def read_root():
    return {"message": "Mouse Colony Management API"}
