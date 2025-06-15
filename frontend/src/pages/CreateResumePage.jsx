import { Link } from 'react-router-dom';
import './CreateResumePage.css';

const CreateResumePage = () => {
  return (
    <div className="create-page-container">
      <div className="create-content-box">
        <div className="rocket-icon">🚀</div>
        <h1>Builder Coming Soon!</h1>
        <p>
          We're hard at work creating an intuitive, AI-powered resume builder to help you craft the perfect resume from scratch.
        </p>
        <p>Check back soon to be one of the first to try it out!</p>
        <Link to="/" className="back-to-home-button">
          Back to Analyzer
        </Link>
      </div>
    </div>
  );
};

export default CreateResumePage;