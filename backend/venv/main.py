import io, re, time, spacy, fitz, docx
from textblob import TextBlob
from spellchecker import SpellChecker
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

# --- Pydantic Models ---
class ContactInfo(BaseModel): name: Optional[str]=None; email: Optional[str]=None; phone: Optional[str]=None
class ScoreDetail(BaseModel): name: str; score: int; max_score: int; feedback: str
class Scorecard(BaseModel): total_score: int; details: List[ScoreDetail]
class ParsedResume(BaseModel): contact_info: ContactInfo; raw_text: str; skills: List[str]=Field(default_factory=list); education: str; experience: str
class ResumeAnalysisResponse(BaseModel): resume_data: ParsedResume; scorecard: Scorecard
class ReScoreRequest(BaseModel): resume_text: str; role: str
class TailoringRequest(BaseModel): resume_text: str; job_description: str
class TailoringResponse(BaseModel): missing_keywords: List[str]

# --- Load Models & Setup ---
print("--- Server starting... ---")
nlp = spacy.load("en_core_web_sm")
spell = SpellChecker()
ROLE_KEYWORDS = { "Software Engineer": ["python", "java", "react", "node.js", "docker", "aws", "sql"], "Data Scientist": ["python", "r", "sql", "pandas", "tensorflow"], "Designer": ["figma", "sketch", "photoshop", "ui", "ux"] }
SECTION_HEADERS = { "experience": ["experience", "work experience"], "education": ["education", "academic background"], "skills": ["skills", "technical skills"] }
ANALYSIS_HISTORY = []
print("--- Server ready. ---")

# --- FastAPI App ---
app = FastAPI(title="Resume Co-Pilot API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- Parsing & Scoring Logic ---
def parse_section(text, headers, all_other_headers):
    pattern_str=r'^\s*(?:' + '|'.join(map(re.escape, headers)) + r')\s*$'
    pattern=re.compile(pattern_str, re.IGNORECASE | re.MULTILINE); match=pattern.search(text)
    if not match: return ""; start_index=match.end(); end_index=len(text)
    for header_group in all_other_headers:
        for header in header_group:
            next_pattern=re.compile(rf'^\s*{re.escape(header)}\s*$', re.IGNORECASE | re.MULTILINE)
            next_match=next_pattern.search(text, pos=start_index)
            if next_match and next_match.start() < end_index: end_index=next_match.start()
    return text[start_index:end_index].strip()
def parse_resume_text(text):
    contact_info=ContactInfo(email=re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text, re.IGNORECASE).group(0) if re.search(r'[\w\.-]+@[\w\.-]+', text) else None, phone=re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text).group(0) if re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text) else None, name=text.split('\n')[0].strip())
    exp_text=parse_section(text, SECTION_HEADERS["experience"], [SECTION_HEADERS["education"], SECTION_HEADERS["skills"]])
    edu_text=parse_section(text, SECTION_HEADERS["education"], [SECTION_HEADERS["experience"], SECTION_HEADERS["skills"]])
    skills_text_block=parse_section(text, SECTION_HEADERS["skills"], [SECTION_HEADERS["experience"], SECTION_HEADERS["education"]])
    skills_list=[skill.strip() for skill in re.split(r'\n|,|•', skills_text_block) if skill.strip() and len(skill.strip()) < 30]
    return ParsedResume(contact_info=contact_info, raw_text=text, skills=list(set(skills_list)), education=edu_text, experience=exp_text)
