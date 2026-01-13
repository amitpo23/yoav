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

interface ScrapedUrl {
  url: string;
  title: string;
  word_count: number;
  language: string;
  scraped_at: string;
}

interface MemoryStats {
  long_term_memories: number;
  user_profiles: number;
  learned_patterns: number;
  total_access_count: number;
}

const AdminPanel: React.FC<AdminPanelProps> = ({ onClose }) => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [scrapedUrls, setScrapedUrls] = useState<ScrapedUrl[]>([]);
  const [memoryStats, setMemoryStats] = useState<MemoryStats | null>(null);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'skills' | 'knowledge' | 'memory'>('dashboard');
  const [loading, setLoading] = useState(false);
  
  // URL Scraping form
  const [newUrl, setNewUrl] = useState('');
  const [scrapeCategory, setScrapeCategory] = useState('general');
  const [crawlEnabled, setCrawlEnabled] = useState(false);
  const [maxPages, setMaxPages] = useState(10);
  
  // Memory form
  const [newMemory, setNewMemory] = useState('');
  const [memoryType, setMemoryType] = useState('fact');
  const [memoryImportance, setMemoryImportance] = useState(0.5);

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
      } else if (activeTab === 'knowledge') {
        const response = await apiService.get('/api/knowledge/scraped-urls');
        setScrapedUrls(response.data.urls || []);
      } else if (activeTab === 'memory') {
        const response = await apiService.get('/api/memory/stats');
        setMemoryStats(response.data);
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

  const handleScrapeUrl = async () => {
    if (!newUrl) return;
    setLoading(true);
    try {
      const response = await apiService.post('/api/knowledge/scrape-url', {
        url: newUrl,
        category: scrapeCategory,
        crawl: crawlEnabled,
        max_pages: maxPages
      });
      alert(response.data.message);
      setNewUrl('');
      loadData();
    } catch (error: any) {
      alert('שגיאה בסריקת URL: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUrl = async (url: string) => {
    if (!window.confirm('למחוק את הURL?')) return;
    try {
      await apiService.delete(`/api/knowledge/scraped-url/${encodeURIComponent(url)}`);
      loadData();
    } catch (error) {
      alert('שגיאה במחיקת URL');
    }
  };

  const handleRefreshUrls = async () => {
    setLoading(true);
    try {
      const response = await apiService.post('/api/knowledge/refresh-urls');
      alert(`רענון הושלם: ${response.data.results.updated} עודכנו, ${response.data.results.unchanged} ללא שינוי`);
      loadData();
    } catch (error) {
      alert('שגיאה ברענון');
    } finally {
      setLoading(false);
    }
  };

  const handleAddMemory = async () => {
    if (!newMemory) return;
    setLoading(true);
    try {
      await apiService.post('/api/memory/remember', {
        content: newMemory,
        memory_type: memoryType,
        importance: memoryImportance
      });
      alert('הזיכרון נשמר בהצלחה');
      setNewMemory('');
      loadData();
    } catch (error) {
      alert('שגיאה בשמירת הזיכרון');
    } finally {
      setLoading(false);
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
            className={activeTab === 'knowledge' ? 'active' : ''}
            onClick={() => setActiveTab('knowledge')}
          >
            🌐 מאגר ידע / URLs
          </button>
          <button
            className={activeTab === 'memory' ? 'active' : ''}
            onClick={() => setActiveTab('memory')}
          >
            🧠 זיכרון
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

          {activeTab === 'knowledge' && (
            <div className="knowledge-view">
              <div className="url-scraper-form">
                <h3>🌐 הוסף URL למאגר הידע</h3>
                <div className="form-row">
                  <input
                    type="url"
                    value={newUrl}
                    onChange={(e) => setNewUrl(e.target.value)}
                    placeholder="https://example.com"
                    className="url-input"
                  />
                </div>
                <div className="form-row">
                  <select 
                    value={scrapeCategory} 
                    onChange={(e) => setScrapeCategory(e.target.value)}
                    className="category-select"
                  >
                    <option value="general">כללי</option>
                    <option value="documentation">תיעוד</option>
                    <option value="faq">שאלות נפוצות</option>
                    <option value="tutorial">מדריכים</option>
                  </select>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={crawlEnabled}
                      onChange={(e) => setCrawlEnabled(e.target.checked)}
                    />
                    סרוק כל האתר
                  </label>
                  {crawlEnabled && (
                    <input
                      type="number"
                      value={maxPages}
                      onChange={(e) => setMaxPages(parseInt(e.target.value))}
                      min="1"
                      max="50"
                      className="max-pages-input"
                      placeholder="מקסימום דפים"
                    />
                  )}
                </div>
                <div className="form-actions">
                  <button 
                    className="action-btn primary" 
                    onClick={handleScrapeUrl}
                    disabled={loading || !newUrl}
                  >
                    {loading ? '⏳ סורק...' : '🔍 סרוק והוסף'}
                  </button>
                  <button 
                    className="action-btn" 
                    onClick={handleRefreshUrls}
                    disabled={loading}
                  >
                    🔄 רענן הכל
                  </button>
                </div>
              </div>

              <div className="scraped-urls-list">
                <h3>📋 URLs שנסרקו ({scrapedUrls.length})</h3>
                {scrapedUrls.length === 0 ? (
                  <p className="empty-state">אין URLs שנסרקו עדיין</p>
                ) : (
                  <table className="urls-table">
                    <thead>
                      <tr>
                        <th>כותרת</th>
                        <th>מילים</th>
                        <th>שפה</th>
                        <th>נסרק</th>
                        <th>פעולות</th>
                      </tr>
                    </thead>
                    <tbody>
                      {scrapedUrls.map((item, index) => (
                        <tr key={index}>
                          <td>
                            <a href={item.url} target="_blank" rel="noopener noreferrer">
                              {item.title.substring(0, 40)}...
                            </a>
                          </td>
                          <td>{item.word_count}</td>
                          <td>{item.language === 'he' ? '🇮🇱' : '🇺🇸'}</td>
                          <td>{new Date(item.scraped_at).toLocaleDateString('he-IL')}</td>
                          <td>
                            <button 
                              className="delete-btn"
                              onClick={() => handleDeleteUrl(item.url)}
                            >
                              🗑️
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          )}

          {activeTab === 'memory' && (
            <div className="memory-view">
              <div className="memory-stats-grid">
                <div className="stat-card">
                  <div className="stat-icon">🧠</div>
                  <div className="stat-value">{memoryStats?.long_term_memories || 0}</div>
                  <div className="stat-label">זיכרונות</div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">👤</div>
                  <div className="stat-value">{memoryStats?.user_profiles || 0}</div>
                  <div className="stat-label">פרופילים</div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">📈</div>
                  <div className="stat-value">{memoryStats?.learned_patterns || 0}</div>
                  <div className="stat-label">דפוסים נלמדו</div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">🔄</div>
                  <div className="stat-value">{memoryStats?.total_access_count || 0}</div>
                  <div className="stat-label">גישות לזיכרון</div>
                </div>
              </div>

              <div className="add-memory-form">
                <h3>➕ הוסף זיכרון חדש</h3>
                <textarea
                  value={newMemory}
                  onChange={(e) => setNewMemory(e.target.value)}
                  placeholder="הזן מידע לשמירה בזיכרון..."
                  rows={3}
                />
                <div className="form-row">
                  <select value={memoryType} onChange={(e) => setMemoryType(e.target.value)}>
                    <option value="fact">עובדה</option>
                    <option value="preference">העדפה</option>
                    <option value="learning">למידה</option>
                    <option value="rule">כלל</option>
                  </select>
                  <label>
                    חשיבות:
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={memoryImportance}
                      onChange={(e) => setMemoryImportance(parseFloat(e.target.value))}
                    />
                    {memoryImportance}
                  </label>
                </div>
                <button 
                  className="action-btn primary"
                  onClick={handleAddMemory}
                  disabled={loading || !newMemory}
                >
                  💾 שמור בזיכרון
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;
