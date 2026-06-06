from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    mice = relationship("Mouse", back_populates="user")
    cages = relationship("Cage", back_populates="user")
    matings = relationship("Mating", back_populates="user")
    analyses = relationship("Analysis", back_populates="user")
