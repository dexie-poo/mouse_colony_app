from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class Mating(Base):
    __tablename__ = "matings"

    id = Column(Integer, primary_key=True, index=True)
    sire_id = Column(Integer, ForeignKey("mice.id"), nullable=False, index=True)
    dam_id = Column(Integer, ForeignKey("mice.id"), nullable=False, index=True)
    mating_date = Column(Date, nullable=True)
    litter_dob = Column(Date, nullable=True)
    litter_size = Column(Integer, nullable=True)
    male_pups = Column(Integer, nullable=True)
    female_pups = Column(Integer, nullable=True)
    pup_genotypes = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    sire = relationship("Mouse", back_populates="sire_matings", foreign_keys=[sire_id])
    dam = relationship("Mouse", back_populates="dam_matings", foreign_keys=[dam_id])
