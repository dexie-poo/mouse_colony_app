from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..litter_export import build_litter_history_xlsx
from ..models.litter_pup import LitterPup
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


def calculate_age_months(dob: date | None):
    if dob is None:
        return None

    today = date.today()
    months = (today.year - dob.year) * 12 + today.month - dob.month
    if today.day < dob.day:
        months -= 1
    return str(max(months, 0))


def create_kept_pup_mice(db: Session, mating: MatingCreate, user_id: int):
    return None


def create_litter_pups(
    db: Session,
    db_mating: Mating,
    mating: MatingCreate,
    current_user: User,
):
    kept_mouse_ids = []
    for pup in mating.pups:
        mouse = None
        if pup.decision == "keep":
            mouse = Mouse(
                user_id=current_user.id,
                external_id=pup.assigned_external_id,
                genotype=pup.genotype or "Unknown",
                gender=pup.sex,
                dob=mating.litter_dob,
                age_months=calculate_age_months(mating.litter_dob),
                owner=current_user.username,
                remark=f"Kept pup from mating #{db_mating.id}",
            )
            db.add(mouse)
            db.flush()
            kept_mouse_ids.append(str(mouse.id))

        db_pup = LitterPup(
            user_id=current_user.id,
            mating_id=db_mating.id,
            mouse_id=mouse.id if mouse else None,
            pup_label=pup.pup_label,
            assigned_external_id=pup.assigned_external_id,
            sex=pup.sex,
            dob=mating.litter_dob,
            wean_date=pup.wean_date,
            genotype=pup.genotype,
            genotype_reference_1=pup.genotype_reference_1,
            genotype_reference_2=pup.genotype_reference_2,
            decision=pup.decision,
        )
        db.add(db_pup)

    return ",".join(kept_mouse_ids) if kept_mouse_ids else None


@router.post("/", response_model=MatingRead)
def create_mating(
    mating: MatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_mouse_exists(db, mating.sire_id, "Sire", current_user.id)
    ensure_mouse_exists(db, mating.dam_id, "Dam", current_user.id)

    payload = mating.model_dump(exclude={"pups"})
    db_mating = Mating(**payload, user_id=current_user.id)
    db.add(db_mating)
    db.flush()
    db.refresh(db_mating)
    kept_mouse_ids = create_litter_pups(db, db_mating, mating, current_user)
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


@router.get("/litter-history/export.xlsx")
def export_litter_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pups = (
        db.query(LitterPup)
        .join(Mating)
        .filter(LitterPup.user_id == current_user.id)
        .order_by(LitterPup.id)
        .all()
    )
    workbook = build_litter_history_xlsx(pups)
    return StreamingResponse(
        workbook,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="litter_history.xlsx"'},
    )
