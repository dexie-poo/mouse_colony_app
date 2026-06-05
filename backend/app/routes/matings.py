from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.mating import Mating
from app.models.mouse import Mouse
from app.schemas.mating import MatingCreate, MatingRead


router = APIRouter(prefix="/matings", tags=["matings"])


def ensure_mouse_exists(db: Session, mouse_id: int, role: str):
    mouse = db.get(Mouse, mouse_id)
    if mouse is None:
        raise HTTPException(status_code=404, detail=f"{role} mouse not found")
    return mouse


@router.post("/", response_model=MatingRead)
def create_mating(mating: MatingCreate, db: Session = Depends(get_db)):
    ensure_mouse_exists(db, mating.sire_id, "Sire")
    ensure_mouse_exists(db, mating.dam_id, "Dam")

    db_mating = Mating(**mating.model_dump())
    db.add(db_mating)
    db.commit()
    db.refresh(db_mating)
    return db_mating


@router.get("/", response_model=list[MatingRead])
def list_matings(db: Session = Depends(get_db)):
    return db.query(Mating).order_by(Mating.id.desc()).all()


@router.get("/mouse/{mouse_id}", response_model=list[MatingRead])
def list_matings_for_mouse(mouse_id: int, db: Session = Depends(get_db)):
    ensure_mouse_exists(db, mouse_id, "Selected")
    return (
        db.query(Mating)
        .filter(or_(Mating.sire_id == mouse_id, Mating.dam_id == mouse_id))
        .order_by(Mating.id.desc())
        .all()
    )
