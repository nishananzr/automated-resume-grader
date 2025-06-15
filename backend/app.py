import streamlit as st
from main import upload_and_analyze, ReScoreRequest, rescore_resume, TailoringRequest, tailor_resume, AICoachRequest, get_ai_coach_feedback
from pydantic import BaseModel
import io
import pandas as pd

st.set_page_config(layout="wide")

st.title("📄 Resume Co-Pilot")
st.write("Get an instant, AI-powered analysis of your resume.")

uploaded_file = st.file_uploader("Upload your resume (PDF, DOCX, TXT)", type=['pdf', 'docx', 'txt'])

if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

if uploaded_file is not None and st.session_state.analysis_result is None:
    with st.spinner('Analyzing your resume...'):
        # Mocking the UploadFile object for the backend function
        class MockUploadFile:
            def __init__(self, file_uploader):
                self.file = file_uploader
                self.filename = file_uploader.name

            async def read(self):
                return self.file.getvalue()

        try:
            mock_file = MockUploadFile(uploaded_file)
            analysis = await upload_and_analyze(mock_file)
            st.session_state.analysis_result = analysis
            st.rerun() # Rerun the script to show the results
        except Exception as e:
            st.error(f"An error occurred: {e}")


if st.session_state.analysis_result:
    analysis = st.session_state.analysis_result
    
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header(f"Score: {analysis.scorecard.total_score}/100")
        for detail in analysis.scorecard.details:
            st.metric(label=detail.name, value=f"{detail.score}/{detail.max_score}")
            st.caption(detail.feedback)
            st.progress(detail.score / detail.max_score)
        
        if st.button("Analyze a New Resume"):
            st.session_state.analysis_result = None
            st.rerun()

    with col2:
        st.header("AI Coach & Tailoring")
        job_description = st.text_area("Paste a Job Description Here for Tailored Feedback")
        
        if st.button("Get AI Coach Feedback"):
            if job_description:
                with st.spinner("Your AI Coach is thinking..."):
                    try:
                        coach_request = AICoachRequest(resume_text=analysis.resume_data.raw_text, job_description=job_description)
                        coach_response = await get_ai_coach_feedback(coach_request)
                        st.markdown(coach_response.feedback)
                    except Exception as e:
                        st.error(f"AI Coach Error: {e}")
            else:
                st.warning("Please paste a job description to get AI Coach feedback.")