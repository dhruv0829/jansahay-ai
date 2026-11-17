import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  Building2, 
  MapPin, 
  ArrowLeft, 
  CheckCircle2, 
  AlertCircle, 
  FileText, 
  ExternalLink, 
  Calendar, 
  Check, 
  Bookmark, 
  BookmarkCheck, 
  Share2, 
  Sparkles,
  Info,
  ShieldCheck,
  Award
} from 'lucide-react';
import { api } from '../services/api';
import { EligibilityBadge } from '../components/EligibilityBadge';
import { useAuth } from '../context/AuthContext';

export const SchemeDetailsPage = () => {
  const { id } = useParams();
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [isTracked, setIsTracked] = useState(false);
  const [trackingNotes, setTrackingNotes] = useState('');
  const [trackingSuccess, setTrackingSuccess] = useState(false);

  useEffect(() => {
    const fetchDetails = async () => {
      setLoading(true);
      try {
        const res = await api.getSchemeDetails(id);
        setData(res);
      } catch (e) {
        console.error("Failed to load scheme details", e);
      } finally {
        setLoading(false);
      }
    };
    fetchDetails();
  }, [id]);

  const handleTrack = async (status = 'Saved') => {
    if (!data?.scheme?.id) return;
    try {
      await api.trackScheme(data.scheme.id, status, trackingNotes || 'Tracked from scheme details page');
      setIsTracked(true);
      setTrackingSuccess(true);
      setTimeout(() => setTrackingSuccess(false), 3000);
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4 space-y-4">
        <div className="h-6 w-32 bg-slate-200 rounded animate-pulse" />
        <div className="h-10 w-3/4 bg-slate-200 rounded animate-pulse" />
        <div className="h-48 bg-slate-100 rounded-xl animate-pulse" />
      </div>
    );
  }

  if (!data?.scheme) {
    return (
      <div className="max-w-xl mx-auto py-16 text-center space-y-3">
        <h2 className="text-lg font-bold text-slate-800">Scheme not found</h2>
        <p className="text-xs text-slate-500">The requested scheme identifier could not be located in our records.</p>
        <Link to="/schemes" className="inline-block px-4 py-2 bg-teal-800 text-white rounded-lg text-xs font-semibold">
          Return to Scheme Catalog
        </Link>
      </div>
    );
  }

  const { scheme: s, personalized_assessment: pa } = data;
  const rule = s.eligibility_rules;

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'benefits', label: `Benefits (${s.benefits?.length || 0})` },
    { id: 'eligibility', label: 'Eligibility Criteria' },
    { id: 'documents', label: `Documents Required (${s.documents?.length || 0})` },
    { id: 'apply', label: 'How to Apply' },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-16">
      {/* Back link */}
      <div>
        <Link
          to="/schemes"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-teal-800 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to All Schemes</span>
        </Link>
      </div>

      {/* Main Scheme Header Card */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider px-2.5 py-0.5 rounded bg-teal-50 text-teal-800 border border-teal-200">
              {s.category}
            </span>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
              {s.level} Government
            </span>
            <span className="text-xs text-slate-500 flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-slate-400" />
              {s.applicable_states === 'All' ? 'Pan-India Applicable' : s.applicable_states}
            </span>
          </div>

          <div className="flex items-center gap-2">
            {s.is_verified && (
              <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-800 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                <span>Verified Portal Record</span>
              </span>
            )}
            <span className="text-[11px] text-slate-400">
              Verified: {s.last_verified_date || 'October 2026'}
            </span>
          </div>
        </div>

        {/* Title */}
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            {s.name}
          </h1>
          {s.short_name && (
            <span className="text-sm font-bold text-teal-800 mt-0.5 block">
              Popularly known as: {s.short_name}
            </span>
          )}
          <p className="text-xs text-slate-500 flex items-center gap-1.5 mt-2">
            <Building2 className="w-3.5 h-3.5 text-slate-400" />
            <span>{s.department} • {s.ministry || 'Government of India'}</span>
          </p>
        </div>

        {/* Key Benefit Banner */}
        <div className="p-4 bg-teal-50/70 border border-teal-200 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <span className="text-[11px] uppercase tracking-wider font-bold text-teal-900 block mb-0.5">
              Financial Assistance / Direct Benefit:
            </span>
            <span className="text-base sm:text-lg font-extrabold text-teal-950">
              {s.benefit_amount}
            </span>
            <span className="text-xs text-teal-900/80 block mt-0.5">
              Type: {s.benefit_type} • Mode: {s.application_mode}
            </span>
          </div>

          <div className="flex items-center gap-2">
            {s.official_url && (
              <a
                href={s.official_url}
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2.5 rounded-lg bg-teal-800 hover:bg-teal-900 text-white font-semibold text-xs shadow-sm transition-colors flex items-center gap-1.5"
              >
                <span>Visit Official Portal</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            )}
          </div>
        </div>

        {/* "Why You Were Recommended" Box (If logged in with profile) */}
        {pa && (
          <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/60 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-emerald-950 flex items-center gap-1.5">
                <Sparkles className="w-4 h-4 text-emerald-700" />
                <span>Why you were recommended for this scheme</span>
              </span>
              <EligibilityBadge status={pa.status} score={pa.match_score} size="sm" />
            </div>

            <p className="text-xs text-emerald-900 leading-relaxed font-medium">
              {pa.summary_reason}
            </p>

            <div className="pt-1">
              <span className="text-[11px] uppercase tracking-wider font-bold text-emerald-900 block mb-1">
                Matched Profile Criteria:
              </span>
              <ul className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                {pa.matched_rules.map((ruleText, idx) => (
                  <li key={idx} className="flex items-start gap-1.5 text-xs text-emerald-950">
                    <Check className="w-3.5 h-3.5 text-emerald-700 flex-shrink-0 mt-0.5" />
                    <span>{ruleText}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Official Disclaimer Banner */}
        <div className="p-3 bg-amber-50/80 border border-amber-200 rounded-lg flex items-start gap-2.5 text-xs text-amber-900">
          <Info className="w-4 h-4 text-amber-700 flex-shrink-0 mt-0.5" />
          <span className="text-[11px] leading-relaxed">
            <strong>Important Assessment Disclaimer:</strong> Eligibility shown here is an indicative assessment calculated from current profile data. Final eligibility determination, document approval, and disbursement are strictly governed by the official scheme authority and designated district nodal officers.
          </span>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex items-center gap-1 border-b border-slate-200 overflow-x-auto pb-0.5">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2.5 text-xs font-bold whitespace-nowrap border-b-2 transition-all ${
              activeTab === tab.id
                ? 'border-teal-800 text-teal-800'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab 1: Overview */}
      {activeTab === 'overview' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 space-y-6">
          <div>
            <h3 className="text-base font-bold text-slate-900 mb-2">Scheme Summary</h3>
            <p className="text-xs sm:text-sm text-slate-700 leading-relaxed font-normal">
              {s.summary}
            </p>
          </div>

          <div>
            <h3 className="text-base font-bold text-slate-900 mb-2">Detailed Description</h3>
            <p className="text-xs sm:text-sm text-slate-700 leading-relaxed whitespace-pre-line font-normal">
              {s.description}
            </p>
          </div>

          {s.target_beneficiary && (
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-xs font-bold text-slate-900 block mb-1">
                Target Beneficiary Demographic
              </span>
              <p className="text-xs text-slate-600">
                {s.target_beneficiary}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Benefits */}
      {activeTab === 'benefits' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 space-y-4">
          <h3 className="text-base font-bold text-slate-900 mb-2">Structured Scheme Benefits</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {s.benefits?.map((b) => (
              <div key={b.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-1">
                <span className="text-xs font-bold text-teal-900 block flex items-center gap-1.5">
                  <Award className="w-4 h-4 text-teal-700" />
                  {b.title}
                </span>
                <p className="text-xs text-slate-600 leading-relaxed">
                  {b.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 3: Eligibility Criteria */}
      {activeTab === 'eligibility' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 space-y-6">
          <div>
            <h3 className="text-base font-bold text-slate-900 mb-1">Formal Rule Parameters</h3>
            <p className="text-xs text-slate-500">Every parameter evaluated by JanSahay's automated eligibility engine.</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl">
              <span className="text-slate-500 block text-[11px]">Age Requirement</span>
              <span className="font-bold text-slate-900">
                {rule?.min_age ? `${rule.min_age} years` : 'No minimum'} to {rule?.max_age ? `${rule.max_age} years` : 'No upper limit'}
              </span>
            </div>

            <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl">
              <span className="text-slate-500 block text-[11px]">Eligible Occupations</span>
              <span className="font-bold text-slate-900">
                {rule?.allowed_occupations || 'Open to all occupations'}
              </span>
            </div>

            <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl">
              <span className="text-slate-500 block text-[11px]">Income Limit</span>
              <span className="font-bold text-slate-900">
                {rule?.max_annual_income ? `Up to ₹${rule.max_annual_income.toLocaleString('en-IN')}/year` : 'No income ceiling specified'}
              </span>
            </div>

            <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl">
              <span className="text-slate-500 block text-[11px]">States & UTs Covered</span>
              <span className="font-bold text-slate-900">
                {rule?.allowed_states === 'All' ? 'Pan-India (All 28 States & 8 UTs)' : rule?.allowed_states}
              </span>
            </div>

            <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl">
              <span className="text-slate-500 block text-[11px]">Landholding Criteria</span>
              <span className="font-bold text-slate-900">
                {rule?.requires_landholding ? `Required (≤ ${rule.max_landholding_acres || 5} acres)` : 'Not required'}
              </span>
            </div>

            <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl">
              <span className="text-slate-500 block text-[11px]">Social Categories</span>
              <span className="font-bold text-slate-900">
                {rule?.allowed_categories || 'Open to all categories (General, OBC, SC, ST, EWS)'}
              </span>
            </div>
          </div>

          {rule?.custom_criteria_text && (
            <div className="p-4 bg-teal-50 border border-teal-200 rounded-xl text-xs text-teal-950">
              <span className="font-bold block mb-1">Additional Conditions & Exceptions:</span>
              <p className="leading-relaxed">{rule.custom_criteria_text}</p>
            </div>
          )}
        </div>
      )}

      {/* Tab 4: Documents Required */}
      {activeTab === 'documents' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 space-y-4">
          <h3 className="text-base font-bold text-slate-900 mb-2">Checklist of Required Proofs</h3>
          <div className="divide-y divide-slate-100 text-xs">
            {s.documents?.map((doc) => (
              <div key={doc.id} className="py-3 flex items-start justify-between gap-3">
                <div className="flex items-start gap-2.5">
                  <FileText className="w-4 h-4 text-teal-700 flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold text-slate-900 block">{doc.document_name}</span>
                    {doc.notes && (
                      <span className="text-slate-500 text-[11px] block mt-0.5">{doc.notes}</span>
                    )}
                  </div>
                </div>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  doc.is_mandatory ? 'bg-rose-50 text-rose-700 border border-rose-200' : 'bg-slate-100 text-slate-600'
                }`}>
                  {doc.is_mandatory ? 'Mandatory' : 'Optional'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 5: How to Apply */}
      {activeTab === 'apply' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 space-y-6">
          <div>
            <h3 className="text-base font-bold text-slate-900 mb-2">Step-by-Step Application Procedure</h3>
            <p className="text-xs sm:text-sm text-slate-700 leading-relaxed font-normal whitespace-pre-line">
              {s.application_process || "Online submission available via designated national portal or at your local Common Service Center (CSC)."}
            </p>
          </div>

          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
            <span className="text-xs font-bold text-slate-900 block">
              Official Portal Link
            </span>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <span className="text-xs text-slate-600 font-mono break-all">
                {s.official_url}
              </span>
              {s.official_url && (
                <a
                  href={s.official_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3.5 py-1.5 rounded-lg bg-teal-800 text-white font-semibold text-xs inline-flex items-center gap-1.5 self-start"
                >
                  <span>Open Portal</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Application Tracking Box */}
      <div className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="font-bold text-sm text-slate-900 block">Track This Scheme on JanSahay</span>
          <span className="text-xs text-slate-500">Save to your dashboard to monitor submission milestones and required deadlines.</span>
        </div>

        <div className="flex items-center gap-2">
          {trackingSuccess ? (
            <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-200 flex items-center gap-1">
              <Check className="w-4 h-4" />
              <span>Saved to Dashboard</span>
            </span>
          ) : (
            <button
              onClick={() => handleTrack('Saved')}
              className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs transition-colors flex items-center gap-1.5"
            >
              <Bookmark className="w-4 h-4 text-slate-500" />
              <span>Bookmark for Later</span>
            </button>
          )}

          <button
            onClick={() => handleTrack('Applied')}
            className="px-4 py-2 rounded-lg bg-teal-800 hover:bg-teal-900 text-white font-semibold text-xs shadow-sm transition-colors flex items-center gap-1.5"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>Mark as Applied</span>
          </button>
        </div>
      </div>
    </div>
  );
};
