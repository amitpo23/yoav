import React, { useState, useEffect, useRef } from 'react';
import './ChatInterface.css';
import { apiService, Message, ChatResponse } from '../services/api';
import MessageBubble from './MessageBubble';
import LoadingIndicator from './LoadingIndicator';

interface ChatInterfaceProps {
  sessionId: string | null;
  onSessionCreated: (sessionId: string) => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ sessionId, onSessionCreated }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (!sessionId) {
      setMessages([]);
    }
  }, [sessionId]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      const response: ChatResponse = await apiService.sendMessage({
        message: inputMessage,
        session_id: sessionId || undefined,
      });

      if (!sessionId) {
        onSessionCreated(response.session_id);
      }

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Error sending message:', err);
      
      // Show waking server message
      const wakingMessage: Message = {
        role: 'assistant',
        content: '🌙 מעיר את השרת... זה עלול לקחת כ-30 שניות בפעם הראשונה. אנא המתן...',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, wakingMessage]);
      
      // Wait 35 seconds
      await new Promise(resolve => setTimeout(resolve, 35000));
      
      try {
        // Retry the API call
        const response: ChatResponse = await apiService.sendMessage({
          message: inputMessage,
          session_id: sessionId || undefined,
        });

        if (!sessionId) {
          onSessionCreated(response.session_id);
        }

        const assistantMessage: Message = {
          role: 'assistant',
          content: response.response,
          timestamp: new Date().toISOString(),
        };

        // Replace waking message with actual response
        setMessages((prev) => [...prev.slice(0, -1), assistantMessage]);
      } catch (retryErr) {
        console.error('Error on retry:', retryErr);
        
        // Replace waking message with error
        const errorMessage: Message = {
          role: 'assistant',
          content: 'מצטער, אירעה שגיאה בתקשורת עם השרת. אנא נסה שוב מאוחר יותר.',
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev.slice(0, -1), errorMessage]);
      }
      
      setIsLoading(false);
    }
  };

  const quickQuestions = [
    'איך מתחברים למערכת?',
    'איך יוצרים הזמנה חדשה?',
    'איך מפיקים דוחות?',
    'בעיות טכניות נפוצות',
  ];

  const handleQuickQuestion = (question: string) => {
    setInputMessage(question);
  };

  return (
    <div className="chat-interface">
      <div className="messages-container">
        {messages.length === 0 && !isLoading && (
          <div className="welcome-screen">
            <div className="welcome-icon">🤖</div>
            <h2>שלום! אני כאן לעזור</h2>
            <p>אני יכול לעזור לך עם שאלות על מערכת ניהול בתי המלון</p>
            
            <div className="quick-questions">
              <p className="quick-questions-title">שאלות נפוצות:</p>
              <div className="quick-questions-grid">
                {quickQuestions.map((question, index) => (
                  <button
                    key={index}
                    className="quick-question-btn"
                    onClick={() => handleQuickQuestion(question)}
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <MessageBubble key={index} message={message} />
        ))}

        {isLoading && <LoadingIndicator />}
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className="input-container" onSubmit={handleSendMessage}>
        <input
          type="text"
          className="message-input"
          placeholder="הקלד את שאלתך כאן..."
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          disabled={isLoading}
        />
        <button
          type="submit"
          className="send-button"
          disabled={!inputMessage.trim() || isLoading}
        >
          <span className="send-icon">📤</span>
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;
