import { PieChart } from 'react-minimal-pie-chart';

const ScoreGauge = ({ score }) => {
  const scoreColor = score > 80 ? '#28a745' : score > 50 ? '#ffc107' : '#dc3545';
  
  return (
    <div className="score-gauge-container">
      <PieChart
        data={[{ value: score, key: 1, color: scoreColor }]}
        totalValue={100}
        lineWidth={20}
        background="#e9ecef"
        startAngle={-90}
        animate
        label={() => `${score}`}
        labelStyle={{
          fontSize: '24px',
          fontFamily: 'sans-serif',
          fontWeight: 'bold',
          fill: scoreColor,
        }}
        labelPosition={0}
      />
    </div>
  );
};

export default ScoreGauge;