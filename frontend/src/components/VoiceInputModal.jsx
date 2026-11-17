import React, { useState, useEffect } from 'react';
import { Mic, MicOff, X, Volume2, AlertCircle } from 'lucide-react';
import { createSpeechRecognizer } from '../services/speech';
import { useLanguage } from '../context/LanguageContext';

export const VoiceInputModal = ({ isOpen, onClose, onSpeechResult }) => {
  const { language } = useLanguage();
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isOpen) {
      setIsListening(false);
      setTranscript('');
      setError(null);
      return;
    }

    const langCode = language === 'hi' ? 'hi-IN' : language === 'mr' ? 'mr-IN' : 'en-IN';

    const recognizer = createSpeechRecognizer({
      onStart: () => {
        setIsListening(true);
        setError(null);
      },
      onResult: (text) => {
        setTranscript(text);
        setIsListening(false);
        if (onSpeechResult) {
          onSpeechResult(text);
        }
      },
      onError: (err) => {
        setIsListening(false);
        setError(typeof err === 'string' ? err : 'Could not capture audio. Please speak clearly or type.');
      },
      onEnd: () => {
        setIsListening(false);
      }
    });

    if (recognizer.isSupported) {
      recognizer.start(langCode);
    } else {
      setError('Web Speech API is not enabled in this browser. Please type your query in the assistant input.');
    }

    return () => {
      recognizer.stop();
    };
  }, [isOpen, language]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-200 relative text-center">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 p-1 rounded-full hover:bg-slate-100 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="my-6 flex justify-center">
          <div className="relative">
            {isListening && (
              <div className="absolute inset-0 rounded-full bg-teal-400/20 animate-ping" />
            )}
            <div className={`w-20 h-20 rounded-full flex items-center justify-center transition-all duration-300 ${
              isListening ? 'bg-teal-700 text-white shadow-lg ring-8 ring-teal-100' : 'bg-slate-100 text-slate-500'
            }`}>
              {isListening ? (
                <Mic className="w-10 h-10 animate-pulse" />
              ) : (
                <MicOff className="w-8 h-8" />
              )}
            </div>
          </div>
        </div>

        <h3 className="text-lg font-bold text-slate-900 mb-1">
          {isListening ? "Listening to your voice..." : "Voice Input Ready"}
        </h3>
        
        <p className="text-xs text-slate-500 mb-4">
          Speak naturally in {language === 'hi' ? 'Hindi' : language === 'mr' ? 'Marathi' : 'English'}. E.g.: "I am a farmer in Maharashtra. What schemes can I get?"
        </p>

        {transcript && (
          <div className="bg-teal-50 border border-teal-200 rounded-lg p-3 text-sm text-teal-900 font-medium mb-4">
            "{transcript}"
          </div>
        )}

        {error && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-900 flex items-start gap-2 text-left mb-4">
            <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <div className="flex gap-2 justify-center">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
          >
            Cancel / Type Query
          </button>
        </div>
      </div>
    </div>
  );
};
