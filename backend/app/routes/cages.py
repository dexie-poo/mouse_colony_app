from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.cage import Cage
from ..schemas.cage import CageCreate, CageRead


router = APIRouter(prefix="/cages", tags=["cages"])


@router.post("/", response_model=CageRead)
def create_cage(cage: CageCreate, db: Session = Depends(get_db)):
    existing_cage = db.query(Cage).filter(Cage.cage_number == cage.cage_number).first()
    if existing_cage:
        raise HTTPException(status_code=400, detail="Cage number already exists")

    db_cage = Cage(**cage.model_dump())
    db.add(db_cage)
    db.commit()
    db.refresh(db_cage)
    return db_cage


@router.get("/", response_model=list[CageRead])
def list_cages(db: Session = Depends(get_db)):
    return db.query(Cage).order_by(Cage.cage_number).all()
