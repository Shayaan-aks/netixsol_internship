import { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Bot, User, Loader2, Mic, MicOff, Volume2, VolumeX } from 'lucide-react';
import { api, ttsService, deepgramSTT } from '../services/api';
import './Chat.css';

// ── Type Declarations for Web Speech API ─────────────────────────────────────
declare global {
  interface Window {
    SpeechRecognition: typeof SpeechRecognition;
    webkitSpeechRecognition: typeof SpeechRecognition;
  }
}

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  intent?: string;
  timestamp: Date;
}

// ── Main Chat Component ───────────────────────────────────────────────────────
export function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Assalam o Alaikum! Main Zara hoon, NetixSol Real Estate ki AI Voice Assistant. Aaj main aapki kya madad kar sakti hoon?',
      isUser: false,
      intent: 'greeting',
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  // Voice state
  const [isRecording, setIsRecording]   = useState(false);
  const [isSpeaking, setIsSpeaking]     = useState(false);
  const [ttsEnabled, setTtsEnabled]     = useState(true);
  const [sttSupported, setSttSupported] = useState(false);
  const [ttsSupported, setTtsSupported] = useState(false);
  const [recordingError, setRecordingError] = useState('');
  const [sttProvider, setSttProvider]   = useState<'deepgram' | 'browser' | 'none'>('none');

  // Refs
  const messagesEndRef  = useRef<HTMLDivElement>(null);
  const recognitionRef  = useRef<SpeechRecognition | null>(null);
  const deepgramWsRef   = useRef<WebSocket | null>(null);
  const mediaStreamRef  = useRef<MediaStream | null>(null);
  const inputRef        = useRef<HTMLInputElement>(null);
  const [sessionId]     = useState(() => "sess_" + Math.random().toString(36).substr(2, 9));

  // ── Initialization ──────────────────────────────────────────────────────────
  useEffect(() => {
    // Check TTS support
    setTtsSupported('speechSynthesis' in window);
    if ('speechSynthesis' in window) {
      window.speechSynthesis.getVoices();
      window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
    }

    // Initialize Deepgram (checks backend for API key), then fall back to browser STT
    const initSTT = async () => {
      await deepgramSTT.init();
      if (deepgramSTT.isDeepgramAvailable()) {
        setSttProvider('deepgram');
        setSttSupported(true);
      } else {
        const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognitionAPI) {
          setSttProvider('browser');
          setSttSupported(true);
        } else {
          setSttProvider('none');
          setSttSupported(false);
        }
      }
    };
    initSTT();

    return () => {
      ttsService.stop();
      recognitionRef.current?.stop();
      deepgramWsRef.current?.close();
      mediaStreamRef.current?.getTracks().forEach(t => t.stop());
    };
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // ── TTS: Speak agent response ───────────────────────────────────────────────
  const speakResponse = useCallback((text: string) => {
    if (!ttsEnabled || !ttsSupported) return;

    // Stop any existing speech
    ttsService.stop();
    setIsSpeaking(true);

    ttsService.speak(
      text,
      () => setIsSpeaking(true),
      () => setIsSpeaking(false),
    );
  }, [ttsEnabled, ttsSupported]);

  // ── Send Message ────────────────────────────────────────────────────────────
  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || loading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      text: text.trim(),
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    // Stop any ongoing TTS when user sends a message
    ttsService.stop();
    setIsSpeaking(false);

    try {
      const response = await api.chat(text.trim(), sessionId);
      const agentMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: response.response,
        isUser: false,
        intent: response.intent,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, agentMsg]);

      // Auto-speak the response if TTS is enabled
      if (ttsEnabled) {
        speakResponse(response.response);
      }

    } catch (error) {
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: "Maafi chahti hoon, main abhi connect nahi ho pa rahi. Thori der mein try karein!",
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  }, [loading, sessionId, ttsEnabled, speakResponse]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    await sendMessage(input);
  };

  // ── STT: Start/Stop Recording (Deepgram + Browser Fallback) ─────────────────
  const toggleRecording = useCallback(() => {
    if (!sttSupported) {
      setRecordingError('Voice input is not supported in your browser. Please use Chrome.');
      setTimeout(() => setRecordingError(''), 3000);
      return;
    }

    if (isRecording) {
      // Stop recording
      recognitionRef.current?.stop();
      deepgramWsRef.current?.close();
      mediaStreamRef.current?.getTracks().forEach(t => t.stop());
      deepgramWsRef.current = null;
      mediaStreamRef.current = null;
      setIsRecording(false);
      return;
    }

    setRecordingError('');
    ttsService.stop();
    setIsSpeaking(false);

    // ── Path A: Deepgram WebSocket STT (Production) ───────────────────────────
    if (sttProvider === 'deepgram' && deepgramSTT.isDeepgramAvailable()) {
      const startDeepgramSTT = async () => {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
          mediaStreamRef.current = stream;

          // Connect to Deepgram WebSocket
          const ws = new WebSocket(deepgramSTT.wsUrl!, ['token', deepgramSTT.apiKey!]);
          deepgramWsRef.current = ws;

          // Use MediaRecorder to capture audio in chunks
          const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

          ws.onopen = () => {
            setIsRecording(true);
            recorder.addEventListener('dataavailable', (e) => {
              if (ws.readyState === WebSocket.OPEN && e.data.size > 0) {
                ws.send(e.data);
              }
            });
            recorder.start(250); // Send 250ms chunks to Deepgram
          };

          ws.onmessage = (event) => {
            try {
              const result = JSON.parse(event.data);
              const transcript = result?.channel?.alternatives?.[0]?.transcript;
              if (transcript) {
                setInput(transcript);
                // Final result — auto-send
                if (result.is_final && transcript.trim()) {
                  setIsRecording(false);
                  recorder.stop();
                  ws.close();
                  stream.getTracks().forEach(t => t.stop());
                  deepgramWsRef.current = null;
                  mediaStreamRef.current = null;
                  setTimeout(() => sendMessage(transcript), 300);
                }
              }
            } catch { /* ignore malformed messages */ }
          };

          ws.onerror = () => {
            setIsRecording(false);
            recorder.stop();
            stream.getTracks().forEach(t => t.stop());
            setRecordingError('Deepgram connection error — dobara try karein');
            setTimeout(() => setRecordingError(''), 3000);
          };

          ws.onclose = () => {
            setIsRecording(false);
            if (recorder.state !== 'inactive') recorder.stop();
          };

        } catch (err: any) {
          setRecordingError(
            err.name === 'NotAllowedError'
              ? 'Microphone permission deny hai — browser settings check karein'
              : 'Microphone access nahi mila'
          );
          setTimeout(() => setRecordingError(''), 4000);
        }
      };
      startDeepgramSTT();
      return;
    }

    // ── Path B: Browser Web Speech API (Fallback) ─────────────────────────────
    const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognitionAPI();
    recognitionRef.current = recognition;
    recognition.lang = 'ur-PK';
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
    recognition.continuous = false;

    recognition.onstart = () => setIsRecording(true);

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const transcript = Array.from(event.results).map(r => r[0].transcript).join('');
      setInput(transcript);
      if (event.results[event.results.length - 1].isFinal) {
        setIsRecording(false);
        recognitionRef.current = null;
        setTimeout(() => sendMessage(transcript), 300);
      }
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      setIsRecording(false);
      recognitionRef.current = null;
      const errorMessages: Record<string, string> = {
        'no-speech':   'Koi awaaz nahi ayi — dobara try karein',
        'audio-capture': 'Microphone access nahi mila',
        'not-allowed': 'Microphone permission deny hai — browser settings check karein',
        'network':     'Network error — internet check karein',
        'aborted':     '',
      };
      const msg = errorMessages[event.error] || `Voice error: ${event.error}`;
      if (msg) { setRecordingError(msg); setTimeout(() => setRecordingError(''), 4000); }
    };

    recognition.onend = () => { setIsRecording(false); recognitionRef.current = null; };
    recognition.start();
  }, [isRecording, sttSupported, sttProvider, sendMessage]);

  // ── Toggle TTS ──────────────────────────────────────────────────────────────
  const toggleTts = () => {
    if (isSpeaking) {
      ttsService.stop();
      setIsSpeaking(false);
    }
    setTtsEnabled(prev => !prev);
  };

  // ── Render ──────────────────────────────────────────────────────────────────
  return (
    <div className="chat-page animate-fade-in">
      <div className="chat-container glass-card">

        {/* Header */}
        <div className="chat-header">
          <div className="agent-profile">
            <div className={`agent-avatar ${isSpeaking ? 'speaking' : ''}`}>
              <Bot size={24} />
              {isSpeaking && (
                <div className="speaking-rings">
                  <div className="ring ring-1" />
                  <div className="ring ring-2" />
                  <div className="ring ring-3" />
                </div>
              )}
            </div>
            <div>
              <h2>Zara AI <span className="agent-badge">Real Estate</span></h2>
              <span className="agent-status">
                {isSpeaking ? '🔊 Bol rahi hoon...' : isRecording ? '🎙️ Sun rahi hoon...' : 'Online'}
              </span>
            </div>
          </div>

          {/* Voice controls in header */}
          <div className="voice-controls-header">
            {ttsSupported && (
              <button
                className={`voice-ctrl-btn ${ttsEnabled ? 'active' : 'muted'}`}
                onClick={toggleTts}
                title={ttsEnabled ? 'TTS On — Click to mute' : 'TTS Off — Click to enable'}
              >
                {ttsEnabled ? <Volume2 size={18} /> : <VolumeX size={18} />}
              </button>
            )}
            <div className="session-chip">Session: {sessionId.slice(-6)}</div>
          </div>
        </div>

        {/* Voice features banner */}
        {(sttSupported || ttsSupported) && (
          <div className="voice-features-banner">
            {sttSupported && (
              <span>
                🎙️ {sttProvider === 'deepgram' ? 'Deepgram Nova-3 STT' : 'Voice Input Ready'}
              </span>
            )}
            {ttsSupported && <span>🔊 Voice Output {ttsEnabled ? 'On' : 'Off'}</span>}
            <span>🌐 Urdulish Mode</span>
          </div>
        )}

        {/* Messages */}
        <div className="chat-messages">
          {messages.map((msg) => (
            <div key={msg.id} className={`message-wrapper ${msg.isUser ? 'user' : 'agent'}`}>
              {!msg.isUser && (
                <div className={`msg-avatar ${isSpeaking && msg.id === messages.filter(m => !m.isUser).slice(-1)[0]?.id ? 'speaking-avatar' : ''}`}>
                  <Bot size={16} />
                </div>
              )}
              <div className="message">
                {msg.text}
                {!msg.isUser && msg.intent && msg.intent !== 'greeting' && (
                  <div className="intent-tag">#{msg.intent}</div>
                )}
              </div>
              {msg.isUser && (
                <div className="msg-avatar user-avatar">
                  <User size={16} />
                </div>
              )}
            </div>
          ))}

          {/* Loading indicator */}
          {loading && (
            <div className="message-wrapper agent typing">
              <div className="msg-avatar"><Bot size={16} /></div>
              <div className="message typing-indicator">
                <span className="dot" /><span className="dot" /><span className="dot" />
                <span className="typing-text">Zara soch rahi hai...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Recording error toast */}
        {recordingError && (
          <div className="error-toast">{recordingError}</div>
        )}

        {/* Input bar */}
        <form className="chat-input" onSubmit={handleSend}>
          {/* Microphone Button (STT) */}
          {sttSupported && (
            <button
              type="button"
              className={`mic-btn ${isRecording ? 'recording' : ''}`}
              onClick={toggleRecording}
              disabled={loading}
              title={isRecording ? 'Click to stop recording' : 'Click to speak (Urdu/English)'}
            >
              {isRecording ? (
                <>
                  <MicOff size={20} />
                  <div className="recording-pulse" />
                </>
              ) : (
                <Mic size={20} />
              )}
            </button>
          )}

          <input
            ref={inputRef}
            type="text"
            placeholder={isRecording ? '🎙️ Sun rahi hoon... (Urdu ya English mein bolen)' : 'Type or speak in Urdu / English...'}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading || isRecording}
          />

          <button
            type="submit"
            className="btn btn-primary send-btn"
            disabled={!input.trim() || loading}
            title="Send message"
          >
            {loading ? <Loader2 size={20} className="spinner" /> : <Send size={20} />}
          </button>
        </form>
      </div>
    </div>
  );
}
