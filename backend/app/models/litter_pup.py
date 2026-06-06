from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class LitterPup(Base):
    __tablename__ = "litter_pups"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    mating_id = Column(Integer, ForeignKey("matings.id"), nullable=False, index=True)
    mouse_id = Column(Integer, ForeignKey("mice.id"), nullable=True, index=True)
    pup_label = Column(String, nullable=True)
    assigned_external_id = Column(String, nullable=True)
    sex = Column(String, nullable=False)
    dob = Column(Date, nullable=True)
    wean_date = Column(Date, nullable=True)
    genotype = Column(String, nullable=True)
    genotype_reference_1 = Column(String, nullable=True)
    genotype_reference_2 = Column(String, nullable=True)
    decision = Column(String, nullable=False)

    mating = relationship("Mating", back_populates="pups")
    mouse = relationship("Mouse")
