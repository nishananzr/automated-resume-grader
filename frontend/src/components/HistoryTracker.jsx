// frontend/src/components/HistoryTracker.jsx
import { useState, useEffect } from 'react';
const HistoryTracker = () => {
    const [history, setHistory] = useState([]);
    useEffect(() => { fetch('https://automated-resume-grader-backend.onrender.com/').then(res => res.json()).then(data => setHistory(data)); }, []);
    return (
        <div className="history-card">
            <h2>Recent Analyses</h2>
            {history.length > 0 ? (<ul>{history.map(item => (<li key={item.timestamp}><span>{new Date(item.timestamp * 1000).toLocaleTimeString()} - {item.filename.substring(0, 20)}</span><span className="history-score">{item.score}/100</span></li>))}</ul>) : <p>No history yet.</p>}
        </div>
    );
};
export default HistoryTracker;