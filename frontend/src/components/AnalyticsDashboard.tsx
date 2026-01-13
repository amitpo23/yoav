import React, { useState, useEffect } from 'react';
import './AnalyticsDashboard.css';
import { apiService } from '../services/api';

interface OverviewData {
  period: string;
  total_messages: number;
  total_sessions: number;
  total_errors: number;
  avg_response_time_ms: number;
  avg_satisfaction: number;
  error_rate: number;
  messages_per_session: number;
}

interface SkillData {
  skill: string;
  count: number;
  percentage: number;
}

interface DailyTrend {
  date: string;
  messages: number;
  sessions: number;
  errors: number;
}

interface HourlyData {
  hour: number;
  count: number;
}

interface AnalyticsData {
  overview: OverviewData;
  skills: { skills: SkillData[]; total_skill_activations: number };
  hourly_distribution: { distribution: HourlyData[] };
  daily_trends: DailyTrend[];
  performance: {
    avg_response_time_ms: number;
    p50_response_time_ms: number;
    p95_response_time_ms: number;
    p99_response_time_ms: number;
  };
}

const AnalyticsDashboard: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('7d');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnalytics();
  }, [period]);

  const loadAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiService.getAnalytics(period);
      setData(response);
    } catch (err) {
      setError('שגיאה בטעינת הנתונים');
      console.error('Error loading analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="analytics-loading">
        <div className="loading-spinner"></div>
        <span>טוען נתונים...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-error">
        <span>⚠️</span>
        <p>{error}</p>
        <button onClick={loadAnalytics}>נסה שוב</button>
      </div>
    );
  }

  if (!data) return null;

  const maxHourlyCount = Math.max(...data.hourly_distribution.distribution.map(h => h.count), 1);
  const maxDailyMessages = Math.max(...data.daily_trends.map(d => d.messages), 1);

  return (
    <div className="analytics-dashboard">
      <div className="analytics-header">
        <h2>📊 אנליטיקה מתקדמת</h2>
        <div className="period-selector">
          {['1d', '7d', '30d'].map(p => (
            <button
              key={p}
              className={period === p ? 'active' : ''}
              onClick={() => setPeriod(p)}
            >
              {p === '1d' ? 'יום' : p === '7d' ? 'שבוע' : 'חודש'}
            </button>
          ))}
        </div>
      </div>

      {/* Overview Cards */}
      <div className="overview-cards">
        <div className="stat-card primary">
          <div className="stat-icon">💬</div>
          <div className="stat-content">
            <span className="stat-value">{data.overview.total_messages.toLocaleString()}</span>
            <span className="stat-label">הודעות</span>
          </div>
        </div>
        
        <div className="stat-card success">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <span className="stat-value">{data.overview.total_sessions.toLocaleString()}</span>
            <span className="stat-label">סשנים</span>
          </div>
        </div>
        
        <div className="stat-card warning">
          <div className="stat-icon">⚡</div>
          <div className="stat-content">
            <span className="stat-value">{data.overview.avg_response_time_ms}ms</span>
            <span className="stat-label">זמן תגובה ממוצע</span>
          </div>
        </div>
        
        <div className="stat-card danger">
          <div className="stat-icon">⚠️</div>
          <div className="stat-content">
            <span className="stat-value">{data.overview.error_rate}%</span>
            <span className="stat-label">שיעור שגיאות</span>
          </div>
        </div>
        
        <div className="stat-card info">
          <div className="stat-icon">⭐</div>
          <div className="stat-content">
            <span className="stat-value">{data.overview.avg_satisfaction || 'N/A'}</span>
            <span className="stat-label">שביעות רצון</span>
          </div>
        </div>
        
        <div className="stat-card secondary">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <span className="stat-value">{data.overview.messages_per_session}</span>
            <span className="stat-label">הודעות לסשן</span>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="charts-row">
        {/* Hourly Distribution */}
        <div className="chart-card">
          <h3>📅 התפלגות שעתית</h3>
          <div className="hourly-chart">
            {data.hourly_distribution.distribution.map(item => (
              <div key={item.hour} className="hour-bar-container">
                <div 
                  className="hour-bar"
                  style={{ height: `${(item.count / maxHourlyCount) * 100}%` }}
                  title={`${item.count} הודעות`}
                />
                <span className="hour-label">{item.hour}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Skills Usage */}
        <div className="chart-card">
          <h3>⚡ שימוש ב-Skills</h3>
          <div className="skills-chart">
            {data.skills.skills.slice(0, 5).map(skill => (
              <div key={skill.skill} className="skill-bar-row">
                <span className="skill-name">{skill.skill}</span>
                <div className="skill-bar-container">
                  <div 
                    className="skill-bar"
                    style={{ width: `${skill.percentage}%` }}
                  />
                  <span className="skill-value">{skill.count}</span>
                </div>
              </div>
            ))}
            {data.skills.skills.length === 0 && (
              <div className="no-data">אין נתונים</div>
            )}
          </div>
        </div>
      </div>

      {/* Daily Trends */}
      <div className="chart-card full-width">
        <h3>📈 מגמות יומיות</h3>
        <div className="daily-chart">
          {data.daily_trends.slice(-14).map(day => (
            <div key={day.date} className="day-column">
              <div className="day-bars">
                <div 
                  className="day-bar messages"
                  style={{ height: `${(day.messages / maxDailyMessages) * 100}%` }}
                  title={`${day.messages} הודעות`}
                />
                <div 
                  className="day-bar sessions"
                  style={{ height: `${(day.sessions / maxDailyMessages) * 50}%` }}
                  title={`${day.sessions} סשנים`}
                />
              </div>
              <span className="day-label">
                {new Date(day.date).toLocaleDateString('he-IL', { day: 'numeric', month: 'numeric' })}
              </span>
            </div>
          ))}
        </div>
        <div className="chart-legend">
          <span className="legend-item messages">● הודעות</span>
          <span className="legend-item sessions">● סשנים</span>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="chart-card">
        <h3>⚡ מדדי ביצועים</h3>
        <div className="performance-metrics">
          <div className="metric-row">
            <span className="metric-label">P50</span>
            <div className="metric-bar-container">
              <div 
                className="metric-bar p50"
                style={{ width: `${Math.min((data.performance.p50_response_time_ms / 1000) * 100, 100)}%` }}
              />
            </div>
            <span className="metric-value">{data.performance.p50_response_time_ms}ms</span>
          </div>
          <div className="metric-row">
            <span className="metric-label">P95</span>
            <div className="metric-bar-container">
              <div 
                className="metric-bar p95"
                style={{ width: `${Math.min((data.performance.p95_response_time_ms / 1000) * 100, 100)}%` }}
              />
            </div>
            <span className="metric-value">{data.performance.p95_response_time_ms}ms</span>
          </div>
          <div className="metric-row">
            <span className="metric-label">P99</span>
            <div className="metric-bar-container">
              <div 
                className="metric-bar p99"
                style={{ width: `${Math.min((data.performance.p99_response_time_ms / 1000) * 100, 100)}%` }}
              />
            </div>
            <span className="metric-value">{data.performance.p99_response_time_ms}ms</span>
          </div>
        </div>
      </div>

      <button className="refresh-btn" onClick={loadAnalytics}>
        🔄 רענן נתונים
      </button>
    </div>
  );
};

export default AnalyticsDashboard;
