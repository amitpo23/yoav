import React, { useState } from 'react';
import './Header.css';
import AdminPanel from './AdminPanel';

interface HeaderProps {
  onMenuClick: () => void;
}

const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
  const [showAdmin, setShowAdmin] = useState(false);

  return (
    <>
      <header className="header">
        <button className="menu-button" onClick={onMenuClick}>
          <span className="menu-icon">☰</span>
        </button>
        
        <div className="header-title">
          <h1>🏨 תמיכה טכנית AI</h1>
          <p className="subtitle">מערכות ניהול לבתי מלון</p>
        </div>
        
        <div className="header-actions">
          <button 
            className="admin-button"
            onClick={() => setShowAdmin(true)}
            title="פאנל ניהול"
          >
            🔧
          </button>
          <span className="status-indicator">
            <span className="status-dot"></span>
            פעיל
          </span>
        </div>
      </header>

      {showAdmin && <AdminPanel onClose={() => setShowAdmin(false)} />}
    </>
  );
};

export default Header;
