from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models.analysis import Analysis
from ..models.mouse import Mouse
from ..models.user import User
from ..schemas.analysis import AnalysisCreate, AnalysisRead


router = APIRouter(prefix="/analyses", tags=["analyses"])


@router.post("/", response_model=AnalysisRead)
def create_analysis(
    analysis: AnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mouse = (
        db.query(Mouse)
        .filter(Mouse.id == analysis.mouse_id, Mouse.user_id == current_user.id)
        .first()
    )
    if mouse is None:
        raise HTTPException(status_code=404, detail="Mouse not found")

    db_analysis = Analysis(**analysis.model_dump(), user_id=current_user.id)
    mouse.sacrificed = "yes"
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis


@router.get("/", response_model=list[AnalysisRead])
def list_analyses(
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(Analysis)
        .join(Mouse)
        .filter(Analysis.user_id == current_user.id)
    )

    if q:
        pattern = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Mouse.external_id.ilike(pattern),
                Mouse.genotype.ilike(pattern),
                Mouse.remark.ilike(pattern),
                Analysis.organs_extracted.ilike(pattern),
                Analysis.organ_conditions.ilike(pattern),
                Analysis.preservation_method.ilike(pattern),
                Analysis.notes.ilike(pattern),
            )
        )

    return query.order_by(Analysis.id.desc()).all()


@router.get("/mouse/{mouse_id}", response_model=list[AnalysisRead])
def list_analyses_for_mouse(
    mouse_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mouse = (
        db.query(Mouse)
        .filter(Mouse.id == mouse_id, Mouse.user_id == current_user.id)
        .first()
    )
    if mouse is None:
        raise HTTPException(status_code=404, detail="Mouse not found")

    return (
        db.query(Analysis)
        .filter(Analysis.user_id == current_user.id, Analysis.mouse_id == mouse_id)
        .order_by(Analysis.id.desc())
        .all()
    )
