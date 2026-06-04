from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cage import Cage
from app.models.mouse import Mouse
from app.schemas.mouse import MouseCreate, MouseRead, MouseUpdate


router = APIRouter(prefix="/mice", tags=["mice"])


@router.post("/", response_model=MouseRead)
def create_mouse(mouse: MouseCreate, db: Session = Depends(get_db)):
    if mouse.cage_id is not None:
        cage = db.get(Cage, mouse.cage_id)
        if cage is None:
            raise HTTPException(status_code=404, detail="Cage not found")

    db_mouse = Mouse(**mouse.model_dump())
    db.add(db_mouse)
    db.commit()
    db.refresh(db_mouse)
    return db_mouse


@router.get("/", response_model=list[MouseRead])
def list_mice(db: Session = Depends(get_db)):
    return db.query(Mouse).order_by(Mouse.id).all()


@router.patch("/{mouse_id}", response_model=MouseRead)
def update_mouse(mouse_id: int, mouse: MouseUpdate, db: Session = Depends(get_db)):
    db_mouse = db.get(Mouse, mouse_id)
    if db_mouse is None:
        raise HTTPException(status_code=404, detail="Mouse not found")

    updates = mouse.model_dump(exclude_unset=True)
    cage_id = updates.get("cage_id")
    if cage_id is not None and db.get(Cage, cage_id) is None:
        raise HTTPException(status_code=404, detail="Cage not found")

    for field, value in updates.items():
        setattr(db_mouse, field, value)

    db.commit()
    db.refresh(db_mouse)
    return db_mouse


@router.post("/{mouse_id}/assign-cage/{cage_id}", response_model=MouseRead)
def assign_mouse_to_cage(mouse_id: int, cage_id: int, db: Session = Depends(get_db)):
    db_mouse = db.get(Mouse, mouse_id)
    if db_mouse is None:
        raise HTTPException(status_code=404, detail="Mouse not found")

    db_cage = db.get(Cage, cage_id)
    if db_cage is None:
        raise HTTPException(status_code=404, detail="Cage not found")

    db_mouse.cage_id = cage_id
    db.commit()
    db.refresh(db_mouse)
    return db_mouse
