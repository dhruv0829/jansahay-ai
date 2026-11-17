import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  SlidersHorizontal, 
  CheckCircle2, 
  AlertCircle, 
  HelpCircle,
  Cpu,
  BarChart2,
  ArrowRight
} from 'lucide-react';
import { api } from '../services/api';
import { SchemeCard } from '../components/SchemeCard';
import { EligibilityBadge } from '../components/EligibilityBadge';
import { useAuth } from '../context/AuthContext';

export const RecommendationsPage = () => {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    const fetchRecs = async () => {
      setLoading(true);
      try {
        const res = await api.getRecommendations();
        setData(res);
      } catch (e) {
        console.error("Failed to load recommendations", e);
      } finally {
        setLoading(false);
      }
    };
    fetchRecs();
  }, []);

  const allRecs = data?.recommendations || [];
  const filtered = allRecs.filter((r) => {
    if (statusFilter === 'likely') return r.eligibility_status === 'likely_eligible';
    if (statusFilter === 'possible') return r.eligibility_status === 'possibly_eligible';
    return true;
  });

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div>
        <span className="text-[11px] font-bold text-teal-800 bg-teal-50 border border-teal-200 px-2 py-0.5 rounded uppercase tracking-wider inline-block mb-1">
          Automated Matching Engine
        </span>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Personalized Scheme Recommendations
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
          Multi-criteria scoring model ranking Indian public welfare schemes for your profile.
        </p>
      </div>

      {/* Transparent Algorithm Weights Banner */}
      <div className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-teal-700" />
            <h3 className="font-bold text-xs uppercase tracking-wider text-slate-800">
              Transparent Algorithm Weighting Model:
            </h3>
          </div>
          <span className="text-[11px] text-slate-500 hidden sm:inline">
            Zero Black-Box Scoring
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-6 gap-2 text-center text-xs">
          <div className="p-2.5 rounded-lg bg-teal-50/70 border border-teal-100">
            <span className="font-bold text-teal-900 text-sm block">40%</span>
            <span className="text-[10px] text-teal-800 uppercase tracking-wider font-semibold">Eligibility Rules</span>
          </div>
          <div className="p-2.5 rounded-lg bg-blue-50/70 border border-blue-100">
            <span className="font-bold text-blue-900 text-sm block">20%</span>
            <span className="text-[10px] text-blue-800 uppercase tracking-wider font-semibold">State / Location</span>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
            <span className="font-bold text-slate-900 text-sm block">15%</span>
            <span className="text-[10px] text-slate-600 uppercase tracking-wider font-semibold">Occupation</span>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
            <span className="font-bold text-slate-900 text-sm block">10%</span>
            <span className="text-[10px] text-slate-600 uppercase tracking-wider font-semibold">Income Relevance</span>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
            <span className="font-bold text-slate-900 text-sm block">10%</span>
            <span className="text-[10px] text-slate-600 uppercase tracking-wider font-semibold">Social Category</span>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
            <span className="font-bold text-slate-900 text-sm block">5%</span>
            <span className="text-[10px] text-slate-600 uppercase tracking-wider font-semibold">Intent & Context</span>
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setStatusFilter('all')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              statusFilter === 'all'
                ? 'bg-teal-800 text-white'
                : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
            }`}
          >
            All Matched ({allRecs.length})
          </button>
          <button
            onClick={() => setStatusFilter('likely')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              statusFilter === 'likely'
                ? 'bg-emerald-800 text-white'
                : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
            }`}
          >
            Likely Eligible ({allRecs.filter(r => r.eligibility_status === 'likely_eligible').length})
          </button>
          <button
            onClick={() => setStatusFilter('possible')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              statusFilter === 'possible'
                ? 'bg-amber-800 text-white'
                : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
            }`}
          >
            Possibly Eligible ({allRecs.filter(r => r.eligibility_status === 'possibly_eligible').length})
          </button>
        </div>
      </div>

      {/* Recommendations Cards Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-64 bg-slate-100 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="p-8 text-center bg-white rounded-xl border border-slate-200">
          <p className="text-xs text-slate-500">No recommendations match the selected filter.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((rec) => (
            <SchemeCard
              key={rec.scheme.id}
              scheme={rec.scheme}
              matchScore={rec.match_score}
              eligibilityStatus={rec.eligibility_status}
              matchReasons={rec.match_reasons}
            />
          ))}
        </div>
      )}
    </div>
  );
};
