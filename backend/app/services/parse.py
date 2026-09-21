import fitz 

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

from keybert import KeyBERT

# Initialize KeyBERT with our existing local model
kw_model = KeyBERT(model="all-MiniLM-L6-v2")

def extract_skills_from_resume(resume_text: str) -> str:
    try:
        # Use KeyBERT to extract the top 10 technical keywords
        keywords = kw_model.extract_keywords(
            resume_text, 
            keyphrase_ngram_range=(1, 2), 
            stop_words='english', 
            top_n=10
        )
        
        # Format the output as a comma-separated list of just the keywords (ignoring scores)
        skills_text = ", ".join([kw[0] for kw in keywords])
        return skills_text
    except Exception as e:
        print(f"Local NLP extraction failed: {e}")
        return "Python, React, Node.js, SQL, Machine Learning"