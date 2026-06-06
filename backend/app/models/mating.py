from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class Mating(Base):
    __tablename__ = "matings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    sire_id = Column(Integer, ForeignKey("mice.id"), nullable=False, index=True)
    dam_id = Column(Integer, ForeignKey("mice.id"), nullable=False, index=True)
    mating_date = Column(Date, nullable=True)
    litter_dob = Column(Date, nullable=True)
    litter_size = Column(Integer, nullable=True)
    male_pups = Column(Integer, nullable=True)
    female_pups = Column(Integer, nullable=True)
    pup_genotypes = Column(Text, nullable=True)
    genotyping_reference = Column(String, nullable=True)
    keep_litter = Column(Integer, nullable=True)
    euthanise_litter = Column(Integer, nullable=True)
    kept_male_pups = Column(Integer, nullable=True)
    kept_female_pups = Column(Integer, nullable=True)
    kept_pup_genotype = Column(String, nullable=True)
    kept_mouse_ids = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="matings")
    sire = relationship("Mouse", back_populates="sire_matings", foreign_keys=[sire_id])
    dam = relationship("Mouse", back_populates="dam_matings", foreign_keys=[dam_id])
