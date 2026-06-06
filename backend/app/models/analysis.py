from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    mouse_id = Column(Integer, ForeignKey("mice.id"), nullable=False, index=True)
    sacrifice_date = Column(Date, nullable=True)
    age_at_sacrifice = Column(String, nullable=True)
    organs_extracted = Column(Text, nullable=True)
    organ_conditions = Column(Text, nullable=True)
    preservation_method = Column(String, nullable=True)
    image_filename = Column(String, nullable=True)
    image_data = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="analyses")
    mouse = relationship("Mouse", back_populates="analyses")