class ScoringService:
    def __init__(self, parsed_resume, role="General"):
        self.resume, self.role, self.text, self.doc, self.score_details, self.total_score = parsed_resume, role, parsed_resume.raw_text, nlp(parsed_resume.raw_text), [], 0
    def _add_score(self, name, score, max_score, feedback): self.score_details.append(ScoreDetail(name=name,score=max(0,min(score,max_score)),max_score=max_score,feedback=feedback)); self.total_score += max(0,min(score,max_score))
    def calculate_final_score(self):
        current_max=sum(d.max_score for d in self.score_details)
        if current_max > 0: self.total_score=int((self.total_score/current_max)*100)
        return Scorecard(total_score=self.total_score, details=self.score_details)
    def score_all(self): self.score_ats_parse_rate(); self.score_impact_words(); self.score_spelling_and_length(); self.score_tone();
        if self.role != "General": self.score_role_relevance();
        return self.calculate_final_score()
    def score_tone(self):
        if self.resume.experience: blob=TextBlob(self.resume.experience); pol=blob.sentiment.polarity;
            if pol > 0.1: score,fb=15,"Excellent! Positive and confident tone."
            elif pol >= 0: score,fb=7,"Neutral tone. Consider using more powerful language."
            else: score,fb=0,"Tone seems negative. Focus on achievements."
        else: score,fb=0,"No experience section found to analyze tone."
        self._add_score("Tone Analysis", score, 15, fb)
    def score_role_relevance(self):
        target_keywords=set(ROLE_KEYWORDS.get(self.role,[])); found=target_keywords.intersection(set(re.findall(r'\w+',self.text.lower())));
        match_p=len(found)/len(target_keywords) if target_keywords else 0
        self._add_score("Role Keywords",int(match_p*30),30,f"Found {len(found)} of {len(target_keywords)} keywords for {self.role}.")
    def score_ats_parse_rate(self):
        found=sum([1 for s in [self.resume.experience,self.resume.education,self.resume.skills,self.resume.contact_info.email] if s]);
        self._add_score("ATS Parse Rate",int((found/4)*25),25,f"Successfully parsed {found}/4 key sections.")
    def score_impact_words(self):
        score=0;
        if self.resume.experience:
            if len(re.findall(r'(\d+%?|\$\d+[\.,\d]*[kKmMbB]?)',self.resume.experience))>=3: score+=20
            if sum(1 for t in nlp(self.resume.experience) if t.pos_=="VERB" and t.lemma_.lower() in {"managed","led","architected","launched"})>=5: score+=20
        self._add_score("Quantifying Impact",score,40,"Scores impact based on measurable results and strong verbs.")
    def score_spelling_and_length(self):
        score=0;words=re.findall(r'\w+',self.text.lower());
        if not spell.unknown(words): score+=20
        if 400<=len(words)<=750: score+=15
        self._add_score("Clarity & Brevity",score,35,"Checks for spelling errors and ideal resume length.")

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"status": "Resume Co-Pilot API is running"}

@app.post("/upload-and-analyze/")
async def upload_and_analyze(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read(); filename = file.filename.lower(); full_text = ""
        if filename.endswith('.pdf'):
            with fitz.open(stream=file_bytes, filetype="pdf") as doc: full_text = "".join(p.get_text() for p in doc)
        elif filename.endswith('.docx'):
            with io.BytesIO(file_bytes) as stream: doc = docx.Document(stream); full_text = "\n".join([p.text for p in doc.paragraphs])
        elif filename.endswith('.txt'):
            full_text = file_bytes.decode('utf-8', errors='ignore')
        else: raise HTTPException(400, "Unsupported file type.")
        if not full_text.strip(): raise HTTPException(400, "File is empty.")
        parsed_data = parse_resume_text(full_text); scorer = ScoringService(parsed_data); scorecard = scorer.score_all()
        ANALYSIS_HISTORY.insert(0, {"timestamp": time.time(), "score": scorecard.total_score, "filename": file.filename});
        if len(ANALYSIS_HISTORY) > 5: ANALYSIS_HISTORY.pop()
        return ResumeAnalysisResponse(resume_data=parsed_data, scorecard=scorecard)
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {type(e).__name__}: {e}")
        raise HTTPException(500, "An unexpected server error occurred.")

@app.post("/rescore/")
async def rescore_resume(request: ReScoreRequest):
    parsed_data = parse_resume_text(request.resume_text); scorer = ScoringService(parsed_data, role=request.role); return scorer.score_all()

@app.post("/tailor-resume/")
async def tailor_resume(request: TailoringRequest):
    jd_doc=nlp(request.job_description); resume_doc=nlp(request.resume_text)
    jd_keywords={t.lemma_.lower() for t in jd_doc if t.pos_ in ["NOUN","PROPN"] and not t.is_stop}
    resume_keywords={t.lemma_.lower() for t in resume_doc if t.pos_ in ["NOUN","PROPN"] and not t.is_stop}
    return TailoringResponse(missing_keywords=sorted(list(jd_keywords-resume_keywords)))

@app.get("/history")
async def get_history(): return ANALYSIS_HISTORY