import { propertiesData, customersData, appointmentsData, interactionsData } from './mockData';

// ── Config ────────────────────────────────────────────────────────────────────
const BACKEND_URL = "http://localhost:8000";
const DEV_API_KEY = "dev-key-netixsol-2024";

// Simulate network delay for mock responses
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// ── TTS Helper ────────────────────────────────────────────────────────────────
export const ttsService = {
  utterance: null as SpeechSynthesisUtterance | null,
  isSpeaking: false,

  speak(text: string, onStart?: () => void, onEnd?: () => void): void {
    if (!window.speechSynthesis) {
      console.warn("TTS: SpeechSynthesis not supported in this browser.");
      onEnd?.();
      return;
    }
    this.stop();
    const utterance = new SpeechSynthesisUtterance(text);
    this.utterance = utterance;
    const voices = window.speechSynthesis.getVoices();
    const urduVoice   = voices.find(v => v.lang.startsWith("ur") || v.name.toLowerCase().includes("urdu"));
    const pakVoice    = voices.find(v => v.lang === "en-PK" || v.name.toLowerCase().includes("pakistan"));
    const indiaVoice  = voices.find(v => v.lang.startsWith("en-IN") || v.lang.startsWith("en-GB"));
    utterance.voice   = urduVoice || pakVoice || indiaVoice || null;
    utterance.lang    = urduVoice ? "ur-PK" : "en-IN";
    utterance.rate    = 0.9;
    utterance.pitch   = 1.1;
    utterance.volume  = 1.0;
    utterance.onstart = () => { this.isSpeaking = true; onStart?.(); };
    utterance.onend   = () => { this.isSpeaking = false; this.utterance = null; onEnd?.(); };
    utterance.onerror = () => { this.isSpeaking = false; this.utterance = null; onEnd?.(); };
    window.speechSynthesis.speak(utterance);
  },

  stop(): void {
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    this.isSpeaking = false;
    this.utterance = null;
  },
};

// ── Deepgram STT Helper ───────────────────────────────────────────────────────
// Fetches Deepgram connection info from backend, falls back to browser STT.
export const deepgramSTT = {
  apiKey: null as string | null,
  wsUrl: null as string | null,
  provider: 'browser' as 'deepgram' | 'browser',
  loaded: false,

  async init(): Promise<void> {
    if (this.loaded) return;
    try {
      const resp = await fetch(`${BACKEND_URL}/v1/voice/stt/token`, {
        headers: { 'X-API-Key': DEV_API_KEY },
      });
      if (resp.ok) {
        const data = await resp.json();
        this.provider = data.provider;
        this.apiKey   = data.api_key || null;
        this.wsUrl    = data.ws_url  || null;
        console.log(`STT provider: ${this.provider}`);
      }
    } catch (e) {
      console.warn('Could not fetch STT token — using browser fallback', e);
    }
    this.loaded = true;
  },

  isDeepgramAvailable(): boolean {
    return this.provider === 'deepgram' && !!this.apiKey;
  },
};

