from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class Cage(Base):
    __tablename__ = "cages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    cage_number = Column(String, nullable=False, index=True)

    user = relationship("User", back_populates="cages")
    mice = relationship("Mouse", back_populates="cage")
