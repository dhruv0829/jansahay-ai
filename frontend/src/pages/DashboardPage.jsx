import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Sparkles, 
  CheckCircle2, 
  Clock, 
  FileText, 
  ArrowRight, 
  SlidersHorizontal, 
  Info,
  HelpCircle,
  ExternalLink,
  ChevronRight,
  TrendingUp,
  ShieldCheck,
  UserCheck
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../services/api';
import { SchemeCard } from '../components/SchemeCard';

export const DashboardPage = () => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [trackedSchemes, setTrackedSchemes] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');

  useEffect(() => {
    const loadDashboard = async () => {
      setLoading(true);
      try {
        const [recRes, trackRes] = await Promise.all([
          api.getRecommendations(selectedCategory === 'All' ? '' : selectedCategory),
          api.getTrackedSchemes().catch(() => [])
        ]);
        setDashboardData(recRes);
        setTrackedSchemes(trackRes);
      } catch (e) {
        console.error("Dashboard load failed", e);
      } finally {
        setLoading(false);
      }
    };
    loadDashboard();
  }, [selectedCategory]);

  const userName = user?.full_name || 'Citizen';
  const recommendations = dashboardData?.recommendations || [];
  const stats = dashboardData?.stats || {
    total_recommended: 0,
    likely_eligible: 0,
    possibly_eligible: 0,
    applications_tracked: 0,
    profile_completeness: 85
  };

  const categories = ['All', 'Agriculture', 'Healthcare', 'Housing', 'Education', 'Entrepreneurship', 'Social Security'];

  return (
    <div className="space-y-8 pb-12">
      {/* Top Greeting & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <span className="text-[11px] font-bold text-teal-800 bg-teal-50 border border-teal-200 px-2 py-0.5 rounded uppercase tracking-wider inline-block mb-1">
            Personalized Welfare Dashboard
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            {t.dashboard.greeting}, {userName}
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            {t.dashboard.subtitle}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link
            to="/profile"
            className="px-3 py-2 text-xs font-semibold rounded-lg border border-slate-300 hover:border-slate-400 text-slate-700 bg-white transition-colors"
          >
            {t.dashboard.updateProfile}
          </Link>
          <Link
            to="/chat"
            className="px-3.5 py-2 text-xs font-semibold rounded-lg bg-teal-800 hover:bg-teal-900 text-white shadow-sm transition-colors flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5 text-teal-300" />
            <span>Ask Scheme Assistant</span>
          </Link>
        </div>
      </div>

      {/* Top Stats 4 Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {/* Recommended Schemes */}
        <div className="p-4 sm:p-5 bg-white rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-600">
              {t.dashboard.stats.recommended}
            </span>
            <div className="w-7 h-7 rounded-lg bg-teal-50 text-teal-700 flex items-center justify-center">
              <Sparkles className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-slate-900">
            {stats.total_recommended}
          </div>
          <span className="text-[11px] text-teal-800 font-medium block mt-1">
            Top ranked by relevance
          </span>
        </div>

        {/* Likely Eligible */}
        <div className="p-4 sm:p-5 bg-white rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-600">
              {t.dashboard.stats.likelyEligible}
            </span>
            <div className="w-7 h-7 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-emerald-700">
            {stats.likely_eligible}
          </div>
          <span className="text-[11px] text-slate-500 font-normal block mt-1">
            Direct criteria met
          </span>
        </div>

        {/* Applications Tracked */}
        <div className="p-4 sm:p-5 bg-white rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-600">
              {t.dashboard.stats.tracked}
            </span>
            <div className="w-7 h-7 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-blue-700">
            {stats.applications_tracked || trackedSchemes.length}
          </div>
          <span className="text-[11px] text-slate-500 font-normal block mt-1">
            Saved & in-progress
          </span>
        </div>

        {/* Profile Completeness */}
        <div className="p-4 sm:p-5 bg-white rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-600">
              {t.dashboard.stats.completeness}
            </span>
            <div className="w-7 h-7 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center">
              <UserCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-slate-900">
            {stats.profile_completeness}%
          </div>
          <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden mt-2">
            <div
              className="bg-teal-700 h-1.5 rounded-full"
              style={{ width: `${stats.profile_completeness}%` }}
            />
          </div>
        </div>
      </div>

      {/* "Why these schemes?" Civic Explanation Box */}
      <div className="p-4 sm:p-5 bg-teal-50/70 border border-teal-200/80 rounded-xl">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 rounded-lg bg-teal-800 text-white flex items-center justify-center flex-shrink-0 mt-0.5 shadow-sm">
            <Info className="w-4 h-4 text-teal-200" />
          </div>
          <div className="flex-1">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <h3 className="font-bold text-sm text-teal-950">
                {t.dashboard.whyHeading}
              </h3>
              <Link
                to="/profile"
                className="text-xs font-semibold text-teal-800 hover:text-teal-950 underline underline-offset-2"
              >
                {t.dashboard.updateProfile} →
              </Link>
            </div>
            <p className="text-xs text-teal-900/80 mt-1 leading-relaxed">
              {t.dashboard.whyExplanation} For Rahul Sharma, priority is given to agricultural subsidies in Maharashtra, farmer income support, and micro-credit programs.
            </p>
          </div>
        </div>
      </div>

      {/* Category Pills Filter */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all ${
              selectedCategory === cat
                ? 'bg-teal-800 text-white shadow-sm'
                : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Main Section: "Recommended for You" Cards Grid */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-slate-900">
              {t.dashboard.recommendedHeading}
            </h2>
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-semibold">
              {recommendations.length} matched
            </span>
          </div>

          <Link
            to="/recommendations"
            className="text-xs font-semibold text-teal-800 hover:text-teal-950 flex items-center gap-1"
          >
            <span>{t.dashboard.viewAll}</span>
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-64 bg-slate-100 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : recommendations.length === 0 ? (
          <div className="p-8 text-center bg-white rounded-xl border border-slate-200">
            <p className="text-xs text-slate-500">No schemes found matching this category filter.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recommendations.slice(0, 6).map((rec) => (
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
      </section>

      {/* Tracked Applications Table */}
      {trackedSchemes.length > 0 && (
        <section className="space-y-3 pt-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Clock className="w-4 h-4 text-teal-700" />
              <span>Your Tracked Applications & Bookmarks</span>
            </h2>
            <span className="text-xs text-slate-500">{trackedSchemes.length} saved</span>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="divide-y divide-slate-100 text-xs">
              {trackedSchemes.map((track) => (
                <div key={track.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/50">
                  <div>
                    <span className="font-bold text-slate-900 block">{track.scheme_name}</span>
                    <span className="text-slate-500 text-[11px]">{track.category} • {track.benefit_amount}</span>
                    {track.notes && (
                      <p className="text-slate-600 text-[11px] mt-1 italic">
                        "{track.notes}"
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-teal-50 text-teal-800 border border-teal-200">
                      {track.status}
                    </span>
                    <Link
                      to={`/schemes/${track.scheme_id}`}
                      className="px-2.5 py-1 text-[11px] font-semibold text-slate-700 hover:text-teal-800"
                    >
                      View Details →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}
    </div>
  );
};
