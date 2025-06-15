# Resume Co-Pilot: An Automated-Resume-Grader
![Uploading dashboard-preview.png…]()

An intelligent resume analysis platform built for the **Masai School Anveshan Hackathon 2025**. This tool provides job-seekers with instant, data-driven feedback to optimize their resumes, pass automated screeners, and land their next interview.

---

## Live Demo & Presentation

*   **Live Application (Deployed on Vercel & Render):**
    *   **[https://automated-resume-grader.vercel.app/](https://automated-resume-grader.vercel.app/)**

*   **Project Presentation Video:**
    *   **[Watch the 5-Minute Demo Here](https://your-youtube-or-google-drive-link)**

*   **GitHub Repository:**
    *   **[https://github.com/nishananzr/automated-resume-grader](https://github.com/nishananzr/automated-resume-grader)**

---

## 🎯 Project Overview

In today's competitive job market, hiring managers spend mere seconds on each resume. The "Resume Co-Pilot" is an intelligent web application designed to give job-seekers an instant "health check" on their resume, providing them with a clear path to improvement.

It goes beyond simple spell-checking by using multiple AI models to analyze content, tone, and relevance against specific job roles. Our goal is to empower every candidate with the insights needed to get past automated screeners (ATS), capture a recruiter's attention, and land their dream job.

---

## ✨ Key Features

*   **Multi-Format File Upload:** Accepts `.pdf`, `.docx`, and `.txt` resumes for maximum user convenience.
*   **Instant Scoring Engine:** Provides a re-balanced score out of 100 based on a multi-point analysis of:
    *   **ATS Parse Rate:** How well the resume's structure can be understood by automated systems.
    *   **Impact & Quantification:** Detection of measurable results and strong action verbs.
    *   **Clarity & Brevity:** Checks for spelling errors and ideal resume length.
*   **Interactive Role-Specific Scoring:** Instantly re-scores the resume against keywords for different job titles (Software Engineer, Data Scientist, Designer).
*   **AI Career Coach (LLM-Powered):** Leverages the **Groq API** with the Llama 3 model to provide expert-level, human-like feedback on strengths, weaknesses, and concrete "before-and-after" suggestions for improving bullet points.
*   **Job Description Tailoring:** Analyzes a pasted job description to find critical missing keywords that align the resume with the job requirements.
*   **Version History:** Tracks scores from recent analyses so users can see their improvement.

---

## 🛠️ Technologies & Architecture

This project is a full-stack application with a modern, decoupled architecture.

*   **Frontend:**
    *   **Framework:** React (with Vite)
    *   **Styling:** CSS
    *   **Deployment:** Vercel

*   **Backend:**
    *   **Framework:** Python with FastAPI
    *   **AI / NLP Libraries:**
        *   **spaCy:** For core entity recognition and text processing.
        *   **TextBlob:** For sentiment and tone analysis.
        *   **pyspellchecker:** For spelling and clarity checks.
    *   **LLM Integration:** Groq API (Llama 3 8B) for real-time AI Coach feedback.
    *   **File Parsing:** `PyMuPDF` & `python-docx`.
    *   **Deployment:** Render

*   **Security:**
    *   Handled secret API keys securely using `.env` files and a properly configured `.gitignore` to prevent leaks.

---

## 🔧 Local Setup & Installation

To run this project on your local machine, please follow these steps.

**Prerequisites:**
*   Node.js (v16+) & npm
*   Python (v3.10+) & pip
*   Git

**1. Clone the Repository:**
```bash
git clone https://github.com/nishananzr/automated-resume-grader.git
cd automated-resume-grader
```

**2. Set up the Backend:**
```# Navigate to the backend directory
cd backend

# Create and activate a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install the required Python packages
pip install -r requirements.txt

# Download the necessary NLP model for spaCy
python -m spacy download en_core_web_sm

# Create a .env file for your secret key
# (Add GROQ_API_KEY=your_key_here inside the file)
echo "GROQ_API_KEY=gsk_your_grok_api_key_here" > .env

# Run the backend server
uvicorn main:app --reload
```
**3. Set up the Frontend:**
```
# Open a new terminal and navigate to the frontend directory
cd frontend

# Install the required npm packages
npm install

# Run the frontend development server
npm run dev
```

