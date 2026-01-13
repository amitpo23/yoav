import React, { useState, useEffect } from 'react';
import './InstallPrompt.css';

interface InstallPromptProps {
  onDismiss?: () => void;
}

const InstallPrompt: React.FC<InstallPromptProps> = ({ onDismiss }) => {
  const [showPrompt, setShowPrompt] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);

  useEffect(() => {
    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
      return;
    }

    // Check localStorage for dismissal
    const dismissed = localStorage.getItem('pwa-prompt-dismissed');
    if (dismissed) {
      const dismissedTime = parseInt(dismissed, 10);
      // Show again after 7 days
      if (Date.now() - dismissedTime < 7 * 24 * 60 * 60 * 1000) {
        return;
      }
    }

    // Listen for install available event
    const handleInstallAvailable = () => {
      setShowPrompt(true);
    };

    window.addEventListener('pwa-install-available', handleInstallAvailable);
    
    // Check if install prompt is already available
    if ((window as any).deferredPrompt) {
      setShowPrompt(true);
    }

    return () => {
      window.removeEventListener('pwa-install-available', handleInstallAvailable);
    };
  }, []);

  const handleInstall = async () => {
    const installPWA = (window as any).installPWA;
    if (installPWA) {
      const installed = await installPWA();
      if (installed) {
        setShowPrompt(false);
        setIsInstalled(true);
      }
    }
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    localStorage.setItem('pwa-prompt-dismissed', Date.now().toString());
    onDismiss?.();
  };

  if (!showPrompt || isInstalled) return null;

  return (
    <div className="install-prompt">
      <div className="install-content">
        <div className="install-icon">📱</div>
        <div className="install-text">
          <h3>התקן את האפליקציה</h3>
          <p>גישה מהירה יותר וחוויה טובה יותר</p>
        </div>
      </div>
      <div className="install-actions">
        <button className="install-btn primary" onClick={handleInstall}>
          התקן
        </button>
        <button className="install-btn secondary" onClick={handleDismiss}>
          לא עכשיו
        </button>
      </div>
    </div>
  );
};

export default InstallPrompt;
