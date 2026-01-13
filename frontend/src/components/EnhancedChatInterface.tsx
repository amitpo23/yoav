import React, { useState, useEffect, useRef } from 'react';
import './EnhancedChatInterface.css';
import { apiService, Message, ChatResponse } from '../services/api';
import MessageBubble from './MessageBubble';
import LoadingIndicator from './LoadingIndicator';
import SkillsPanel from './SkillsPanel';
import ThinkingProcess from './ThinkingProcess';

interface EnhancedChatInterfaceProps {
  sessionId: string | null;
  onSessionCreated: (sessionId: string) => void;
}

const EnhancedChatInterface: React.FC<EnhancedChatInterfaceProps> = ({ sessionId, onSessionCreated }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSkills, setShowSkills] = useState(true);
  const [activeSkills, setActiveSkills] = useState<string[]>([]);
  const [thinking, setThinking] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, thinking]);

  useEffect(() => {
    if (!sessionId) {
      setMessages([]);
      setSuggestions(generateSmartSuggestions([]));
    }
  }, [sessionId]);

  useEffect(() => {
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [inputMessage]);

  const generateSmartSuggestions = (messages: Message[]): string[] => {
    if (messages.length === 0) {
      return [
        'איך מתחברים למערכת?',
        'צור דוח תפוסה חודשי',
        'הסבר על ניהול הזמנות',
        'פתור בעיית הדפסה',
      ];
    }
    // Generate contextual suggestions based on conversation
    return [
      'ספר לי עוד',
      'תן דוגמה',
      'מה עוד אפשר לעשות?',
    ];
  };

  const handleSendMessage = async (message?: string) => {
    const textToSend = message || inputMessage;
    if (!textToSend.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: textToSend,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);
    setThinking('מנתח את השאלה...');

    try {
      // Simulate thinking process
      setTimeout(() => setThinking('מחפש במאגר הידע...'), 500);
      setTimeout(() => setThinking('יוצר תשובה מותאמת אישית...'), 1000);

      const response: ChatResponse = await apiService.sendMessage({
        message: textToSend,
        session_id: sessionId || undefined,
      });

      if (!sessionId) {
        onSessionCreated(response.session_id);
      }

      setThinking(null);

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      
      // Update suggestions based on new context
      setSuggestions(generateSmartSuggestions([...messages, userMessage, assistantMessage]));

      // Extract used skills from response
      if (response.sources && response.sources.length > 0) {
        setActiveSkills(response.sources.map(s => s.category));
      }

    } catch (err) {
      console.error('Error sending message:', err);
      setError('שגיאה בשליחת ההודעה. אנא נסה שוב.');
      setThinking(null);
      
      const errorMessage: Message = {
        role: 'assistant',
        content: 'מצטער, אירעה שגיאה. אנא ודא שהשרת פועל ונסה שוב.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const quickActions = [
    { icon: '📊', label: 'דוח', action: 'צור דוח תפוסה לחודש האחרון' },
    { icon: '🔍', label: 'חיפוש', action: 'חפש הזמנה' },
    { icon: '➕', label: 'הזמנה', action: 'איך יוצרים הזמנה חדשה?' },
    { icon: '🛠️', label: 'תמיכה', action: 'בעיות טכניות נפוצות' },
  ];

  return (
    <div className="enhanced-chat-interface">
      <div className="chat-header">
        <div className="header-info">
          <div className="model-indicator">
            <span className="model-icon">🤖</span>
            <div className="model-details">
              <span className="model-name">AI Assistant Pro</span>
              <span className="model-status">• מקוון</span>
            </div>
          </div>
        </div>
        <button 
          className="skills-toggle"
          onClick={() => setShowSkills(!showSkills)}
        >
          <span className="skills-icon">⚡</span>
          Skills {showSkills ? '▼' : '▲'}
        </button>
      </div>

      {showSkills && (
        <SkillsPanel activeSkills={activeSkills} />
      )}

      <div className="messages-area">
        {messages.length === 0 && !isLoading && (
          <div className="welcome-screen-enhanced">
            <div className="welcome-hero">
              <div className="hero-icon">🤖</div>
              <h1>שלום! אני העוזר החכם שלך</h1>
              <p className="hero-subtitle">
                אני כאן לעזור לך עם כל שאלה על מערכת ניהול בתי המלון
              </p>
            </div>

            <div className="quick-actions-grid">
              {quickActions.map((action, index) => (
                <button
                  key={index}
                  className="quick-action-card"
                  onClick={() => handleSendMessage(action.action)}
                >
                  <span className="action-icon">{action.icon}</span>
                  <span className="action-label">{action.label}</span>
                </button>
              ))}
            </div>

            <div className="suggestions-section">
              <h3>או נסה את אלה:</h3>
              <div className="suggestions-grid">
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    className="suggestion-chip"
                    onClick={() => handleSendMessage(suggestion)}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        <div className="messages-list">
          {messages.map((message, index) => (
            <MessageBubble key={index} message={message} />
          ))}

          {thinking && <ThinkingProcess message={thinking} />}
          {isLoading && !thinking && <LoadingIndicator />}
        </div>

        {error && (
          <div className="error-banner">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}

        {messages.length > 0 && !isLoading && suggestions.length > 0 && (
          <div className="contextual-suggestions">
            <span className="suggestions-label">המשך:</span>
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                className="context-chip"
                onClick={() => handleSendMessage(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="input-area-enhanced">
        <div className="input-container-enhanced">
          <textarea
            ref={textareaRef}
            className="message-input-enhanced"
            placeholder="שאל אותי כל דבר... (Enter לשליחה, Shift+Enter לשורה חדשה)"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            rows={1}
          />
          <button
            className="send-button-enhanced"
            onClick={() => handleSendMessage()}
            disabled={!inputMessage.trim() || isLoading}
          >
            {isLoading ? (
              <span className="sending-icon">⏳</span>
            ) : (
              <span className="send-icon">➤</span>
            )}
          </button>
        </div>
        <div className="input-footer">
          <span className="input-hint">
            העוזר החכם משתמש ב-AI מתקדם ומאגר ידע מקצועי
          </span>
        </div>
      </div>
    </div>
  );
};

export default EnhancedChatInterface;
