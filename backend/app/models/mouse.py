from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class Mouse(Base):
    __tablename__ = "mice"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    genotype = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    owner = Column(String, nullable=True)
    dob = Column(Date, nullable=True)
    age_months = Column(String, nullable=True)
    remark = Column(Text, nullable=True)
    cage_id = Column(Integer, ForeignKey("cages.id"), nullable=True)
    sacrificed = Column(String, nullable=True)

    user = relationship("User", back_populates="mice")
    cage = relationship("Cage", back_populates="mice")
    analyses = relationship("Analysis", back_populates="mouse")
    sire_matings = relationship(
        "Mating",
        back_populates="sire",
        foreign_keys="Mating.sire_id",
    )
    dam_matings = relationship(
        "Mating",
        back_populates="dam",
        foreign_keys="Mating.dam_id",
    )

    @property
    def cage_number(self):
        return self.cage.cage_number if self.cage else None
