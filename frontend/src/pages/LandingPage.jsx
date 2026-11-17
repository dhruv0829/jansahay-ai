import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  ShieldCheck, 
  Sparkles, 
  ArrowRight, 
  Search, 
  SlidersHorizontal, 
  FileCheck2, 
  Users, 
  Award, 
  TrendingUp,
  Cpu,
  CheckCircle,
  HelpCircle,
  ChevronRight,
  Sprout,
  GraduationCap,
  HeartPulse,
  Home,
  Briefcase,
  Lock,
  ExternalLink
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../services/api';
import { SchemeCard } from '../components/SchemeCard';

export const LandingPage = () => {
  const { t } = useLanguage();
  const { quickDemoLogin } = useAuth();
  const navigate = useNavigate();
  const [featuredSchemes, setFeaturedSchemes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [schemesData, catsData] = await Promise.all([
          api.getSchemes({ limit: 4 }),
          api.getCategories()
        ]);
        setFeaturedSchemes(schemesData.slice(0, 4));
        setCategories(catsData);
      } catch (e) {
        console.error("Failed to fetch landing data", e);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleDemoStart = async () => {
    await quickDemoLogin('citizen');
    navigate('/dashboard');
  };

  const categoryIcons = {
    'Agriculture': Sprout,
    'Education': GraduationCap,
    'Healthcare': HeartPulse,
    'Housing': Home,
    'Entrepreneurship': Briefcase,
    'Employment': TrendingUp,
    'Social Security': Lock,
  };

  return (
    <div className="space-y-16 sm:space-y-24 pb-16">
      {/* Hero Section */}
      <section className="relative pt-12 sm:pt-20 pb-12 overflow-hidden bg-gradient-to-b from-teal-50/50 via-slate-50 to-slate-50 border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 relative z-10">
          <div className="max-w-3xl mx-auto text-center space-y-6">
            {/* Pill Badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white border border-teal-200 shadow-sm text-xs font-semibold text-teal-800">
              <span className="w-2 h-2 rounded-full bg-teal-600 animate-pulse" />
              <span>{t.hero.badge}</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-3xl sm:text-5xl font-extrabold text-slate-900 tracking-tight leading-[1.15]">
              {t.hero.title}
            </h1>

            {/* Subtitle */}
            <p className="text-base sm:text-lg text-slate-600 leading-relaxed font-normal max-w-2xl mx-auto">
              {t.hero.subtitle}
            </p>

            {/* Call to Actions */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
              <Link
                to="/signup"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-teal-800 hover:bg-teal-900 text-white font-semibold text-sm shadow-md hover:shadow-lg transition-all"
              >
                <Sparkles className="w-4 h-4 text-teal-300" />
                <span>{t.hero.ctaPrimary}</span>
                <ArrowRight className="w-4 h-4" />
              </Link>

              <Link
                to="/schemes"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-white border border-slate-300 hover:border-slate-400 text-slate-700 font-semibold text-sm shadow-sm transition-all"
              >
                <Search className="w-4 h-4 text-slate-400" />
                <span>{t.hero.ctaSecondary}</span>
              </Link>
            </div>

            {/* Presentation Quick-Start Callout */}
            {import.meta.env.DEV && <div className="pt-4">
              <div className="inline-flex items-center gap-3 px-4 py-2 rounded-lg bg-emerald-50/80 border border-emerald-200 text-xs text-emerald-900 font-medium">
                <span className="font-bold">Presentation Demo Mode:</span>
                <span>Experience Rahul Sharma's verified farmer profile</span>
                <button
                  onClick={handleDemoStart}
                  className="font-bold text-teal-800 hover:text-teal-950 underline underline-offset-2 ml-1"
                >
                  Launch Demo Dashboard →
                </button>
              </div>
            </div>}
          </div>

          {/* Visual Architecture Diagram Section */}
          <div className="mt-12 sm:mt-16 max-w-4xl mx-auto bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8">
            <div className="text-center mb-6">
              <span className="text-xs uppercase font-bold tracking-wider text-teal-800 bg-teal-50 px-2.5 py-1 rounded-full border border-teal-200">
                Civic-Tech Engine Workflow
              </span>
              <h2 className="text-base sm:text-lg font-bold text-slate-900 mt-2">
                Transparent Profile to Scheme Matching Pipeline
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
              {/* Step 1 */}
              <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/60 text-left">
                <div className="w-8 h-8 rounded-lg bg-teal-100 text-teal-800 flex items-center justify-center font-bold text-xs mb-3">
                  01
                </div>
                <h3 className="font-bold text-sm text-slate-900 mb-1">User Profile</h3>
                <p className="text-xs text-slate-500 leading-normal">
                  Age, State, Occupation, Income, Category, Landholding & Rural status.
                </p>
                <div className="mt-2.5 flex flex-wrap gap-1">
                  <span className="text-[10px] bg-white border border-slate-200 px-1.5 py-0.5 rounded text-slate-600">Farmer</span>
                  <span className="text-[10px] bg-white border border-slate-200 px-1.5 py-0.5 rounded text-slate-600">Maharashtra</span>
                  <span className="text-[10px] bg-white border border-slate-200 px-1.5 py-0.5 rounded text-slate-600">₹2.4L</span>
                </div>
              </div>

              {/* Step 2 */}
              <div className="p-4 rounded-xl border border-teal-200 bg-teal-50/50 text-left relative">
                <div className="w-8 h-8 rounded-lg bg-teal-700 text-white flex items-center justify-center font-bold text-xs mb-3 shadow-sm">
                  02
                </div>
                <h3 className="font-bold text-sm text-teal-950 mb-1">Eligibility Analysis</h3>
                <p className="text-xs text-teal-900/80 leading-normal">
                  Rule engine evaluates state constraints, income ceiling, age bounds, and trade criteria.
                </p>
                <div className="mt-2.5 flex items-center gap-1.5 text-[10px] font-semibold text-emerald-700">
                  <CheckCircle className="w-3.5 h-3.5" />
                  <span>Rule Engine Verified</span>
                </div>
              </div>

              {/* Step 3 */}
              <div className="p-4 rounded-xl border border-blue-200 bg-blue-50/40 text-left">
                <div className="w-8 h-8 rounded-lg bg-blue-700 text-white flex items-center justify-center font-bold text-xs mb-3 shadow-sm">
                  03
                </div>
                <h3 className="font-bold text-sm text-slate-900 mb-1">Personalized Matches</h3>
                <p className="text-xs text-slate-600 leading-normal">
                  Ranked schemes with match scores, transparent explanations, and official portal links.
                </p>
                <div className="mt-2.5 flex items-center gap-1 text-[10px] font-bold text-blue-700">
                  <Sparkles className="w-3 h-3" />
                  <span>Ranked by Compatibility</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Popular Categories Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-8 gap-4">
          <div>
            <span className="text-xs uppercase font-bold tracking-wider text-teal-800">
              Coverage & Domains
            </span>
            <h2 className="text-2xl font-bold text-slate-900 mt-1">
              Explore Government Scheme Sectors
            </h2>
          </div>
          <Link
            to="/schemes"
            className="text-xs font-semibold text-teal-800 hover:text-teal-900 flex items-center gap-1"
          >
            <span>View All Categories</span>
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
          {categories.slice(0, 6).map((cat) => {
            const Icon = categoryIcons[cat.name] || ShieldCheck;
            return (
              <Link
                key={cat.name}
                to={`/schemes?category=${encodeURIComponent(cat.name)}`}
                className="group p-4 bg-white rounded-xl border border-slate-200 hover:border-teal-300 hover:shadow-md transition-all text-center flex flex-col items-center justify-center"
              >
                <div className="w-10 h-10 rounded-xl bg-teal-50 group-hover:bg-teal-700 text-teal-700 group-hover:text-white flex items-center justify-center mb-3 transition-colors">
                  <Icon className="w-5 h-5" />
                </div>
                <span className="font-semibold text-xs text-slate-900 group-hover:text-teal-900 line-clamp-1">
                  {cat.name}
                </span>
                <span className="text-[11px] text-slate-500 mt-0.5">
                  {cat.count} Schemes
                </span>
              </Link>
            );
          })}
        </div>
      </section>

      {/* Featured Central & State Programs */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-8 gap-4">
          <div>
            <span className="text-xs uppercase font-bold tracking-wider text-teal-800">
              Verified Initiatives
            </span>
            <h2 className="text-2xl font-bold text-slate-900 mt-1">
              Featured Flagship Schemes
            </h2>
          </div>
          <Link
            to="/schemes"
            className="text-xs font-semibold text-teal-800 hover:text-teal-900 flex items-center gap-1"
          >
            <span>Explore full catalog</span>
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {featuredSchemes.map((scheme) => (
            <SchemeCard
              key={scheme.id}
              scheme={scheme}
              compact={true}
              eligibilityStatus="likely_eligible"
            />
          ))}
        </div>
      </section>

      {/* How It Works Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="bg-slate-900 text-white rounded-2xl p-8 sm:p-12 relative overflow-hidden">
          <div className="max-w-2xl mb-10">
            <span className="text-xs uppercase font-bold tracking-wider text-teal-400">
              How It Works
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold text-white mt-1 mb-3">
              {t.howItWorks.title}
            </h2>
            <p className="text-slate-400 text-xs sm:text-sm leading-relaxed">
              {t.howItWorks.subtitle}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="border border-slate-800 rounded-xl p-5 bg-slate-800/40">
              <span className="text-xs font-bold text-teal-400 mb-2 block">Step 01</span>
              <h3 className="font-bold text-base text-white mb-2">{t.howItWorks.step1Title}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{t.howItWorks.step1Desc}</p>
            </div>

            <div className="border border-slate-800 rounded-xl p-5 bg-slate-800/40">
              <span className="text-xs font-bold text-teal-400 mb-2 block">Step 02</span>
              <h3 className="font-bold text-base text-white mb-2">{t.howItWorks.step2Title}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{t.howItWorks.step2Desc}</p>
            </div>

            <div className="border border-slate-800 rounded-xl p-5 bg-slate-800/40">
              <span className="text-xs font-bold text-teal-400 mb-2 block">Step 03</span>
              <h3 className="font-bold text-base text-white mb-2">{t.howItWorks.step3Title}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{t.howItWorks.step3Desc}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Trust & Transparency Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-xl border border-slate-200 bg-white">
            <div className="w-9 h-9 rounded-lg bg-teal-50 text-teal-700 flex items-center justify-center mb-3">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-sm text-slate-900 mb-1.5">Official Source Verifiable</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Every scheme record is mapped directly to authoritative central ministries and state government portals.
            </p>
          </div>

          <div className="p-6 rounded-xl border border-slate-200 bg-white">
            <div className="w-9 h-9 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center mb-3">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-sm text-slate-900 mb-1.5">Transparent Scoring</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              No black-box recommendations. You can see exact mathematical weights across eligibility, location, and income criteria.
            </p>
          </div>

          <div className="p-6 rounded-xl border border-slate-200 bg-white">
            <div className="w-9 h-9 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center mb-3">
              <FileCheck2 className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-sm text-slate-900 mb-1.5">Complete Document Checklist</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Know exactly which papers (Aadhaar, Land 7/12, Income certificate) are required before you begin an application.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};
