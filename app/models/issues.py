from sqlalchemy import Column, String, Integer, JSON
from app.database import Base


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    # might need to be a join table in the future because a json column
    # can reference an id that doesn't exist
    diagnosis_ids = Column(JSON, default=list)
    plant_ids = Column(JSON, default=list)
