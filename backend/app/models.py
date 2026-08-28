from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class InterviewSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String, index=True)
    target_role = Column(String, index=True)
    resume_text = Column(Text)
    extracted_skills = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

   
    qa_pairs = relationship("QAPair", back_populates="session")

class QAPair(Base):
    __tablename__ = "qa_pairs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    question_text = Column(Text)
    candidate_answer = Column(Text, nullable=True) # Nullable because it's empty when first asked
    evaluation_feedback = Column(Text, nullable=True) 

    session = relationship("InterviewSession", back_populates="qa_pairs")