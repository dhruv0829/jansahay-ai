import React, { useState, useEffect, useRef } from 'react';
import { 
  Bot, 
  Send, 
  Mic, 
  Sparkles, 
  User, 
  RotateCcw,
  Volume2,
  VolumeX,
  ExternalLink,
  ShieldCheck,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { VoiceInputModal } from '../components/VoiceInputModal';
import { SchemeCard } from '../components/SchemeCard';
import { speakText, stopSpeaking } from '../services/speech';

export const ChatPage = () => {
  const { user } = useAuth();
  const { t, language } = useLanguage();
  const messagesEndRef = useRef(null);

  const [inputMessage, setInputMessage] = useState('');
  const [speakingId, setSpeakingId] = useState(null);
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: `Namaste${user?.full_name ? ` ${user.full_name.split(' ')[0]}` : ''}! I am your **JanSahay Grounded AI Scheme Assistant**.\n\nI am connected directly to **73 verified Central & State Government Welfare Schemes** and over **3,400 official guidelines** in English and Hindi.\n\nYou can ask me natural questions about agricultural subsidies, healthcare coverage, business loans, or ask **"Why am I eligible for this scheme?"** to get a rule audit.`,
      recommended_schemes: [],
      citations: [],
      follow_up_suggestions: [
        "I am a farmer in Maharashtra. What schemes can I get?",
        "Which healthcare schemes provide ₹5 Lakh cashless cover?",
        "How do I apply for PM-KISAN step by step?",
        "What loans are available under MUDRA?"
      ]
    }
  ]);
  const [loading, setLoading] = useState(false);
  const [voiceModalOpen, setVoiceModalOpen] = useState(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  useEffect(() => {
    return () => {
      stopSpeaking();
    };
  }, []);

  const handleSend = async (messageToSend = null) => {
    const text = (messageToSend !== null ? messageToSend : inputMessage).trim();
    if (!text || loading) return;

    stopSpeaking();
    setSpeakingId(null);

    const userMessageId = `user-${Date.now()}`;
    const newMsgList = [
      ...messages,
      { id: userMessageId, role: 'user', content: text }
    ];
    setMessages(newMsgList);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await api.sendMessage(text, 'default-session', language);
      setMessages([
        ...newMsgList,
        {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: response.message,
          recommended_schemes: response.recommended_schemes || [],
          follow_up_suggestions: response.follow_up_suggestions || [],
          citations: response.citations || [],
          grounded_sources: response.grounded_sources || []
        }
      ]);
    } catch (e) {
      console.error("Chat error", e);
      setMessages([
        ...newMsgList,
        {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: e.message || "I couldn't get a response from JanSahay right now. Please try again."
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleSpeak = (msgId, text) => {
    if (speakingId === msgId) {
      stopSpeaking();
      setSpeakingId(null);
    } else {
      setSpeakingId(msgId);
      speakText(text, language, () => {
        setSpeakingId(null);
      });
    }
  };

  const handleSpeechResult = (spokenText) => {
    setVoiceModalOpen(false);
    if (spokenText) {
      handleSend(spokenText);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8.5rem)] max-w-4xl mx-auto bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Assistant Header */}
      <div className="px-6 py-4 border-b border-slate-200 bg-slate-50/70 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-emerald-800 text-white flex items-center justify-center shadow-sm">
            <Bot className="w-5 h-5 text-emerald-200" />
          </div>
          <div>
            <h1 className="text-base font-bold text-slate-900 leading-tight flex items-center gap-2">
              <span>{t.chat.title}</span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 uppercase tracking-wider">
                Grounded RAG Catalog
              </span>
            </h1>
            <p className="text-[11px] text-slate-500">
              {t.chat.subtitle}
            </p>
            <p className="text-[10px] text-slate-500 mt-1 max-w-xl">
              {t.chat.privacyNotice}
            </p>
          </div>
        </div>

        <button
          onClick={() => {
            stopSpeaking();
            setMessages([messages[0]]);
          }}
          title="Reset conversation"
          className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors text-xs flex items-center gap-1 font-medium"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Clear</span>
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-lg bg-emerald-800 text-white flex items-center justify-center flex-shrink-0 mt-0.5">
                <Bot className="w-4 h-4 text-emerald-200" />
              </div>
            )}

            <div
              className={`max-w-[88%] sm:max-w-[80%] rounded-2xl px-4 py-3.5 text-xs sm:text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-emerald-800 text-white rounded-tr-none'
                  : 'bg-slate-50 text-slate-900 border border-slate-200 rounded-tl-none space-y-3'
              }`}
            >
              {/* Formatted Content */}
              <div className="whitespace-pre-line">
                {msg.content}
              </div>

              {/* TTS Voice Readout Button for Assistant */}
              {msg.role === 'assistant' && msg.id !== 'welcome' && (
                <div className="pt-1 flex items-center gap-2">
                  <button
                    onClick={() => handleToggleSpeak(msg.id, msg.content)}
                    className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700 hover:text-emerald-900 bg-white border border-emerald-200 px-2.5 py-1 rounded-full shadow-2xs hover:bg-emerald-50 transition"
                  >
                    {speakingId === msg.id ? (
                      <>
                        <VolumeX className="w-3.5 h-3.5 text-red-600 animate-pulse" />
                        <span>Stop Voice</span>
                      </>
                    ) : (
                      <>
                        <Volume2 className="w-3.5 h-3.5" />
                        <span>Listen to Answer</span>
                      </>
                    )}
                  </button>
                </div>
              )}

              {/* Citations Section */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="pt-2 border-t border-slate-200/80">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-900 block mb-1.5 flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-700" />
                    <span>Official Verified Sources:</span>
                  </span>
                  <div className="space-y-1">
                    {msg.citations.map((c, idx) => (
                      <a
                        key={idx}
                        href={c.official_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center justify-between text-xs p-2 bg-white rounded-lg border border-slate-200 hover:border-emerald-300 transition text-slate-700 hover:text-emerald-900"
                      >
                        <span className="font-semibold">{c.scheme_name}</span>
                        <div className="flex items-center gap-1 text-[11px] text-emerald-700">
                          <span>{c.official_url.replace('https://', '')}</span>
                          <ExternalLink className="w-3 h-3" />
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              )}

              {/* Embedded Scheme Cards (if returned by AI) */}
              {msg.recommended_schemes && msg.recommended_schemes.length > 0 && (
                <div className="pt-2 space-y-2.5">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-900 block">
                    Recommended Welfare Cards:
                  </span>
                  <div className="grid grid-cols-1 gap-2.5">
                    {msg.recommended_schemes.slice(0, 2).map((rec, i) => {
                      const schemeObj = rec.scheme || rec;
                      return (
                        <SchemeCard
                          key={schemeObj.id || i}
                          scheme={schemeObj}
                          recommendation={rec}
                        />
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Follow-up suggestions */}
              {msg.follow_up_suggestions && msg.follow_up_suggestions.length > 0 && (
                <div className="pt-2 border-t border-slate-200/80">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1.5">
                    Suggested Next Inquiries:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {msg.follow_up_suggestions.map((suggestion, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSend(suggestion)}
                        className="text-left text-[11px] px-2.5 py-1 bg-white hover:bg-emerald-50 hover:text-emerald-900 border border-slate-200 rounded-lg text-slate-700 transition-colors shadow-2xs"
                      >
                        {suggestion} →
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-lg bg-slate-800 text-white flex items-center justify-center flex-shrink-0 mt-0.5">
                <User className="w-4 h-4 text-slate-200" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-lg bg-emerald-800 text-white flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 text-emerald-200" />
            </div>
            <div className="bg-slate-50 border border-slate-200 rounded-2xl rounded-tl-none p-3.5 flex items-center gap-2 text-xs text-slate-500">
              <div className="w-2 h-2 rounded-full bg-emerald-600 animate-bounce" />
              <div className="w-2 h-2 rounded-full bg-emerald-600 animate-bounce delay-100" />
              <div className="w-2 h-2 rounded-full bg-emerald-600 animate-bounce delay-200" />
              <span className="ml-1 font-medium">Preparing your answer...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Quick Chips */}
      <div className="px-4 py-2 bg-slate-50/70 border-t border-slate-100 flex items-center gap-1.5 overflow-x-auto scrollbar-none">
        <span className="text-[10px] uppercase font-bold text-slate-500 whitespace-nowrap pl-1">
          Quick Prompts:
        </span>
        {[
          "I am a farmer in Maharashtra. What schemes can I get?",
          "How can I get ₹5 Lakh hospital insurance under Ayushman Bharat?",
          "What loans are available under MUDRA?",
          "What is the eligibility for Atal Pension Yojana?",
          "Which housing schemes can I apply for under PMAY?"
        ].map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(prompt)}
            className="px-2.5 py-1 rounded-full text-[11px] whitespace-nowrap bg-white border border-slate-200 text-slate-700 hover:border-emerald-400 hover:text-emerald-900 transition-colors shadow-2xs font-medium"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Form Bar */}
      <div className="p-3 sm:p-4 bg-white border-t border-slate-200">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          {/* Voice Input Button */}
          <button
            type="button"
            onClick={() => setVoiceModalOpen(true)}
            className="p-2.5 rounded-xl text-slate-600 hover:text-emerald-800 hover:bg-emerald-50 transition-colors border border-slate-200 bg-slate-50"
            title={t.chat.speakPrompt || "Speak your question in English, Hindi, or Marathi"}
          >
            <Mic className="w-4 h-4 text-emerald-700" />
          </button>

          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder={t.chat.placeholder}
            disabled={loading}
            className="flex-1 px-4 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-700 focus:border-emerald-700 bg-white"
          />

          <button
            type="submit"
            disabled={loading || !inputMessage.trim()}
            className="px-4 py-2.5 rounded-xl bg-emerald-800 hover:bg-emerald-900 disabled:opacity-40 text-white font-semibold text-xs transition-colors flex items-center gap-1.5 shadow-sm"
          >
            <span className="hidden sm:inline">Send</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>

      {/* Voice Recognition Modal */}
      <VoiceInputModal
        isOpen={voiceModalOpen}
        onClose={() => setVoiceModalOpen(false)}
        onSpeechResult={handleSpeechResult}
      />
    </div>
  );
};
