from sqlalchemy.orm import DeclarativeBase
import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum
from datetime import datetime

class Status(enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Base(DeclarativeBase):
    pass

class JobProcessing(Base):
    __tablename__ = "job_processing"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    jobdesc_path = Column(String(255), nullable=False)
    cv_path = Column(String(255), nullable=False)
    decision = Column(String(255), nullable=False)
    report_path = Column(String(255), nullable=False)
    progress = Column(Integer, nullable=False)
    status = Column(Enum(Status), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    

