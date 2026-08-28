from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SessionCreate(BaseModel):
    candidate_name: str
    target_role: str
class QAPairResponse(BaseModel):
    id : int
    question_text : str
    candidate_answer : Optional[str] = None
    class Config:
        from_attributes = True
class SessionResponse(BaseModel):
    id : int
    candidate_name : str
    target_role : str
    extracted_skills : Optional[str] = None
    qa_pairs : List[QAPairResponse] = []
    class Config:
        from_attributes = True
class AnswerSubmit(BaseModel):
    answer: str