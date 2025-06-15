import streamlit as st
from main import parse_resume_text, ScoringService, ReScoreRequest, rescore_resume, TailoringRequest, tailor_resume, AICoachRequest, get_ai_coach_feedback
from pydantic import BaseModel
import io
import docx
from pypdf import PdfReader # <-- Use the new library

st.set_page_config(layout="wide")
st.title("📄 Resume Co-Pilot")
st.write("Get an instant, AI-powered analysis of your resume.")

uploaded_file = st.file_uploader("Upload your resume (PDF, DOCX, TXT)", type=['pdf', 'docx', 'txt'])

# This is a small helper to mock the FastAPI backend function
async def run_analysis(file):
    file_bytes = file.getvalue()
    filename = file.name.lower()
    full_text = ""
    
    if filename.endswith('.pdf'):
        reader = PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            full_text += page.extract_text() or ""
    elif filename.endswith('.docx'):
        doc = docx.Document(io.BytesIO(file_bytes))
        full_text = "\n".join([para.text for para in doc.paragraphs])
    elif filename.endswith('.txt'):
        full_text = file_bytes.decode('utf-8', errors='ignore')

    if not full_text.strip():
        st.error("Could not extract any text from the file.")
        return None
    
    parsed_data = parse_resume_text(full_text)
    scorer = ScoringService(parsed_data)
    scorecard = scorer.score_all()
    
    # Mock the full response object
    class MockResponse:
        def __init__(self, data, card):
            self.resume_data = data
            self.scorecard = card

    return MockResponse(parsed_data, scorecard)


if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

if uploaded_file is not None and st.session_state.analysis_result is None:
    with st.spinner('Analyzing your resume...'):
        analysis = await run_analysis(uploaded_file)
        if analysis:
            st.session_state.analysis_result = analysis
            st.rerun()

if st.session_state.analysis_result:
    analysis = st.session_state.analysis_result
    col1, col2 = st.columns([1, 2])
    with col1:
        st.header(f"Score: {analysis.scorecard.total_score}/100")
        for detail in analysis.scorecard.details:
            st.metric(label=detail.name, value=f"{detail.score}/{detail.max_score}")
        if st.button("Analyze a New Resume"):
            st.session_state.analysis_result = None
            st.rerun()
    with col2:
        st.header("AI Coach & Tailoring")
        job_description = st.text_area("Paste a Job Description Here for Tailored Feedback")
        if st.button("Get AI Coach Feedback"):
            if job_description:
                with st.spinner("Your AI Coach is thinking..."):
                    coach_request = AICoachRequest(resume_text=analysis.resume_data.raw_text, job_description=job_description)
                    coach_response = await get_ai_coach_feedback(coach_request)
                    st.markdown(coach_response.feedback)
            else:
                st.warning("Please paste a job description first.")