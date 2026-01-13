import React, { useState, useEffect } from 'react';
import './App.css';
import EnhancedChatInterface from './components/EnhancedChatInterface';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import InstallPrompt from './components/InstallPrompt';
import { wsService } from './services/websocket';

function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [showSidebar, setShowSidebar] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    // Connect WebSocket when session is created
    if (sessionId) {
      wsService.connect(sessionId).catch(console.error);
    }

    return () => {
      wsService.disconnect();
    };
  }, [sessionId]);

  useEffect(() => {
    // Online/Offline detection
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const handleNewChat = () => {
    setSessionId(null);
  };

  return (
    <div className="App">
      <Header onMenuClick={() => setShowSidebar(!showSidebar)} />
      
      {!isOnline && (
        <div className="offline-banner">
          📡 אין חיבור לאינטרנט. חלק מהפונקציות לא יעבדו.
        </div>
      )}
      
      <div className="app-container">
        {showSidebar && (
          <Sidebar
            onNewChat={handleNewChat}
            currentSessionId={sessionId}
            onClose={() => setShowSidebar(false)}
          />
        )}
        
        <main className="main-content">
          <EnhancedChatInterface
            sessionId={sessionId}
            onSessionCreated={setSessionId}
          />
        </main>
      </div>
      
      <InstallPrompt />
    </div>
  );
}

export default App;
