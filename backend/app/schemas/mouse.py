from datetime import date

from pydantic import BaseModel

from .cage import CageRead


class MouseBase(BaseModel):
    genotype: str
    gender: str
    dob: date | None = None
    age_months: str | None = None
    owner: str | None = None
    remark: str | None = None
    cage_number: str | None = None


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
