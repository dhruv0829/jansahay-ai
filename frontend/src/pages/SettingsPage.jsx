import React, { useState } from 'react';
import { Globe, Eye, Bell, Check, ShieldCheck } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export const SettingsPage = () => {
  const { language, setLanguage, t } = useLanguage();
  const [fontSize, setFontSize] = useState('normal');
  const [highContrast, setHighContrast] = useState(false);
  const [notifications, setNotifications] = useState({
    schemeDeadlines: true,
    newMatchingSchemes: true,
    smsAlerts: false
  });
  const [savedAlert, setSavedAlert] = useState(false);

  const handleSave = () => {
    setSavedAlert(true);
    setTimeout(() => setSavedAlert(false), 2500);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 pb-12">
      <div>
        <span className="text-[11px] font-bold text-teal-800 bg-teal-50 border border-teal-200 px-2 py-0.5 rounded uppercase tracking-wider inline-block mb-1">
          Accessibility & Preferences
        </span>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Application Settings
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
          Configure regional language translation, typography size, and notification alerts.
        </p>
      </div>

      {savedAlert && (
        <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 font-semibold flex items-center gap-2">
          <Check className="w-4 h-4 text-emerald-600" />
          <span>Preferences successfully applied.</span>
        </div>
      )}

      {/* Multilingual Selector */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
        <div className="flex items-center gap-2.5">
          <Globe className="w-5 h-5 text-teal-700" />
          <div>
            <h2 className="text-sm font-bold text-slate-900">Interface Language</h2>
            <p className="text-xs text-slate-500">Translate navigation, headers, and scheme statuses.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
          {[
            { code: 'en', label: 'English', desc: 'Default Indian English' },
            { code: 'hi', label: 'हिन्दी (Hindi)', desc: 'राष्ट्रीय भाषा' },
            { code: 'mr', label: 'मराठी (Marathi)', desc: 'महाराष्ट्र राज्य भाषा' },
          ].map((item) => (
            <button
              key={item.code}
              type="button"
              onClick={() => {
                setLanguage(item.code);
                handleSave();
              }}
              className={`p-3.5 rounded-xl border text-left transition-all ${
                language === item.code
                  ? 'border-teal-700 bg-teal-50/70 ring-2 ring-teal-700'
                  : 'border-slate-200 hover:bg-slate-50'
              }`}
            >
              <span className="font-bold text-xs text-slate-900 block">{item.label}</span>
              <span className="text-[11px] text-slate-500">{item.desc}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Accessibility & Visual Comfort */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
        <div className="flex items-center gap-2.5">
          <Eye className="w-5 h-5 text-teal-700" />
          <div>
            <h2 className="text-sm font-bold text-slate-900">Accessibility & Visual Readability</h2>
            <p className="text-xs text-slate-500">Adjust typography contrast and font sizes for easier reading.</p>
          </div>
        </div>

        <div className="space-y-4 pt-1">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-2">Typography Scale</label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 'normal', label: 'Default (100%)' },
                { id: 'large', label: 'Large (115%)' },
                { id: 'xlarge', label: 'Extra Large (130%)' }
              ].map((sz) => (
                <button
                  key={sz.id}
                  type="button"
                  onClick={() => {
                    setFontSize(sz.id);
                    handleSave();
                  }}
                  className={`py-2 px-3 rounded-lg border text-xs font-semibold text-center transition-all ${
                    fontSize === sz.id
                      ? 'border-teal-700 bg-teal-800 text-white'
                      : 'border-slate-200 text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  {sz.label}
                </button>
              ))}
            </div>
          </div>

          <div className="pt-2">
            <label className="flex items-center gap-3 p-3 rounded-xl border border-slate-200 hover:bg-slate-50 cursor-pointer">
              <input
                type="checkbox"
                checked={highContrast}
                onChange={(e) => {
                  setHighContrast(e.target.checked);
                  handleSave();
                }}
                className="w-4 h-4 text-teal-700 rounded"
              />
              <div className="text-xs">
                <span className="font-bold text-slate-900 block">High Contrast Mode</span>
                <span className="text-slate-500 text-[11px]">Enhance borders and text sharpness for low-vision users.</span>
              </div>
            </label>
          </div>
        </div>
      </div>

      {/* Notifications */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
        <div className="flex items-center gap-2.5">
          <Bell className="w-5 h-5 text-teal-700" />
          <div>
            <h2 className="text-sm font-bold text-slate-900">Scheme Alerts & Notifications</h2>
            <p className="text-xs text-slate-500">Stay informed on deadline cutoffs and new government schemes.</p>
          </div>
        </div>

        <div className="space-y-2 pt-1 text-xs">
          <label className="flex items-center gap-3 p-2.5 rounded-lg border border-slate-100 hover:bg-slate-50 cursor-pointer">
            <input
              type="checkbox"
              checked={notifications.schemeDeadlines}
              onChange={(e) => setNotifications({ ...notifications, schemeDeadlines: e.target.checked })}
              className="w-4 h-4 text-teal-700 rounded"
            />
            <span className="font-medium text-slate-800">Application deadline reminders for tracked schemes</span>
          </label>

          <label className="flex items-center gap-3 p-2.5 rounded-lg border border-slate-100 hover:bg-slate-50 cursor-pointer">
            <input
              type="checkbox"
              checked={notifications.newMatchingSchemes}
              onChange={(e) => setNotifications({ ...notifications, newMatchingSchemes: e.target.checked })}
              className="w-4 h-4 text-teal-700 rounded"
            />
            <span className="font-medium text-slate-800">Notify when new schemes match my occupation or state</span>
          </label>
        </div>
      </div>
    </div>
  );
};