// ── API Service ───────────────────────────────────────────────────────────────
export const api = {
  // --- Properties ---
  searchProperties: async (query?: string, budgetMax?: number) => {
    await delay(600);
    let results = [...propertiesData];

    if (query) {
      const q = query.toLowerCase();
      results = results.filter(p =>
        p.title.toLowerCase().includes(q) ||
        p.location.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q)
      );
    }

    if (budgetMax) {
      results = results.filter(p => p.price <= budgetMax);
    }

    return results;
  },

  // --- Customers ---
  getCustomers: async () => {
    await delay(500);
    return customersData;
  },

  getCustomerByPhone: async (phone: string) => {
    await delay(400);
    return customersData.find(c => c.phone === phone);
  },

  getCustomerInteractions: async (customerId: string) => {
    await delay(300);
    return interactionsData.filter(i => i.customerId === customerId);
  },

  // --- Appointments ---
  getAppointments: async () => {
    await delay(500);
    return appointmentsData;
  },

  bookAppointment: async (data: any) => {
    await delay(800);
    const newApt = {
      id: `apt_${Date.now()}`,
      ...data,
      status: 'Confirmed'
    };
    appointmentsData.push(newApt);
    return newApt;
  },

  // --- Voice Chat — Real Backend with Mock Fallback ---
  /**
   * Sends a message to Zara (the AI agent).
   * 1. Tries the real backend at localhost:8000 with proper auth header.
   * 2. Falls back to mock response if backend is unavailable.
   */
  chat: async (message: string, sessionId: string) => {
    try {
      const response = await fetch(`${BACKEND_URL}/v1/voice/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": DEV_API_KEY,           // ← Required auth header (was missing before!)
        },
        body: JSON.stringify({
          message,
          session_id: sessionId,
          language: "ur-PK",
        }),
      });

      if (response.ok) {
        return await response.json();
      }

      const errBody = await response.text();
      console.error(`Backend error ${response.status}:`, errBody);
      throw new Error(`Backend error: ${response.status}`);

    } catch (e) {
      // ── Mock fallback for offline/demo mode ──────────────────────────────
      console.warn("Backend unavailable — using mock response", e);
      await delay(1200);

      const msg = message.toLowerCase();
      let reply: string;

      if (msg.includes("assalam") || msg.includes("hello") || msg.includes("hi") || msg.includes("salam")) {
        reply = "Wa Alaikum Assalam! Main Zara hoon, NetixSol Real Estate ki AI assistant. Aaj aap kya dekhna chahte hain — property kharidni hai, kiraye pe leni hai, ya koi investment plan kar rahe hain?";
      } else if (msg.includes("dha") || msg.includes("defence")) {
        reply = "DHA mein bohat ache options hain! Phase 6 aur Phase 8 mein abhi kuch behtareen houses available hain. Aapka budget roughly kitna hai — toh main aapko perfect match dhundh sakti hoon?";
      } else if (msg.includes("bahria") || msg.includes("bahria town")) {
        reply = "Bahria Town mein plots aur houses dono available hain. Lahore mein Bahria Town aur Islamabad mein alag variants hain. Aap kahan chahte hain — Lahore ya Islamabad?";
      } else if (msg.includes("house") || msg.includes("ghar") || msg.includes("property")) {
        reply = "Bilkul, main aapki madad karoon gi! Aapka budget kya hai aur kaunsa area prefer karte hain? Jaise DHA, Bahria Town, Gulberg, ya koi aur?";
      } else if (msg.includes("appointment") || msg.includes("milna") || msg.includes("meeting")) {
        reply = "Zaroor! Main aapke liye appointment book kar sakti hoon. Aapka phone number aur preferred date aur time batayein please?";
      } else if (msg.includes("price") || msg.includes("qeemat") || msg.includes("rate") || msg.includes("cost")) {
        reply = "Prices area aur property type ke hisab se vary karte hain. Aap kaunse area mein aur kitne marla ka ghar ya plot dekhna chahte hain?";
      } else if (msg.includes("invest") || msg.includes("investment")) {
        reply = "Investment ke liye DHA Phase 6 aur Bahria Town mein plots bohat acchi ROI de rahe hain. Aapka investment budget aur time horizon kya hai?";
      } else if (msg.includes("rent") || msg.includes("kiraya") || msg.includes("lease")) {
        reply = "Rent ke liye bohat options hain! Aapko kitne bedrooms chahiye aur konsa area prefer karoge? Budget bhi batayein please.";
      } else {
        reply = "Ji bilkul, main samajh rahi hoon! Aap real estate ke baare mein poochain — main buying, selling, renting, ya investment — sab mein madad kar sakti hoon. Aap kya chahte hain?";
      }

      return {
        response: reply,
        session_id: sessionId,
        intent: "general",
        confidence: 0.85,
        sentiment: "positive",
        tools_called: [],
        latency_ms: 1200,
        request_id: `mock-${Date.now()}`,
        language: "ur-PK",
      };
    }
  },
};
