import React from 'react';
import { ShieldCheck, Phone, Info, ExternalLink, Globe } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export const Footer = () => {
  const { t } = useLanguage();

  return (
    <footer className="bg-slate-900 text-slate-300 border-t border-slate-800 text-xs mt-auto">
      {/* Disclaimer Banner */}
      <div className="bg-slate-950 py-3 px-4 border-b border-slate-800/80">
        <div className="max-w-7xl mx-auto flex items-start sm:items-center gap-2.5 text-slate-400 text-[11px] leading-relaxed">
          <Info className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5 sm:mt-0" />
          <span>
            <strong>Official Notice:</strong> {t.common.disclaimer} All seeded schemes and portals represent genuine Indian Central and State public initiatives.
          </span>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand info */}
          <div className="space-y-3 md:col-span-1">
            <div className="flex items-center gap-2 text-white font-bold text-base">
              <div className="w-6 h-6 rounded bg-teal-600 flex items-center justify-center">
                <ShieldCheck className="w-4 h-4 text-white" />
              </div>
              <span>{t.appName}</span>
            </div>
            <p className="text-slate-400 text-xs leading-relaxed">
              AI-Based Government Scheme Recommendation and Explainable Eligibility Platform for Indian citizens.
            </p>
            <div className="text-[11px] text-teal-400 flex items-center gap-1.5 font-medium">
              <Globe className="w-3.5 h-3.5" />
              <span>Available in English, हिन्दी, and मराठी</span>
            </div>
          </div>

          {/* Quick Portals */}
          <div>
            <h4 className="text-white font-semibold mb-3 text-xs uppercase tracking-wider">
              National Portals
            </h4>
            <ul className="space-y-2 text-slate-400 text-xs">
              <li>
                <a href="https://india.gov.in" target="_blank" rel="noreferrer" className="hover:text-white flex items-center gap-1">
                  <span>National Portal of India</span>
                  <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
              <li>
                <a href="https://pmkisan.gov.in" target="_blank" rel="noreferrer" className="hover:text-white flex items-center gap-1">
                  <span>PM-KISAN Samman Nidhi</span>
                  <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
              <li>
                <a href="https://pmjay.gov.in" target="_blank" rel="noreferrer" className="hover:text-white flex items-center gap-1">
                  <span>Ayushman Bharat PM-JAY</span>
                  <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
              <li>
                <a href="https://scholarships.gov.in" target="_blank" rel="noreferrer" className="hover:text-white flex items-center gap-1">
                  <span>National Scholarship Portal</span>
                  <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
            </ul>
          </div>

          {/* Scheme Categories */}
          <div>
            <h4 className="text-white font-semibold mb-3 text-xs uppercase tracking-wider">
              Popular Categories
            </h4>
            <ul className="space-y-2 text-slate-400 text-xs">
              <li>Agriculture & Farmers Welfare</li>
              <li>Higher Education & Scholarships</li>
              <li>Healthcare & Hospital Coverage</li>
              <li>Rural & Urban Housing (PMAY)</li>
              <li>Micro-Enterprise & Stand-Up India</li>
            </ul>
          </div>

          {/* National Helplines */}
          <div>
            <h4 className="text-white font-semibold mb-3 text-xs uppercase tracking-wider">
              Citizen Helplines
            </h4>
            <div className="space-y-2.5 text-xs text-slate-400">
              <div className="flex items-center gap-2">
                <Phone className="w-3.5 h-3.5 text-teal-400" />
                <span>PM-KISAN Helpline: <strong>155261 / 011-24300606</strong></span>
              </div>
              <div className="flex items-center gap-2">
                <Phone className="w-3.5 h-3.5 text-teal-400" />
                <span>Ayushman Bharat Toll-Free: <strong>14555</strong></span>
              </div>
              <div className="flex items-center gap-2">
                <Phone className="w-3.5 h-3.5 text-teal-400" />
                <span>National Scholarship Helpdesk: <strong>0120-6619540</strong></span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="pt-6 border-t border-slate-800 text-[11px] text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p>© 2026 JanSahay Civic-Tech Platform. Designed for Academic Project Presentation & Public Welfare Demonstration.</p>
          <div className="flex items-center gap-4 text-slate-400">
            <span>Inter Sans</span>
            <span>•</span>
            <span>FastAPI Python Engine</span>
            <span>•</span>
            <span>React & Tailwind CSS</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
