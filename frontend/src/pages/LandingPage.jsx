import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import dashboardPreview from '../assets/dashboard-preview.png';
import './LandingPage.css';

const LandingPage = () => {
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setError('');
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first.");
      return;
    }
    setIsLoading(true);
    setError('');
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('https://automated-resume-grader-backend.onrender.com/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        let errorDetail = response.statusText;
        try {
            const errorData = await response.json();
            errorDetail = errorData.detail || errorDetail;
        } catch (e) {
            // Ignore if error response is not JSON
        }
        throw new Error(errorDetail);
      }

      const data = await response.json();
      navigate('/analysis', { state: { analysisData: data } });
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
    }
  };

  return (
    <div className="landing-container">
      {/* --- Hero Section --- */}
      <section className="hero-section">
        <div className="hero-left">
          <h1>Unlock Your Resume's Full Potential.</h1>
          <p className="hero-subtitle">
            Our AI analyzes your resume against thousands of data points to give you the professional edge you need to land your dream job, faster.
          </p>
          <div className="upload-box">
            <p className="upload-box-title">Upload your resume to get an instant score.</p>
            
            <p className="file-formats-text">Supported formats: PDF, DOCX, TXT</p>
            
            <input 
              type="file" 
              id="resume-upload" 
              accept=".pdf,.doc,.docx,.txt" 
              onChange={handleFileChange} 
              className="file-input" 
            />
            <label htmlFor="resume-upload" className="file-label">
              {file ? file.name : 'Choose Your File'}
            </label>
            <button onClick={handleUpload} disabled={isLoading || !file} className="upload-button">
              {isLoading ? 'Scanning...' : 'Get My Score'}
            </button>
            {error && <p className="error-message-landing">{error}</p>}
          </div>
          <p className="create-link-text">
            Don't have a resume? <Link to="/create">Create one for free</Link>
          </p>
        </div>
        <div className="hero-right">
          <img src={dashboardPreview} alt="Resume analysis dashboard preview" className="preview-image" />
        </div>
      </section>

      {/* --- Features Section --- */}
      <section className="features-section">
        <h2>A Deeper Level of Analysis</h2>
        <p className="features-subtitle">We go beyond simple spell-checking to find what really matters to recruiters.</p>
        <div className="features-grid">
            <div className="feature-card">
                <h3>Maximize Your Impact</h3>
                <p>Our system identifies weak language and suggests powerful action verbs and quantifiable metrics to make your achievements shine.</p>
            </div>
            <div className="feature-card">
                <h3>Achieve Perfect Clarity</h3>
                <p>We check for ideal length, consistent formatting, and readability to ensure your message is clear and professional.</p>
            </div>
            <div className="feature-card">
                <h3>Beat the Resume Robots (ATS)</h3>
                <p>Get an analysis of crucial keywords and formatting that helps your resume get past automated screeners and into human hands.</p>
            </div>
        </div>
      </section>

      {/* --- How It Works Section --- */}
      <section className="how-it-works-section">
          <h2>Simple, Fast, and Insightful</h2>
          <p className="how-it-works-subtitle">Get from upload to improvement in under a minute.</p>
          <div className="how-it-works-grid">
              <div className="step-card">
                  <div className="step-number">1</div>
                  <h3>Upload Your Resume</h3>
                  <p>Securely upload your resume in PDF, DOCX, or TXT format. We process it instantly without saving your personal data.</p>
              </div>
              <div className="step-card">
                  <div className="step-number">2</div>
                  <h3>Get Your General Score</h3>
                  <p>Receive a score out of 100 based on key metrics that recruiters and hiring managers look for.</p>
              </div>
              <div className="step-card">
                  <div className="step-number">3</div>
                  <h3>Tailor for Your Dream Job</h3>
                  <p>Interactively re-score your resume against specific job titles to see how well you match.</p>
              </div>
          </div>
      </section>
    </div>
  );
};

export default LandingPage;