from pydantic import BaseModel


class CageBase(BaseModel):
    name: str
    location: str | None = None
    notes: str | None = None


class CageCreate(CageBase):
    pass


class CageRead(CageBase):
    id: int

    class Config:
        from_attributes = True
