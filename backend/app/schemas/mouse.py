from datetime import date

from pydantic import BaseModel

from app.schemas.cage import CageRead


class MouseBase(BaseModel):
    genotype: str
    gender: str
    project: str | None = None
    dob: date | None = None
    age: str | None = None
    age_analysed: str | None = None
    notes: str | None = None
    cage_id: int | None = None


class MouseCreate(MouseBase):
    pass


class MouseUpdate(MouseBase):
    genotype: str | None = None
    gender: str | None = None


class MouseRead(MouseBase):
    id: int
    cage: CageRead | None = None

    class Config:
        from_attributes = True
