import React, { useState, useRef, useCallback } from 'react';
import './VoiceInput.css';

interface VoiceInputProps {
  onTranscript: (text: string) => void;
  disabled?: boolean;
  language?: string;
}

declare global {
  interface Window {
    webkitSpeechRecognition: any;
    SpeechRecognition: any;
  }
}

const VoiceInput: React.FC<VoiceInputProps> = ({
  onTranscript,
  disabled = false,
  language = 'he-IL'
}) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [volume, setVolume] = useState(0);
  const recognitionRef = useRef<any>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);

  const startListening = useCallback(() => {
    setError(null);
    setTranscript('');

    // Check browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      setError('הדפדפן שלך לא תומך בזיהוי קול. נסה Chrome או Edge.');
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognitionRef.current = recognition;

      recognition.lang = language;
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        setIsListening(true);
        startVolumeMonitor();
      };

      recognition.onresult = (event: any) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }

        setTranscript(finalTranscript || interimTranscript);
        
        if (finalTranscript) {
          onTranscript(finalTranscript);
        }
      };

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        switch (event.error) {
          case 'no-speech':
            setError('לא זוהה דיבור. נסה שוב.');
            break;
          case 'audio-capture':
            setError('לא נמצא מיקרופון. בדוק את החיבור.');
            break;
          case 'not-allowed':
            setError('נדרשת הרשאה לשימוש במיקרופון.');
            break;
          default:
            setError(`שגיאה: ${event.error}`);
        }
        stopListening();
      };

      recognition.onend = () => {
        setIsListening(false);
        stopVolumeMonitor();
      };

      recognition.start();
    } catch (err) {
      setError('שגיאה בהפעלת זיהוי קול');
      console.error(err);
    }
  }, [language, onTranscript]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setIsListening(false);
    stopVolumeMonitor();
  }, []);

  const startVolumeMonitor = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioContextRef.current = new AudioContext();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      analyserRef.current.fftSize = 256;

      const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
      
      const updateVolume = () => {
        if (analyserRef.current && isListening) {
          analyserRef.current.getByteFrequencyData(dataArray);
          const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
          setVolume(average / 255);
          requestAnimationFrame(updateVolume);
        }
      };
      updateVolume();
    } catch (err) {
      console.error('Error starting volume monitor:', err);
    }
  };

  const stopVolumeMonitor = () => {
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    setVolume(0);
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  return (
    <div className="voice-input-container">
      <button
        className={`voice-button ${isListening ? 'listening' : ''} ${disabled ? 'disabled' : ''}`}
        onClick={toggleListening}
        disabled={disabled}
        title={isListening ? 'לחץ להפסקה' : 'לחץ לדיבור'}
      >
        <div className="voice-icon">
          {isListening ? (
            <svg viewBox="0 0 24 24" fill="currentColor">
              <rect x="6" y="6" width="12" height="12" rx="2" />
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
              <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
            </svg>
          )}
        </div>
        
        {isListening && (
          <div className="volume-indicator">
            <div 
              className="volume-bar" 
              style={{ transform: `scaleY(${0.3 + volume * 0.7})` }}
            />
            <div 
              className="volume-bar" 
              style={{ transform: `scaleY(${0.3 + volume * 0.7})`, animationDelay: '0.1s' }}
            />
            <div 
              className="volume-bar" 
              style={{ transform: `scaleY(${0.3 + volume * 0.7})`, animationDelay: '0.2s' }}
            />
          </div>
        )}
      </button>

      {isListening && (
        <div className="listening-status">
          <span className="pulse-dot"></span>
          מאזין...
        </div>
      )}

      {transcript && isListening && (
        <div className="transcript-preview">
          "{transcript}"
        </div>
      )}

      {error && (
        <div className="voice-error">
          {error}
        </div>
      )}
    </div>
  );
};

export default VoiceInput;
