from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models.cage import Cage
from ..models.user import User
from ..schemas.cage import CageCreate, CageRead


router = APIRouter(prefix="/cages", tags=["cages"])


@router.post("/", response_model=CageRead)
def create_cage(
    cage: CageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_cage = (
        db.query(Cage)
        .filter(Cage.user_id == current_user.id, Cage.cage_number == cage.cage_number)
        .first()
    )
    if existing_cage:
        raise HTTPException(status_code=400, detail="Cage number already exists")

    db_cage = Cage(**cage.model_dump(), user_id=current_user.id)
    db.add(db_cage)
    db.commit()
    db.refresh(db_cage)
    return db_cage


@router.get("/", response_model=list[CageRead])
def list_cages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Cage)
        .filter(Cage.user_id == current_user.id)
        .order_by(Cage.cage_number)
        .all()
    )
