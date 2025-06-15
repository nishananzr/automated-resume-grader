import { useState } from 'react';

const ResumeTailoring = ({ resumeText, jobDescription, setJobDescription }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [missingKeywords, setMissingKeywords] = useState(null);

  const handleGetInsights = async () => {
    if (!jobDescription.trim()) return;
    setIsLoading(true);
    setMissingKeywords(null);
    try {
      const response = await fetch('http://127.0.0.1:8000/tailor-resume/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_text: resumeText, job_description: jobDescription }),
      });
      const data = await response.json();
      setMissingKeywords(data.missing_keywords);
    } catch (error) {
      console.error("Failed to get insights:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="tailoring-card">
      <h2>Keyword Matcher</h2>
      <p>Paste a job description to find missing keywords from your resume.</p>
      <div className="tailoring-input-box">
        <textarea
          placeholder="Paste job description here..."
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
        />
        <div className="tailoring-actions">
          <button onClick={handleGetInsights} disabled={isLoading || !jobDescription.trim()} className="insights-button">
            {isLoading ? 'Finding...' : 'Find Missing Keywords'}
          </button>
        </div>
      </div>
      {missingKeywords !== null && (
        <div className="keywords-result">
          <h4>Keywords to Consider Adding:</h4>
          {missingKeywords.length > 0 ? (
            <div className="keywords-list">
              {missingKeywords.map(kw => <span key={kw} className="keyword-tag">{kw}</span>)}
            </div>
          ) : (
            <p className="great-match-text">Great match! Your resume aligns well with the key terms in this job description.</p>
          )}
        </div>
      )}
    </div>
  );
};
export default ResumeTailoring;