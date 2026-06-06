from datetime import date

from pydantic import BaseModel


class AnalysisBase(BaseModel):
    mouse_id: int
    sacrifice_date: date | None = None
    age_at_sacrifice: str | None = None
    organs_extracted: str | None = None
    organ_conditions: str | None = None
    preservation_method: str | None = None
    image_filename: str | None = None
    image_data: str | None = None
    notes: str | None = None


class AnalysisCreate(AnalysisBase):
    pass


class AnalysisRead(AnalysisBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
