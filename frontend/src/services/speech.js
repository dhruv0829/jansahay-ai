/**
 * Voice-First Multilingual Speech Services (STT and TTS)
 * Supports English (en-IN), Hindi (hi-IN), and Marathi (mr-IN).
 */

const LANG_CODE_MAP = {
  en: 'en-IN',
  hi: 'hi-IN',
  mr: 'mr-IN',
};

export const createSpeechRecognizer = ({ onResult, onError, onEnd, onStart }) => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    return {
      isSupported: false,
      start: () => {
        if (onError) onError('Speech recognition is not supported in this browser. Please use keyboard text input.');
      },
      stop: () => {},
    };
  }

  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = 'en-IN';

  recognition.onstart = () => {
    if (onStart) onStart();
  };

  recognition.onresult = (event) => {
    if (event.results && event.results[0] && event.results[0][0]) {
      const transcript = event.results[0][0].transcript;
      if (onResult) onResult(transcript);
    }
  };

  recognition.onerror = (event) => {
    let friendlyMessage = 'Voice input error occurred. Please try again or type your question.';
    if (event.error === 'not-allowed') {
      friendlyMessage = 'Microphone permission was denied. Please allow microphone access in your browser settings.';
    } else if (event.error === 'no-speech') {
      friendlyMessage = 'No speech was detected. Please click the mic icon and speak clearly.';
    } else if (event.error === 'network') {
      friendlyMessage = 'Network error occurred during speech recognition. Please check your internet connection.';
    }
    if (onError) onError(friendlyMessage);
  };

  recognition.onend = () => {
    if (onEnd) onEnd();
  };

  return {
    isSupported: true,
    start: (appLang = 'en') => {
      const targetCode = LANG_CODE_MAP[appLang] || 'en-IN';
      recognition.lang = targetCode;
      try {
        recognition.start();
      } catch (e) {
        console.warn('Speech recognition notice:', e);
      }
    },
    stop: () => {
      try {
        recognition.stop();
      } catch (e) {}
    },
  };
};

/**
 * Text-to-Speech (TTS) Voice Synthesis
 */
export const speakText = (text, appLang = 'en', onEnd = null) => {
  if (!('speechSynthesis' in window)) {
    console.warn('Speech synthesis not supported in this browser environment.');
    return;
  }

  // Cancel any ongoing speech
  window.speechSynthesis.cancel();

  // Strip markdown formatting before speaking
  const cleanText = text
    .replace(/[*_#`[\]()]/g, ' ')
    .replace(/https?:\/\/\S+/g, '')
    .trim();

  if (!cleanText) return;

  const utterance = new SpeechSynthesisUtterance(cleanText);
  const targetCode = LANG_CODE_MAP[appLang] || 'en-IN';
  utterance.lang = targetCode;
  utterance.rate = 0.95; // slightly slower for high civic clarity
  utterance.pitch = 1.0;

  // Attempt to select an Indian voice if available
  const voices = window.speechSynthesis.getVoices();
  const matchedVoice = voices.find(v => v.lang.startsWith(targetCode.substring(0, 2)));
  if (matchedVoice) {
    utterance.voice = matchedVoice;
  }

  if (onEnd) {
    utterance.onend = onEnd;
    utterance.onerror = () => onEnd();
  }

  window.speechSynthesis.speak(utterance);
};

export const stopSpeaking = () => {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
};
