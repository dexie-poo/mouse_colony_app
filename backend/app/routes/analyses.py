from fastapi import APIRouter, Depends, HTTPException
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Analysis)
        .filter(Analysis.user_id == current_user.id)
        .order_by(Analysis.id.desc())
        .all()
    )
