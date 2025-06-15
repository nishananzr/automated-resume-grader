import React from 'react';

const FeedbackCard = ({ detail }) => {
    const scorePercentage = (detail.score / detail.max_score) * 100;
    let icon;
    if (scorePercentage > 80) {
        icon = '✅'; // Green check
    } else if (scorePercentage > 50) {
        icon = '⚠️'; // Yellow warning
    } else {
        icon = '❌'; // Red X
    }

    return (
        <div className="feedback-card">
            <h3>{icon} {detail.name}</h3>
            <div className="score-bar">
                <div 
                    className="score-bar-fill" 
                    style={{ width: `${scorePercentage}%` }}
                ></div>
            </div>
            <p className="feedback-text">{detail.feedback}</p>
        </div>
    );
};

export default FeedbackCard;