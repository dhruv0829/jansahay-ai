import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Building2, 
  MapPin, 
  ArrowRight, 
  Check, 
  Bookmark, 
  BookmarkCheck, 
  ExternalLink,
  ShieldCheck,
  Sparkles
} from 'lucide-react';
import { EligibilityBadge } from './EligibilityBadge';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../services/api';

export const SchemeCard = ({ 
  scheme, 
  matchScore = null, 
  eligibilityStatus = 'possibly_eligible', 
  matchReasons = [], 
  onTrackUpdated = null,
  compact = false 
}) => {
  const { t } = useLanguage();
  const [isTracked, setIsTracked] = useState(false);
  const [isTrackingLoading, setIsTrackingLoading] = useState(false);

  // If scheme wrapper is passed from recommendation endpoint
  const s = scheme.scheme || scheme;
  const score = matchScore !== null ? matchScore : (scheme.match_score || null);
  const status = scheme.eligibility_status || eligibilityStatus;
  const reasons = scheme.match_reasons || matchReasons;

  const handleTrackToggle = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsTrackingLoading(true);
    try {
      await api.trackScheme(s.id, isTracked ? 'Removed' : 'Saved', 'Bookmarked from recommendation card');
      setIsTracked(!isTracked);
      if (onTrackUpdated) onTrackUpdated(s.id, !isTracked);
    } catch (err) {
      console.error("Tracking error", err);
    } finally {
      setIsTrackingLoading(false);
    }
  };

  return (
    <div className="group bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md hover:border-teal-300 transition-all duration-200 flex flex-col justify-between overflow-hidden">
      {/* Top Header */}
      <div className="p-5 pb-4">
        <div className="flex items-start justify-between gap-3 mb-2">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center text-xs font-semibold px-2.5 py-0.5 rounded bg-slate-100 text-slate-700">
              {s.category}
            </span>
            <span className="inline-flex items-center text-xs text-slate-500 gap-1">
              <MapPin className="w-3 h-3 text-slate-400" />
              {s.applicable_states === 'All' ? 'Pan-India' : s.applicable_states}
            </span>
          </div>

          <div className="flex items-center gap-1.5">
            {score !== null && (
              <span className="inline-flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded bg-teal-50 text-teal-800 border border-teal-200">
                <Sparkles className="w-3 h-3 text-teal-600" />
                {score}% Match
              </span>
            )}
            <button
              onClick={handleTrackToggle}
              disabled={isTrackingLoading}
              title={isTracked ? "Application tracked" : "Save scheme for tracking"}
              className="text-slate-400 hover:text-teal-700 p-1 rounded-md hover:bg-slate-50 transition-colors"
            >
              {isTracked ? (
                <BookmarkCheck className="w-4 h-4 text-teal-600 fill-teal-100" />
              ) : (
                <Bookmark className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>

        {/* Scheme Name & Department */}
        <Link to={`/schemes/${s.slug || s.id}`} className="block group-hover:text-teal-800">
          <h3 className="font-semibold text-base text-slate-900 leading-snug tracking-tight mb-1">
            {s.short_name ? (
              <span>
                <strong className="text-teal-900 mr-1.5">{s.short_name}</strong>
                <span className="font-medium text-slate-700 text-sm">({s.name})</span>
              </span>
            ) : (
              s.name
            )}
          </h3>
        </Link>

        <p className="text-xs text-slate-500 flex items-center gap-1.5 mb-3 line-clamp-1">
          <Building2 className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
          <span>{s.department}</span>
        </p>

        {/* Key Benefit Highlight */}
        <div className="mb-3.5 bg-slate-50/80 border border-slate-100 rounded-lg px-3 py-2">
          <span className="text-[11px] uppercase tracking-wider text-slate-600 font-semibold block mb-0.5">
            Key Benefit
          </span>
          <span className="text-xs font-bold text-teal-950">
            {s.benefit_amount}
          </span>
        </div>

        {/* Eligibility Status Badge */}
        <div className="mb-3">
          <EligibilityBadge status={status} />
        </div>

        {/* Transparent Reason Bullets */}
        {reasons && reasons.length > 0 && !compact && (
          <div className="border-t border-slate-100 pt-3">
            <span className="text-[11px] font-semibold text-slate-600 uppercase tracking-wider block mb-1.5">
              Why you match key criteria:
            </span>
            <ul className="space-y-1">
              {reasons.slice(0, 3).map((reason, idx) => (
                <li key={idx} className="flex items-start gap-1.5 text-xs text-slate-700 leading-tight">
                  <Check className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 mt-0.5" />
                  <span>{reason}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Card Footer / Actions */}
      <div className="px-5 py-3 bg-slate-50/60 border-t border-slate-100 flex items-center justify-between gap-3 text-xs">
        <Link
          to={`/schemes/${s.slug || s.id}`}
          className="font-medium text-teal-700 hover:text-teal-900 inline-flex items-center gap-1 group-hover:gap-1.5 transition-all"
        >
          <span>{t.common.viewDetails}</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>

        {s.official_url && (
          <a
            href={s.official_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-slate-500 hover:text-slate-800 inline-flex items-center gap-1 text-[11px]"
            title="Opens external official portal"
          >
            <span>{s.portal_name || 'Portal'}</span>
            <ExternalLink className="w-3 h-3 text-slate-400" />
          </a>
        )}
      </div>
    </div>
  );
};
