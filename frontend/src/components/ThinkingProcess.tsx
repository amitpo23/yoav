import React from 'react';
import './ThinkingProcess.css';

interface ThinkingProcessProps {
  message: string;
}

const ThinkingProcess: React.FC<ThinkingProcessProps> = ({ message }) => {
  return (
    <div className="thinking-process">
      <div className="thinking-avatar">
        <div className="brain-icon">🧠</div>
        <div className="thinking-waves">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
      <div className="thinking-content">
        <div className="thinking-label">חושב...</div>
        <div className="thinking-message">{message}</div>
        <div className="thinking-progress">
          <div className="progress-bar"></div>
        </div>
      </div>
    </div>
  );
};

export default ThinkingProcess;
