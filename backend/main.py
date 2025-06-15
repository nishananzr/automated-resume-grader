import io
import re
import time
import spacy
import fitz  
import docx  
import os
from groq import Groq
from textblob import TextBlob
from spellchecker import SpellChecker
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv


load_dotenv()


class ContactInfo(BaseModel): name: Optional[str]=None; email: Optional[str]=None; phone: Optional[str]=None
class ScoreDetail(BaseModel): name: str; score: int; max_score: int; feedback: str
class Scorecard(BaseModel): total_score: int; details: List[ScoreDetail]
class ParsedResume(BaseModel): contact_info: ContactInfo; raw_text: str; skills: List[str]=Field(default_factory=list); education: str; experience: str
class ResumeAnalysisResponse(BaseModel): resume_data: ParsedResume; scorecard: Scorecard
class ReScoreRequest(BaseModel): resume_text: str; role: str
class TailoringRequest(BaseModel): resume_text: str; job_description: str
class TailoringResponse(BaseModel): missing_keywords: List[str]
class AICoachRequest(BaseModel): resume_text: str; job_description: str
class AICoachResponse(BaseModel): feedback: str


print("--- Server starting... This is the final, verified version. ---")
nlp = spacy.load("en_core_web_sm")
spell = SpellChecker()
ROLE_KEYWORDS = { "Software Engineer": ["python", "java", "react", "node", "docker", "aws", "sql"], "Data Scientist": ["python", "r", "sql", "pandas", "tensorflow"], "Designer": ["figma", "sketch", "photoshop", "ui", "ux"] }
SECTION_HEADERS = { "experience": ["experience", "work experience", "employment history"], "education": ["education", "academic background"], "skills": ["skills", "technical skills", "proficiencies"] }
ANALYSIS_HISTORY = []
print("--- Server ready. ---")

app = FastAPI(title="Resume Co-Pilot API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


def parse_section(text, headers, all_other_headers):
    pattern_str = r'^\s*(?:' + '|'.join(map(re.escape, headers)) + r')\s*$'
    pattern = re.compile(pattern_str, re.IGNORECASE | re.MULTILINE)
    match = pattern.search(text)
    if not match: return ""
    start_index, end_index = match.end(), len(text)
    for header_group in all_other_headers:
        for header in header_group:
            next_pattern = re.compile(rf'^\s*{re.escape(header)}\s*$', re.IGNORECASE | re.MULTILINE)
            next_match = next_pattern.search(text, pos=start_index)
            if next_match and next_match.start() < end_index: end_index = next_match.start()
    return text[start_index:end_index].strip()

def parse_resume_text(text):
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text, re.IGNORECASE)
    phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    email = email_match.group(0) if email_match else None
    phone = phone_match.group(0) if phone_match else None
    name = text.split('\n')[0].strip() if text else "Unknown"
    contact_info = ContactInfo(email=email, phone=phone, name=name)
    exp_text = parse_section(text, SECTION_HEADERS["experience"], [SECTION_HEADERS["education"], SECTION_HEADERS["skills"]])
    edu_text = parse_section(text, SECTION_HEADERS["education"], [SECTION_HEADERS["experience"], SECTION_HEADERS["skills"]])
    skills_text_block = parse_section(text, SECTION_HEADERS["skills"], [SECTION_HEADERS["experience"], SECTION_HEADERS["education"]])
    skills_list = [skill.strip() for skill in re.split(r'\n|,|•', skills_text_block) if skill.strip() and len(skill.strip()) < 30]
    return ParsedResume(contact_info=contact_info, raw_text=text, skills=list(set(skills_list)), education=edu_text, experience=exp_text)


