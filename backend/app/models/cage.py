from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Cage(Base):
    __tablename__ = "cages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    location = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    mice = relationship("Mouse", back_populates="cage")
