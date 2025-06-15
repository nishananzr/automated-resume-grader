import { useLocation, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import ScoreSidebar from '../components/ScoreSidebar';
import ResumeTailoring from '../components/ResumeTailoring';
import AICoach from '../components/AICoach';
import '../AnalysisPage.css';

const AnalysisPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const initialAnalysisData = location.state?.analysisData;

  const [currentScorecard, setCurrentScorecard] = useState(initialAnalysisData?.scorecard);
  const [selectedRole, setSelectedRole] = useState('General');
  const [jobDescription, setJobDescription] = useState('');
  const [isRescoring, setIsRescoring] = useState(false);

  useEffect(() => {
    if (!initialAnalysisData) navigate('/');
  }, [initialAnalysisData, navigate]);

  

  const handleRoleChange = async (e) => {
    const newRole = e.target.value;
    setSelectedRole(newRole);

    
    if (!initialAnalysisData || !initialAnalysisData.resume_data || !initialAnalysisData.resume_data.raw_text) {
        console.error("Cannot re-score, initial resume data is missing.");
        return; 
    }

    if (newRole === 'General') {
      setCurrentScorecard(initialAnalysisData.scorecard);
      return;
    }

    setIsRescoring(true);
    try {
      const response = await fetch('https://automated-resume-grader-backend.onrender.com/rescore/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: initialAnalysisData.resume_data.raw_text, // This is now safe
          role: newRole,
        }),
      });
      if (!response.ok) throw new Error("Re-scoring failed.");
      setCurrentScorecard(await response.json());
    } catch (error) {
      console.error("Rescore failed:", error);
    } finally {
      setIsRescoring(false);
    }
  };

  if (!initialAnalysisData || !currentScorecard) return null;

  return (
    <div className="analysis-container">
      <header className="analysis-header">
        <div className="logo">Resume Co-Pilot</div>
        <button onClick={() => navigate('/')} className="new-upload-button">New Upload</button>
      </header>
      <main className="analysis-main-content">
        {isRescoring ? <div className="sidebar-loading">Recalculating...</div> : <ScoreSidebar scorecard={currentScorecard} />}
        <div className="right-column">
          <div className="role-selector-card">
            <h3>Tailor Score for a Role</h3>
            <p>See how your resume scores against keywords for a specific job title.</p>
            <select value={selectedRole} onChange={handleRoleChange} className="role-selector-dashboard">
              <option value="General">General Score</option>
              <option value="Software Engineer">Software Engineer</option>
              <option value="Data Scientist">Data Scientist</option>
              <option value="Designer">Designer</option>
            </select>
          </div>
          {/* We now pass the setter down to ResumeTailoring */}
          <ResumeTailoring 
            resumeText={initialAnalysisData.resume_data.raw_text}
            jobDescription={jobDescription}
            setJobDescription={setJobDescription} 
          />
          {/* The AI Coach is the star feature */}
          <AICoach 
            resumeText={initialAnalysisData.resume_data.raw_text}
            jobDescription={jobDescription}
          />
        </div>
      </main>
    </div>
  );
};
export default AnalysisPage;