class ScoringService:
    def __init__(self, parsed_resume, role="General"):
        self.resume = parsed_resume
        self.role = role
        self.text = parsed_resume.raw_text or ""
        self.doc = None
        self.score_details, self.total_score = [], 0
    def get_doc(self):
        if self.doc is None and self.text: self.doc = nlp(self.text)
        return self.doc
    def _add_score(self, name, score, max_score, feedback):
        clamped_score=max(0,min(score,max_score)); self.score_details.append(ScoreDetail(name=name,score=clamped_score,max_score=max_score,feedback=feedback)); self.total_score+=clamped_score
    def calculate_final_score(self):
        current_max = sum(d.max_score for d in self.score_details); base_score = 15
        if current_max > 0: self.total_score = base_score + int((self.total_score/current_max)*(100-base_score))
        else: self.total_score = base_score
        return Scorecard(total_score=self.total_score, details=self.score_details)
    def score_all(self):
        self.score_ats_parse_rate(); self.score_impact_words(); self.score_clarity_and_brevity(); self.score_tone()
        if self.role != "General": self.score_role_relevance()
        return self.calculate_final_score()
    def score_tone(self):
        max_score, score, feedback = 15, 0, "No experience section found to analyze tone."
        if self.resume.experience:
            try:
                pol = TextBlob(self.resume.experience).sentiment.polarity
                if pol > 0.15: score, feedback = 15, "Excellent! Positive and confident tone."
                elif pol >= 0.05: score, feedback = 10, "Good, professional tone."
                else: score, feedback = 2, "Tone may seem flat or slightly negative."
            except Exception: pass
        self._add_score("Tone Analysis", score, max_score, feedback)
    def score_impact_words(self):
        max_score, score = 40, 0
        if self.resume.experience:
            try:
                if len(re.findall(r'(\d+%?|\$\d+[\.,\d]*[kKmMbB]?)', self.resume.experience)) >= 1: score += 10
                doc = self.get_doc()
                if doc and sum(1 for t in doc if t.pos_ == "VERB" and t.lemma_.lower() in {"managed","led","architected","launched"}) >= 2: score += 10
            except Exception: pass
        self._add_score("Quantifying Impact", score, max_score, "Use of metrics and strong action verbs.")
    def score_clarity_and_brevity(self):
        max_score, score = 30, 0
        if self.text:
            words = re.findall(r'\w+', self.text.lower()); num_errors = len(spell.unknown(words))
            if num_errors == 0: score += 15
            elif num_errors <= 3: score += 10
            if 300 <= len(words) <= 800: score += 15
            elif 200 <= len(words) < 1000: score += 8
        self._add_score("Clarity & Brevity", score, max_score, "Checks for spelling and ideal length.")
    def score_role_relevance(self):
        max_score, score = 30, 0; target_keywords = set(ROLE_KEYWORDS.get(self.role, []))
        if target_keywords and self.text:
            found = target_keywords.intersection(set(re.findall(r'\w+', self.text.lower())))
            score = int((len(found) / len(target_keywords)) * max_score) if target_keywords else 0
        self._add_score("Role Keywords", score, max_score, f"Keyword match for {self.role}.")
    def score_ats_parse_rate(self):
        max_score = 25
        found = sum([1 for s in [self.resume.experience, self.resume.education, self.resume.skills, self.resume.contact_info.email] if s])
        self._add_score("ATS Parse Rate", int((found / 4) * max_score), 25, "How well key sections are identified.")

# --- API Endpoints ---
@app.get("/")
def read_root(): return {"status": "Resume Co-Pilot API is running"}

@app.post("/upload-and-analyze/")
async def upload_and_analyze(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read(); filename = file.filename.lower(); full_text = ""
        stream = io.BytesIO(file_bytes)
        if filename.endswith('.pdf'):
            with fitz.open(stream=stream, filetype="pdf") as doc: full_text = "".join(p.get_text() for p in doc)
        elif filename.endswith('.docx'):
            doc = docx.Document(stream); full_text = "\n".join([p.text for p in doc.paragraphs])
        elif filename.endswith('.txt'):
            full_text = file_bytes.decode('utf-8', errors='ignore')
        else: raise HTTPException(400, "Unsupported file type.")
        stream.close()
        parsed_data = parse_resume_text(full_text); scorer = ScoringService(parsed_data); scorecard = scorer.score_all()
        ANALYSIS_HISTORY.insert(0, {"timestamp": time.time(), "score": scorecard.total_score, "filename": file.filename});
        if len(ANALYSIS_HISTORY) > 5: ANALYSIS_HISTORY.pop()
        return ResumeAnalysisResponse(resume_data=parsed_data, scorecard=scorecard)
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {type(e).__name__}: {e}")
        raise HTTPException(500, "Failed to process file. It may be corrupted.")

@app.post("/rescore/")
async def rescore_resume(request: ReScoreRequest):
    parsed_data = parse_resume_text(request.resume_text); scorer = ScoringService(parsed_data, role=request.role); return scorer.score_all()

@app.post("/tailor-resume/")
async def tailor_resume(request: TailoringRequest):
    jd_doc=nlp(request.job_description); resume_doc=nlp(request.resume_text)
    jd_keywords={t.lemma_.lower() for t in jd_doc if not t.is_stop and not t.is_punct and t.pos_ in["NOUN","PROPN","ADJ"]}
    resume_keywords={t.lemma_.lower() for t in resume_doc if not t.is_stop and not t.is_punct}
    return TailoringResponse(missing_keywords=sorted(list(jd_keywords-resume_keywords))[:12])

@app.post("/ai-coach-feedback/")
async def get_ai_coach_feedback(request: AICoachRequest):
    # THIS IS THE KEY CHANGE: Initialize the client here
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(500, "Groq API key is not configured on the server.")
    
    try:
        groq_client = Groq(api_key=api_key)
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert career coach. Analyze the resume against the job description. Provide 3 sections in markdown: '**Strengths:**' (2-3 bullets), '**Areas for Improvement:**' (2-3 specific, actionable bullets), and '**Example Rewrite:**' (Pick one weak bullet point and rewrite it to be more impactful). Be encouraging but direct."},
                {"role": "user", "content": f"Job Description:\n---\n{request.job_description}\n---\n\nResume:\n---\n{request.resume_text}\n---"}
            ],
            model="llama3-8b-8192"
        )
        return AICoachResponse(feedback=chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"❌ GROQ API ERROR: {e}")
        raise HTTPException(503, "The AI Coach service is experiencing issues. Please try again later.")

@app.get("/history")
async def get_history(): return ANALYSIS_HISTORY