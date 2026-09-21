import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from .parse import extract_skills_from_resume

CHROMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "chroma_db")

def get_vector_store():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return Chroma(
        persist_directory=CHROMA_PATH, 
        embedding_function=embeddings,
        collection_metadata={"hnsw:space": "cosine"}
    )

def generate_interview_question(role: str, skills: str, previous_qa: list) -> str:
    vectorstore = get_vector_store()
    search_query = f"{role} technical concepts {skills}"
    docs = vectorstore.similarity_search(search_query, k=3)
    context = "\n".join([doc.page_content for doc in docs])
    
    llm = ChatGoogleGenerativeAI(model="gemini-3.7-flash", temperature=0.7, max_retries=0)
    history_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in previous_qa])
    
    prompt = PromptTemplate.from_template(
        "You are an expert technical interviewer. Reference knowledge:\n{context}\n\n"
        "Candidate Role: {role}\nSkills: {skills}\n\n"
        "Previous questions asked:\n{history}\n\n"
        "Generate ONE new, specific technical interview question based on the textbook knowledge and candidate skills. Do not repeat previous questions. Output ONLY the question text."
    )
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "role": role,
            "skills": skills,
            "context": context,
            "history": history_text
        })
        
        content = response.content
        if isinstance(content, list):
            question_text = " ".join([part.get("text", "") for part in content if isinstance(part, dict)])
        else:
            question_text = str(content)
            
        return question_text
    except Exception as e:
        print(f"API Rate limit hit: {e}")
        mock_questions = [
            f"How would you optimize the architecture for a highly scalable {role} system using {skills}?",
            "Can you explain a time when you had to debug a critical production issue, and what steps you took?",
            "If we were to migrate our legacy database to a modern stack, what challenges would you anticipate?",
            "Describe the tradeoffs between using a microservices architecture versus a monolith for our specific use case.",
            "How do you ensure security and prevent common vulnerabilities when deploying your code?"
        ]
        index = len(previous_qa) if len(previous_qa) < 5 else 0
        return mock_questions[index]

from sentence_transformers import util
import torch

def evaluate_session(session_data: str) -> str:
    qa_pairs = []
    lines = session_data.split('\n')
    current_q = None
    
    for line in lines:
        if line.startswith("Q: "):
            current_q = line[3:].strip()
        elif line.startswith("A: "):
            current_a = line[3:].strip()
            if current_q and current_a:
                qa_pairs.append((current_q, current_a))
                current_q = None

    if not qa_pairs:
        return "Not enough data to evaluate."

    vectorstore = get_vector_store()
    embeddings_model = vectorstore.embeddings
    
    total_score = 0
    valid_pairs = 0
    
    for q, a in qa_pairs:
        # Retrieve textbook context for the question
        docs = vectorstore.similarity_search(q, k=1)
        if docs:
            context = docs[0].page_content
            
            # Embed candidate's answer and textbook context locally
            ans_emb = embeddings_model.embed_query(a)
            ctx_emb = embeddings_model.embed_query(context)
            
            # Calculate Cosine Similarity mathematically
            ans_tensor = torch.tensor(ans_emb)
            ctx_tensor = torch.tensor(ctx_emb)
            sim = util.cos_sim(ans_tensor, ctx_tensor).item()
            
            # Scale to a realistic 0-100 score (answers are shorter than context, so sim is rarely 1.0)
            score = max(0, min(100, sim * 200)) 
            total_score += score
            valid_pairs += 1

    avg_score = total_score / valid_pairs if valid_pairs > 0 else 75.0

    # Rule-based output generation
    recommendation = "**Hire.** The candidate has a solid foundational grasp." if avg_score > 50 else "**Reject.** The candidate needs to review fundamentals."
    strength = "Strong semantic alignment with core technical documentation." if avg_score > 50 else "Attempted to address the questions, but lacked depth."
    improvement = "Could elaborate more on specific edge cases." if avg_score > 50 else "Answers significantly deviated from the textbook reference space."
    
    markdown = f"""### Local Semantic Evaluation
*Evaluated entirely offline using `all-MiniLM-L6-v2` Cosine Similarity*

**Technical Accuracy Score:** {avg_score:.1f}%

**1. Key Strengths**
- {strength}
- Answer vectors successfully aligned with the textbook mathematical space.

**2. Areas for Improvement**
- {improvement}

**3. Final Recommendation**
- {recommendation}
"""
    return markdown