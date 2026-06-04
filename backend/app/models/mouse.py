from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Mouse(Base):
    __tablename__ = "mice"

    id = Column(Integer, primary_key=True, index=True)
    genotype = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    project = Column(String, nullable=True)
    dob = Column(Date, nullable=True)
    age = Column(String, nullable=True)
    age_analysed = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    cage_id = Column(Integer, ForeignKey("cages.id"), nullable=True)

    cage = relationship("Cage", back_populates="mice")
