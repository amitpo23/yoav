import React, { useState } from 'react';
import './App.css';
import EnhancedChatInterface from './components/EnhancedChatInterface';
import Header from './components/Header';
import Sidebar from './components/Sidebar';

function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [showSidebar, setShowSidebar] = useState(false);

  const handleNewChat = () => {
    setSessionId(null);
  };

  return (
    <div className="App">
      <Header onMenuClick={() => setShowSidebar(!showSidebar)} />
      
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
    </div>
  );
}

export default App;
