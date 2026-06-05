from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Cage(Base):
    __tablename__ = "cages"

    id = Column(Integer, primary_key=True, index=True)
    cage_number = Column(String, unique=True, nullable=False, index=True)

    mice = relationship("Mouse", back_populates="cage")
