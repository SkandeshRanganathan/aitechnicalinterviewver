from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, database
from .services.parse import extract_text_from_pdf, extract_skills_from_resume
from .services.ai import generate_interview_question, evaluate_session

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="AI Interview System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload_resume", response_model=schemas.SessionResponse)
async def upload_resume(
    candidate_name: str = Form(...),
    target_role: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    pdf_bytes = await file.read()
    resume_text = extract_text_from_pdf(pdf_bytes)
    skills = extract_skills_from_resume(resume_text)

    db_session = models.InterviewSession(
        candidate_name=candidate_name,
        target_role=target_role,
        resume_text=resume_text,
        extracted_skills=skills
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    return db_session

@app.post("/sessions/{session_id}/next_question", response_model=schemas.QAPairResponse)
def get_next_question(session_id: int, db: Session = Depends(database.get_db)):
    session = db.query(models.InterviewSession).filter(models.InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    previous_qa = [(qa.question_text, qa.candidate_answer) for qa in session.qa_pairs if qa.candidate_answer]
    
    new_question = generate_interview_question(
        role=session.target_role,
        skills=session.extracted_skills,
        previous_qa=previous_qa
    )

    qa_pair = models.QAPair(session_id=session.id, question_text=new_question)
    db.add(qa_pair)
    db.commit()
    db.refresh(qa_pair)

    return qa_pair

@app.post("/qa/{qa_id}/answer", response_model=schemas.QAPairResponse)
def submit_answer(qa_id: int, answer_data: schemas.AnswerSubmit, db: Session = Depends(database.get_db)):
    qa_pair = db.query(models.QAPair).filter(models.QAPair.id == qa_id).first()
    if not qa_pair:
        raise HTTPException(status_code=404, detail="Question not found")

    qa_pair.candidate_answer = answer_data.answer
    db.commit()
    db.refresh(qa_pair)
    
    return qa_pair

@app.get("/sessions/{session_id}/summary")
def get_session_summary(session_id: int, db: Session = Depends(database.get_db)):
    session = db.query(models.InterviewSession).filter(models.InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session_data = f"Role: {session.target_role}\nSkills: {session.extracted_skills}\n\n"
    for qa in session.qa_pairs:
        if qa.candidate_answer:
            session_data += f"Q: {qa.question_text}\nA: {qa.candidate_answer}\n\n"
        
    analysis = evaluate_session(session_data)
    
    return {
        "candidate_name": session.candidate_name,
        "role": session.target_role,
        "qa_pairs": [{"question": qa.question_text, "answer": qa.candidate_answer} for qa in session.qa_pairs if qa.candidate_answer],
        "analysis": analysis
    }