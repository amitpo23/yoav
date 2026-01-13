import React, { useState, useEffect } from 'react';
import './AdminPanel.css';
import { apiService } from '../services/api';

interface AdminPanelProps {
  onClose: () => void;
}

interface Stats {
  total_sessions: number;
  active_sessions: number;
  total_messages: number;
  total_knowledge_items: number;
  available_skills: number;
  uptime: string;
}

interface Skill {
  name: string;
  description: string;
  category: string;
  enabled: boolean;
}

const AdminPanel: React.FC<AdminPanelProps> = ({ onClose }) => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'skills' | 'sessions' | 'knowledge'>('dashboard');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'dashboard') {
        const response = await apiService.get('/api/admin/stats');
        setStats(response.data);
      } else if (activeTab === 'skills') {
        const response = await apiService.get('/api/skills');
        setSkills(response.data.skills);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCleanup = async () => {
    if (!window.confirm('האם למחוק סשנים ישנים?')) return;
    
    try {
      await apiService.post('/api/admin/system/cleanup', { hours: 24 });
      alert('סשנים ישנים נוקו בהצלחה');
      loadData();
    } catch (error) {
      alert('שגיאה בניקוי סשנים');
    }
  };

  return (
    <div className="admin-panel-overlay">
      <div className="admin-panel">
        <div className="admin-header">
          <h2>🔧 פאנל ניהול</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="admin-tabs">
          <button
            className={activeTab === 'dashboard' ? 'active' : ''}
            onClick={() => setActiveTab('dashboard')}
          >
            📊 דאשבורד
          </button>
          <button
            className={activeTab === 'skills' ? 'active' : ''}
            onClick={() => setActiveTab('skills')}
          >
            ⚡ Skills
          </button>
          <button
            className={activeTab === 'sessions' ? 'active' : ''}
            onClick={() => setActiveTab('sessions')}
          >
            💬 סשנים
          </button>
          <button
            className={activeTab === 'knowledge' ? 'active' : ''}
            onClick={() => setActiveTab('knowledge')}
          >
            📚 מאגר ידע
          </button>
        </div>

        <div className="admin-content">
          {loading && <div className="loading">טוען...</div>}

          {activeTab === 'dashboard' && stats && (
            <div className="dashboard">
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-icon">💬</div>
                  <div className="stat-value">{stats.total_sessions}</div>
                  <div className="stat-label">סה"כ סשנים</div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">✅</div>
                  <div className="stat-value">{stats.active_sessions}</div>
                  <div className="stat-label">סשנים פעילים</div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">📝</div>
                  <div className="stat-value">{stats.total_messages}</div>
                  <div className="stat-label">סה"כ הודעות</div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">📚</div>
                  <div className="stat-value">{stats.total_knowledge_items}</div>
                  <div className="stat-label">פריטי ידע</div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">⚡</div>
                  <div className="stat-value">{stats.available_skills}</div>
                  <div className="stat-label">Skills זמינים</div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">⏱️</div>
                  <div className="stat-value">{stats.uptime}</div>
                  <div className="stat-label">סטטוס מערכת</div>
                </div>
              </div>

              <div className="admin-actions">
                <button className="action-btn" onClick={handleCleanup}>
                  🧹 נקה סשנים ישנים
                </button>
                <button className="action-btn" onClick={loadData}>
                  🔄 רענן נתונים
                </button>
              </div>
            </div>
          )}

          {activeTab === 'skills' && (
            <div className="skills-list">
              {skills.map((skill, index) => (
                <div key={index} className="skill-item">
                  <div className="skill-info">
                    <h3>{skill.name}</h3>
                    <p>{skill.description}</p>
                    <span className="skill-category">{skill.category}</span>
                  </div>
                  <div className="skill-status">
                    <span className={`status-badge ${skill.enabled ? 'enabled' : 'disabled'}`}>
                      {skill.enabled ? 'פעיל' : 'כבוי'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'sessions' && (
            <div className="sessions-view">
              <p>מידע על סשנים פעילים...</p>
            </div>
          )}

          {activeTab === 'knowledge' && (
            <div className="knowledge-view">
              <p>ניהול מאגר הידע...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;
