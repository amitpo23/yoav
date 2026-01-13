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

interface ConversationLog {
  session_id: string;
  timestamp: string;
  role: string;
  message: string;
  response_time_ms?: number;
  skills_used?: string[];
}

interface DailyReport {
  date: string;
  total_conversations: number;
  total_messages: number;
  avg_response_time_ms: number;
  top_topics: { topic: string; count: number }[];
  skills_usage: { [key: string]: number };
}

interface WeeklyReport {
  period: string;
  total_messages: number;
  total_sessions: number;
  daily_breakdown: { date: string; messages: number; sessions: number }[];
  top_topics: { topic: string; count: number }[];
  avg_response_time: number;
}

interface RealtimeStats {
  messages_last_hour: number;
  active_sessions_today: number;
  messages_today: number;
  current_hour: number;
  last_message_time: string | null;
}

const AdminPanel: React.FC<AdminPanelProps> = ({ onClose }) => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [scrapedUrls, setScrapedUrls] = useState<ScrapedUrl[]>([]);
  const [memoryStats, setMemoryStats] = useState<MemoryStats | null>(null);
  const [logs, setLogs] = useState<ConversationLog[]>([]);
  const [realtimeStats, setRealtimeStats] = useState<RealtimeStats | null>(null);
  const [weeklyReport, setWeeklyReport] = useState<WeeklyReport | null>(null);
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  const [sessionMessages, setSessionMessages] = useState<ConversationLog[]>([]);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'skills' | 'knowledge' | 'memory' | 'logs' | 'reports'>('dashboard');
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
      } else if (activeTab === 'logs') {
        const [logsRes, realtimeRes] = await Promise.all([
          apiService.get('/api/logs?limit=50'),
          apiService.get('/api/logs/realtime')
        ]);
        setLogs(logsRes.data.logs || []);
        setRealtimeStats(realtimeRes.data);
      } else if (activeTab === 'reports') {
        const response = await apiService.get('/api/reports/weekly');
        setWeeklyReport(response.data);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSessionMessages = async (sessionId: string) => {
    try {
      const response = await apiService.get(`/api/logs/session/${sessionId}`);
      setSessionMessages(response.data.messages || []);
      setSelectedSession(sessionId);
    } catch (error) {
      console.error('Error loading session:', error);
    }
  };

  const exportLogs = async (format: 'json' | 'csv') => {
    try {
      const response = await apiService.get(`/api/logs/export?format=${format}`);
      const blob = new Blob([response.data], { 
        type: format === 'csv' ? 'text/csv' : 'application/json' 
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `conversation_logs.${format}`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      alert('שגיאה בייצוא לוגים');
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
          <button
            className={activeTab === 'logs' ? 'active' : ''}
            onClick={() => setActiveTab('logs')}
          >
            📜 לוגים
          </button>
          <button
            className={activeTab === 'reports' ? 'active' : ''}
            onClick={() => setActiveTab('reports')}
          >
            📈 דוחות
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

          {activeTab === 'logs' && (
            <div className="logs-view">
              {realtimeStats && (
                <div className="realtime-stats">
                  <div className="realtime-stat">
                    <span className="stat-icon">⏰</span>
                    <span className="stat-value">{realtimeStats.messages_last_hour}</span>
                    <span className="stat-label">הודעות בשעה האחרונה</span>
                  </div>
                  <div className="realtime-stat">
                    <span className="stat-icon">👥</span>
                    <span className="stat-value">{realtimeStats.active_sessions_today}</span>
                    <span className="stat-label">סשנים היום</span>
                  </div>
                  <div className="realtime-stat">
                    <span className="stat-icon">💬</span>
                    <span className="stat-value">{realtimeStats.messages_today}</span>
                    <span className="stat-label">הודעות היום</span>
                  </div>
                </div>
              )}

              <div className="logs-actions">
                <button className="action-btn" onClick={() => exportLogs('json')}>
                  📥 ייצא JSON
                </button>
                <button className="action-btn" onClick={() => exportLogs('csv')}>
                  📥 ייצא CSV
                </button>
                <button className="action-btn" onClick={loadData}>
                  🔄 רענן
                </button>
              </div>

              {selectedSession ? (
                <div className="session-detail">
                  <div className="session-header">
                    <h3>📝 שיחה: {selectedSession.substring(0, 8)}...</h3>
                    <button className="back-btn" onClick={() => setSelectedSession(null)}>
                      ← חזור
                    </button>
                  </div>
                  <div className="session-messages">
                    {sessionMessages.map((msg, index) => (
                      <div key={index} className={`log-message ${msg.role}`}>
                        <div className="message-header">
                          <span className="role">{msg.role === 'user' ? '👤 משתמש' : '🤖 בוט'}</span>
                          <span className="time">
                            {new Date(msg.timestamp).toLocaleTimeString('he-IL')}
                          </span>
                          {msg.response_time_ms && (
                            <span className="response-time">{msg.response_time_ms}ms</span>
                          )}
                        </div>
                        <div className="message-content">{msg.message}</div>
                        {msg.skills_used && msg.skills_used.length > 0 && (
                          <div className="skills-used">
                            ⚡ {msg.skills_used.join(', ')}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="logs-list">
                  <h3>📜 לוגים אחרונים ({logs.length})</h3>
                  <table className="logs-table">
                    <thead>
                      <tr>
                        <th>זמן</th>
                        <th>סשן</th>
                        <th>תפקיד</th>
                        <th>הודעה</th>
                        <th>זמן תגובה</th>
                      </tr>
                    </thead>
                    <tbody>
                      {logs.map((log, index) => (
                        <tr key={index} onClick={() => loadSessionMessages(log.session_id)}>
                          <td>{new Date(log.timestamp).toLocaleTimeString('he-IL')}</td>
                          <td className="session-id">{log.session_id.substring(0, 8)}...</td>
                          <td>{log.role === 'user' ? '👤' : '🤖'}</td>
                          <td className="message-preview">{log.message.substring(0, 50)}...</td>
                          <td>{log.response_time_ms ? `${log.response_time_ms}ms` : '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {activeTab === 'reports' && (
            <div className="reports-view">
              {weeklyReport && (
                <>
                  <div className="report-header">
                    <h3>📊 דוח שבועי</h3>
                    <span className="period">{weeklyReport.period}</span>
                  </div>

                  <div className="report-summary">
                    <div className="summary-card">
                      <div className="summary-icon">💬</div>
                      <div className="summary-value">{weeklyReport.total_messages}</div>
                      <div className="summary-label">סה"כ הודעות</div>
                    </div>
                    <div className="summary-card">
                      <div className="summary-icon">👥</div>
                      <div className="summary-value">{weeklyReport.total_sessions}</div>
                      <div className="summary-label">סה"כ סשנים</div>
                    </div>
                    <div className="summary-card">
                      <div className="summary-icon">⏱️</div>
                      <div className="summary-value">{Math.round(weeklyReport.avg_response_time)}ms</div>
                      <div className="summary-label">זמן תגובה ממוצע</div>
                    </div>
                  </div>

                  <div className="report-section">
                    <h4>📅 פירוט יומי</h4>
                    <div className="daily-chart">
                      {weeklyReport.daily_breakdown.map((day, index) => (
                        <div key={index} className="day-bar">
                          <div 
                            className="bar" 
                            style={{ 
                              height: `${Math.min(100, (day.messages / Math.max(...weeklyReport.daily_breakdown.map(d => d.messages || 1))) * 100)}%` 
                            }}
                          >
                            <span className="bar-value">{day.messages}</span>
                          </div>
                          <span className="day-label">
                            {new Date(day.date).toLocaleDateString('he-IL', { weekday: 'short' })}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="report-section">
                    <h4>🏷️ נושאים פופולריים</h4>
                    <div className="topics-list">
                      {weeklyReport.top_topics.slice(0, 5).map((topic, index) => (
                        <div key={index} className="topic-item">
                          <span className="topic-name">{topic.topic}</span>
                          <span className="topic-count">{topic.count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              )}

              {!weeklyReport && !loading && (
                <div className="empty-state">
                  <p>📊 אין עדיין מספיק נתונים לדוח שבועי</p>
                  <p>התחל שיחות עם הסוכן כדי לצבור סטטיסטיקות</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;
