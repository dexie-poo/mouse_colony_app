from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..export import build_mouse_export_xlsx
from ..models.cage import Cage
from ..models.mouse import Mouse
from ..schemas.mouse import MouseCreate, MouseRead, MouseUpdate


router = APIRouter(prefix="/mice", tags=["mice"])


def get_or_create_cage(db: Session, cage_number: str | None):
    if not cage_number:
        return None

    cage = db.query(Cage).filter(Cage.cage_number == cage_number).first()
    if cage:
        return cage

    cage = Cage(cage_number=cage_number)
    db.add(cage)
    db.flush()
    return cage


def calculate_age_months(dob: date | None):
    if dob is None:
        return None

    today = date.today()
    months = (today.year - dob.year) * 12 + today.month - dob.month
    if today.day < dob.day:
        months -= 1
    return str(max(months, 0))


@router.post("/", response_model=MouseRead)
def create_mouse(mouse: MouseCreate, db: Session = Depends(get_db)):
    payload = mouse.model_dump()
    cage_number = payload.pop("cage_number", None)
    payload["age_months"] = calculate_age_months(payload.get("dob"))
    cage = get_or_create_cage(db, cage_number)

    db_mouse = Mouse(**payload)
    if cage:
        db_mouse.cage = cage

    db.add(db_mouse)
    db.commit()
    db.refresh(db_mouse)
    return db_mouse


@router.get("/", response_model=list[MouseRead])
def list_mice(db: Session = Depends(get_db)):
    return db.query(Mouse).order_by(Mouse.id).all()


@router.get("/export.xlsx")
def export_mice(db: Session = Depends(get_db)):
    mice = db.query(Mouse).order_by(Mouse.id).all()
    workbook = build_mouse_export_xlsx(mice)
    return StreamingResponse(
        workbook,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="mice_cage_list.xlsx"'},
    )


@router.patch("/{mouse_id}", response_model=MouseRead)
def update_mouse(mouse_id: int, mouse: MouseUpdate, db: Session = Depends(get_db)):
    db_mouse = db.get(Mouse, mouse_id)
    if db_mouse is None:
        raise HTTPException(status_code=404, detail="Mouse not found")

    updates = mouse.model_dump(exclude_unset=True)
    cage_number = updates.pop("cage_number", None)
    if "dob" in updates:
        updates["age_months"] = calculate_age_months(updates["dob"])

    for field, value in updates.items():
        setattr(db_mouse, field, value)

    if cage_number is not None:
        db_mouse.cage = get_or_create_cage(db, cage_number)

    db.commit()
    db.refresh(db_mouse)
    return db_mouse


@router.post("/{mouse_id}/assign-cage/{cage_number}", response_model=MouseRead)
def assign_mouse_to_cage(mouse_id: int, cage_number: str, db: Session = Depends(get_db)):
    db_mouse = db.get(Mouse, mouse_id)
    if db_mouse is None:
        raise HTTPException(status_code=404, detail="Mouse not found")

    db_mouse.cage = get_or_create_cage(db, cage_number)
    db.commit()
    db.refresh(db_mouse)
    return db_mouse
