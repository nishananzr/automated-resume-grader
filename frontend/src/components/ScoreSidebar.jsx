import { useState } from 'react';

const ChevronIcon = ({ isOpen }) => (<svg className={`chevron-icon ${isOpen ? 'open' : ''}`} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="6 9 12 15 18 9"></polyline></svg>);
const StatusIcon = ({ score, maxScore }) => {
    const percentage = (score / maxScore) * 100;
    if (percentage >= 80) return <span className="status-icon success">✓</span>;
    if (percentage >= 50) return <span className="status-icon warning">!</span>;
    return <span className="status-icon error">×</span>;
};

const ScoreSidebar = ({ scorecard }) => {
  const [openSection, setOpenSection] = useState('CONTENT');

  const scoreCategories = {
    'CONTENT': scorecard.details.filter(d => ["ATS Parse Rate", "Quantifying Impact", "Clarity & Brevity"].includes(d.name)),
    'AI ANALYSIS': scorecard.details.filter(d => ["Tone Analysis", "Role Keywords"].includes(d.name)),
  };

  return (
    <aside className="score-sidebar">
      <div className="main-score-card">
        <p className="main-score-title">Your Score</p>
        <p className="main-score-value">{scorecard.total_score}<span>/100</span></p>
        <p className="main-score-issues">{scorecard.details.length} Areas to Review</p>
      </div>

      {Object.entries(scoreCategories).map(([categoryName, details]) => {
        if (details.length === 0) return null;
        const categoryScore = Math.round(details.reduce((a, d) => a + d.score, 0) / details.reduce((a, d) => a + d.max_score, 0) * 100);
        const isOpen = openSection === categoryName;

        return (
          <div key={categoryName} className="collapsible-section">
            <button className="section-header" onClick={() => setOpenSection(isOpen ? null : categoryName)}>
              <span>{categoryName}</span>
              <div className="section-summary">
                <span className={`section-score-badge p${categoryScore >= 80 ? '-high' : categoryScore >= 50 ? '-medium' : '-low'}`}>
                  {categoryScore}%
                </span>
                <ChevronIcon isOpen={isOpen} />
              </div>
            </button>
            {isOpen && (
              <div className="section-content">
                {details.map(detail => (
                  <div key={detail.name} className="detail-item">
                    <div className="detail-header">
                      <StatusIcon score={detail.score} maxScore={detail.max_score} />
                      <span className="detail-name">{detail.name}</span>
                    </div>
                    <p className="detail-feedback">{detail.feedback}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )
      })}
    </aside>
  );
};
export default ScoreSidebar;