import React from 'react';
import './LoadingIndicator.css';

const LoadingIndicator: React.FC = () => {
  return (
    <div className="loading-indicator">
      <div className="loading-avatar">🤖</div>
      <div className="loading-content">
        <div className="loading-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  );
};

export default LoadingIndicator;
