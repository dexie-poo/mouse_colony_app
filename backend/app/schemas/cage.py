from pydantic import BaseModel


class CageBase(BaseModel):
    cage_number: str


class CageCreate(CageBase):
    pass


class CageRead(CageBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
