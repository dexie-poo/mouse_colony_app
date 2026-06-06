from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models.mating import Mating
from ..models.mouse import Mouse
from ..models.user import User
from ..schemas.mating import MatingCreate, MatingRead


router = APIRouter(prefix="/matings", tags=["matings"])


def ensure_mouse_exists(db: Session, mouse_id: int, role: str, user_id: int):
    mouse = (
        db.query(Mouse)
        .filter(Mouse.id == mouse_id, Mouse.user_id == user_id)
        .first()
    )
    if mouse is None:
        raise HTTPException(status_code=404, detail=f"{role} mouse not found")
    return mouse


def create_kept_pup_mice(db: Session, mating: MatingCreate, user_id: int):
    kept_mouse_ids = []
    litter_dob = mating.litter_dob
    genotype = mating.kept_pup_genotype or mating.pup_genotypes or "Unknown"

    pup_specs = [
        ("Male", mating.kept_male_pups or 0),
        ("Female", mating.kept_female_pups or 0),
    ]
    for gender, count in pup_specs:
        for _ in range(count):
            mouse = Mouse(
                user_id=user_id,
                genotype=genotype,
                gender=gender,
                dob=litter_dob,
                remark=f"Kept pup from mating record",
            )
            db.add(mouse)
            db.flush()
            kept_mouse_ids.append(str(mouse.id))

    return ",".join(kept_mouse_ids) if kept_mouse_ids else None


@router.post("/", response_model=MatingRead)
def create_mating(
    mating: MatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_mouse_exists(db, mating.sire_id, "Sire", current_user.id)
    ensure_mouse_exists(db, mating.dam_id, "Dam", current_user.id)

    payload = mating.model_dump()
    db_mating = Mating(**payload, user_id=current_user.id)
    db.add(db_mating)
    if mating.keep_litter:
        kept_mouse_ids = create_kept_pup_mice(db, mating, current_user.id)
        db_mating.kept_mouse_ids = kept_mouse_ids
    db.commit()
    db.refresh(db_mating)
    return db_mating


@router.get("/", response_model=list[MatingRead])
def list_matings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Mating)
        .filter(Mating.user_id == current_user.id)
        .order_by(Mating.id.desc())
        .all()
    )


@router.get("/mouse/{mouse_id}", response_model=list[MatingRead])
def list_matings_for_mouse(
    mouse_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_mouse_exists(db, mouse_id, "Selected", current_user.id)
    return (
        db.query(Mating)
        .filter(
            Mating.user_id == current_user.id,
            or_(Mating.sire_id == mouse_id, Mating.dam_id == mouse_id),
        )
        .order_by(Mating.id.desc())
        .all()
    )
