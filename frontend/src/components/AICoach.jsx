import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
const AICoach = ({ resumeText, jobDescription }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [error, setError] = useState('');
  const getFeedback = async () => {
    if (!jobDescription.trim()) { setError('Please paste a job description first.'); return; }
    setIsLoading(true); setFeedback(''); setError('');
    try {
      const response = await fetch('http://127.0.0.1:8000/ai-coach-feedback/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ resume_text: resumeText, job_description: jobDescription }), });
      if (!response.ok) throw new Error("The AI Coach is currently unavailable. Please try again later.");
      const data = await response.json(); setFeedback(data.feedback);
    } catch (err) { setError(err.message); } finally { setIsLoading(false); }
  };
  return (
    <div className="ai-coach-card">
      <h2>AI Career Coach</h2>
      <p>Get personalized, expert-level feedback from an LLM trained on millions of resumes.</p>
      <button onClick={getFeedback} disabled={isLoading || !jobDescription.trim()} className="insights-button ai-button">
        {isLoading ? 'Your coach is thinking...' : 'Get AI Coach Feedback'}
      </button>
      {error && <p className="error-message">{error}</p>}
      {feedback && <div className="feedback-content"><ReactMarkdown>{feedback}</ReactMarkdown></div>}
    </div>
  );
};
export default AICoach;