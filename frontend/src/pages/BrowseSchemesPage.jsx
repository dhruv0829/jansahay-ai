import React, { useState, useEffect } from 'react';
import { 
  Search, 
  SlidersHorizontal, 
  RotateCcw, 
  Building2, 
  MapPin, 
  Sparkles,
  Filter
} from 'lucide-react';
import { api } from '../services/api';
import { SchemeCard } from '../components/SchemeCard';

export const BrowseSchemesPage = () => {
  const [schemes, setSchemes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedState, setSelectedState] = useState('');
  const [selectedLevel, setSelectedLevel] = useState('');
  const [sortBy, setSortBy] = useState('popular');
  const [mobileFilterOpen, setMobileFilterOpen] = useState(false);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const cats = await api.getCategories();
        setCategories(cats);
      } catch (e) {
        console.error(e);
      }
    };
    fetchCategories();
  }, []);

  useEffect(() => {
    const fetchSchemes = async () => {
      setLoading(true);
      try {
        const data = await api.getSchemes({
          search: searchTerm,
          category: selectedCategory,
          state: selectedState,
          level: selectedLevel,
          sort: sortBy
        });
        setSchemes(data);
      } catch (e) {
        console.error("Failed to load schemes", e);
      } finally {
        setLoading(false);
      }
    };
    const timer = setTimeout(() => {
      fetchSchemes();
    }, 200);
    return () => clearTimeout(timer);
  }, [searchTerm, selectedCategory, selectedState, selectedLevel, sortBy]);

  const handleReset = () => {
    setSearchTerm('');
    setSelectedCategory('');
    setSelectedState('');
    setSelectedLevel('');
    setSortBy('popular');
  };

  const indianStates = [
    'All', 'Maharashtra', 'Uttar Pradesh', 'Gujarat', 'Karnataka', 
    'Tamil Nadu', 'Rajasthan', 'Madhya Pradesh', 'Bihar', 'West Bengal'
  ];

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div>
        <span className="text-[11px] font-bold text-teal-800 bg-teal-50 border border-teal-200 px-2 py-0.5 rounded uppercase tracking-wider inline-block mb-1">
          Official Government Scheme Catalog
        </span>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Browse All Government Schemes
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
          Explore and filter verified central ministries and state welfare initiatives across India.
        </p>
      </div>

      {/* Search & Top Action Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by scheme name, keyword (e.g. kisan, loan, scholarship, hospital)..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-teal-700 focus:border-teal-700 bg-white shadow-sm"
          />
        </div>

        <div className="flex items-center gap-2">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2.5 rounded-xl border border-slate-200 text-xs font-semibold bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-teal-700"
          >
            <option value="popular">Sort: Default Order</option>
            <option value="az">Sort: Alphabetical (A-Z)</option>
          </select>

          <button
            onClick={() => setMobileFilterOpen(!mobileFilterOpen)}
            className="sm:hidden px-3 py-2.5 rounded-xl border border-slate-200 text-xs font-semibold bg-white text-slate-700 flex items-center gap-1.5"
          >
            <Filter className="w-3.5 h-3.5" />
            <span>Filters</span>
          </button>
        </div>
      </div>

      {/* Main Content Layout with Filter Sidebar */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-6 items-start">
        {/* Filter Sidebar */}
        <div className={`sm:block ${mobileFilterOpen ? 'block' : 'hidden'} sm:col-span-1 bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-5`}>
          <div className="flex items-center justify-between border-b border-slate-100 pb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-900 flex items-center gap-1.5">
              <SlidersHorizontal className="w-3.5 h-3.5 text-teal-700" />
              <span>Filters</span>
            </span>
            <button
              onClick={handleReset}
              className="text-[11px] text-teal-800 hover:text-teal-950 font-semibold flex items-center gap-1"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Reset</span>
            </button>
          </div>

          {/* Category Filter */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-2">
              Category
            </label>
            <div className="space-y-1 max-h-48 overflow-y-auto pr-1">
              <button
                onClick={() => setSelectedCategory('')}
                className={`w-full text-left px-2 py-1.5 rounded text-xs transition-colors ${
                  selectedCategory === ''
                    ? 'bg-teal-800 text-white font-semibold'
                    : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                All Categories
              </button>
              {categories.map((cat) => (
                <button
                  key={cat.name}
                  onClick={() => setSelectedCategory(cat.name)}
                  className={`w-full text-left px-2 py-1.5 rounded text-xs transition-colors flex items-center justify-between ${
                    selectedCategory === cat.name
                      ? 'bg-teal-800 text-white font-semibold'
                      : 'text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <span className="truncate">{cat.name}</span>
                  <span className="text-[10px] opacity-75">{cat.count}</span>
                </button>
              ))}
            </div>
          </div>

          {/* State Jurisdiction Filter */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1.5">
              State Jurisdiction
            </label>
            <select
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value === 'All' ? '' : e.target.value)}
              className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white text-slate-700 focus:ring-1 focus:ring-teal-700"
            >
              <option value="">All States (Pan-India)</option>
              {indianStates.filter(s => s !== 'All').map(st => (
                <option key={st} value={st}>{st}</option>
              ))}
            </select>
          </div>

          {/* Government Level Filter */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1.5">
              Government Tier
            </label>
            <div className="grid grid-cols-3 gap-1">
              {['', 'Central', 'State'].map((lvl) => (
                <button
                  key={lvl || 'all'}
                  onClick={() => setSelectedLevel(lvl)}
                  className={`py-1.5 px-2 rounded text-[11px] font-semibold border transition-all ${
                    selectedLevel === lvl
                      ? 'border-teal-700 bg-teal-50 text-teal-900 font-bold'
                      : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  {lvl || 'All'}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Schemes Grid */}
        <div className="sm:col-span-3 space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>Showing <strong>{schemes.length}</strong> verified government schemes</span>
            {(selectedCategory || selectedState || searchTerm) && (
              <span className="text-teal-800 font-medium">Filtered results</span>
            )}
          </div>

          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[1, 2, 3, 4].map((n) => (
                <div key={n} className="h-64 bg-slate-100 rounded-xl animate-pulse" />
              ))}
            </div>
          ) : schemes.length === 0 ? (
            <div className="bg-white rounded-xl border border-slate-200 p-8 text-center space-y-3">
              <Search className="w-8 h-8 text-slate-300 mx-auto" />
              <h3 className="font-bold text-sm text-slate-800">No matching schemes found</h3>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Try loosening your filters or search for another keyword like "farmer", "scholarship", or "health".
              </p>
              <button
                onClick={handleReset}
                className="px-3 py-1.5 rounded-lg bg-teal-800 text-white text-xs font-semibold"
              >
                Clear Filters
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {schemes.map((s) => (
                <SchemeCard
                  key={s.id}
                  scheme={s}
                  compact={false}
                  eligibilityStatus="possibly_eligible"
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
