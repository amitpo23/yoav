import React from 'react';
import './SkillsPanel.css';

interface SkillsPanelProps {
  activeSkills: string[];
}

interface Skill {
  id: string;
  name: string;
  icon: string;
  description: string;
  category: string;
}

const SkillsPanel: React.FC<SkillsPanelProps> = ({ activeSkills }) => {
  const skills: Skill[] = [
    {
      id: 'knowledge-search',
      name: 'חיפוש ידע',
      icon: '🔍',
      description: 'חיפוש במאגר הידע המקצועי',
      category: 'search'
    },
    {
      id: 'reservation-management',
      name: 'ניהול הזמנות',
      icon: '📅',
      description: 'עזרה בניהול והזמנת חדרים',
      category: 'reservations'
    },
    {
      id: 'report-generation',
      name: 'יצירת דוחות',
      icon: '📊',
      description: 'הפקת דוחות ואנליטיקה',
      category: 'reports'
    },
    {
      id: 'troubleshooting',
      name: 'פתרון בעיות',
      icon: '🛠️',
      description: 'תמיכה טכנית ופתרון תקלות',
      category: 'troubleshooting'
    },
    {
      id: 'authentication',
      name: 'אימות והרשאות',
      icon: '🔐',
      description: 'ניהול משתמשים והרשאות',
      category: 'authentication'
    },
    {
      id: 'room-management',
      name: 'ניהול חדרים',
      icon: '🏨',
      description: 'תפעול וניהול חדרי המלון',
      category: 'rooms'
    },
    {
      id: 'language-processing',
      name: 'עיבוד שפה',
      icon: '🗣️',
      description: 'הבנה וניתוח של שפה טבעית',
      category: 'language'
    },
    {
      id: 'memory-recall',
      name: 'זיכרון שיחה',
      icon: '🧠',
      description: 'זכירת הקשר והיסטוריה',
      category: 'memory'
    }
  ];

  return (
    <div className="skills-panel">
      <div className="skills-header">
        <h3>⚡ יכולות זמינות</h3>
        <span className="skills-count">{skills.length} Skills</span>
      </div>
      <div className="skills-grid">
        {skills.map((skill) => (
          <div
            key={skill.id}
            className={`skill-card ${activeSkills.includes(skill.category) ? 'active' : ''}`}
          >
            <div className="skill-icon">{skill.icon}</div>
            <div className="skill-info">
              <div className="skill-name">{skill.name}</div>
              <div className="skill-description">{skill.description}</div>
            </div>
            {activeSkills.includes(skill.category) && (
              <div className="skill-badge">
                <span className="badge-pulse"></span>
                פעיל
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default SkillsPanel;
