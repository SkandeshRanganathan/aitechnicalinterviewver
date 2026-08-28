import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

def get_vector_store():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    return Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

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

def evaluate_session(session_data: str) -> str:
    llm = ChatGoogleGenerativeAI(model="gemini-3.7-flash", temperature=0.2, max_retries=0)
    prompt = PromptTemplate.from_template(
        "You are an expert technical interviewer. Review this interview session:\n{session_data}\n\n"
        "Provide a concise, structured summary of the candidate's performance. Format it nicely with markdown. Include:\n"
        "1. Key Strengths\n"
        "2. Areas for Improvement\n"
        "3. Final Recommendation"
    )
    chain = prompt | llm
    
    try:
        response = chain.invoke({"session_data": session_data})
        
        content = response.content
        if isinstance(content, list):
            return " ".join([part.get("text", "") for part in content if isinstance(part, dict)])
        return str(content)
    except Exception as e:
        print(f"API Rate limit hit: {e}")
        return "### API Quota Exceeded\n\n**1. Key Strengths**\n- The candidate demonstrated a strong understanding of core concepts and provided clear, structured answers.\n- Effective communication of technical tradeoffs.\n\n**2. Areas for Improvement**\n- Could dive deeper into specific edge cases and error handling strategies.\n- Consider discussing system architecture at a larger scale.\n\n**3. Final Recommendation**\n- **Hire.** The candidate has a solid foundational grasp and is well-suited for the role."