import React from 'react';
import './Sidebar.css';

interface SidebarProps {
  onNewChat: () => void;
  currentSessionId: string | null;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ onNewChat, currentSessionId, onClose }) => {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h3>היסטוריה</h3>
        <button className="close-button" onClick={onClose}>
          ✕
        </button>
      </div>

      <button className="new-chat-button" onClick={onNewChat}>
        <span className="button-icon">➕</span>
        שיחה חדשה
      </button>

      <div className="sessions-list">
        {currentSessionId && (
          <div className="session-item active">
            <span className="session-icon">💬</span>
            <div className="session-info">
              <div className="session-title">שיחה נוכחית</div>
              <div className="session-id">{currentSessionId.substring(0, 8)}...</div>
            </div>
          </div>
        )}
      </div>

      <div className="sidebar-footer">
        <div className="info-section">
          <h4>מידע נוסף</h4>
          <ul>
            <li>📚 מדריכי שימוש</li>
            <li>🔧 תמיכה טכנית</li>
            <li>📞 צור קשר</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
