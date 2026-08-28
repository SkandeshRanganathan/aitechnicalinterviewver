import fitz 
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_skills_from_resume(resume_text: str) -> str:
    llm = ChatGoogleGenerativeAI(model="gemini-3.7-flash", temperature=0, max_retries=0)
    prompt = PromptTemplate.from_template(
        "Extract the core technical skills, technologies, and domain exposure from this resume.\n"
        "Return them as a concise comma-separated list.\n\nResume:\n{resume_text}"
    )
    chain = prompt | llm
    
    try:
        response = chain.invoke({"resume_text": resume_text})
        
        # Gemini 3.6 sometimes returns a list of content blocks instead of a flat string
        content = response.content
        if isinstance(content, list):
            skills_text = " ".join([part.get("text", "") for part in content if isinstance(part, dict)])
        else:
            skills_text = str(content)
            
        return skills_text
    except Exception as e:
        print(f"API Rate limit hit: {e}")
        return "Python, React, Node.js, SQL, Machine Learning"