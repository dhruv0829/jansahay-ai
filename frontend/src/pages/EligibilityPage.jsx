import React, { useState, useEffect } from 'react';
import { 
  CheckSquare, 
  Sparkles, 
  Check, 
  X, 
  AlertCircle, 
  HelpCircle, 
  ArrowRight,
  ShieldCheck,
  Cpu,
  UserCheck
} from 'lucide-react';
import { api } from '../services/api';
import { EligibilityBadge } from '../components/EligibilityBadge';
import { useAuth } from '../context/AuthContext';

export const EligibilityPage = () => {
  const { user } = useAuth();
  const [schemes, setSchemes] = useState([]);
  const [selectedSchemeId, setSelectedSchemeId] = useState('');
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);

  // Sandbox parameters
  const [testProfile, setTestProfile] = useState({
    age: 28,
    gender: 'Male',
    state: 'Maharashtra',
    occupation: 'Farmer',
    annual_income: 240000,
    social_category: 'OBC',
    is_rural: true,
    landholding_acres: 3.5,
    is_disabled: false,
    has_bpl_card: false,
    is_student: false
  });

  useEffect(() => {
    const fetchSchemes = async () => {
      try {
        const data = await api.getSchemes();
        setSchemes(data);
        if (data.length > 0) {
          setSelectedSchemeId(data[0].id);
        }
      } catch (e) {
        console.error(e);
      }
    };
    fetchSchemes();
  }, []);

  // When selectedSchemeId is set or changes, evaluate automatically
  useEffect(() => {
    if (selectedSchemeId) {
      handleEvaluate();
    }
  }, [selectedSchemeId]);

  const handleEvaluate = async () => {
    if (!selectedSchemeId) return;
    setLoading(true);
    try {
      const res = await api.checkEligibility(parseInt(selectedSchemeId), testProfile);
      setReport(res);
    } catch (e) {
      console.error("Evaluation error", e);
    } finally {
      setLoading(false);
    }
  };

  const handleResetToRahul = () => {
    setTestProfile({
      age: 28,
      gender: 'Male',
      state: 'Maharashtra',
      occupation: 'Farmer',
      annual_income: 240000,
      social_category: 'OBC',
      is_rural: true,
      landholding_acres: 3.5,
      is_disabled: false,
      has_bpl_card: false,
      is_student: false
    });
  };

  const handleResetToStudent = () => {
    setTestProfile({
      age: 20,
      gender: 'Female',
      state: 'Maharashtra',
      occupation: 'Student',
      annual_income: 150000,
      social_category: 'SC',
      is_rural: true,
      landholding_acres: 0,
      is_disabled: false,
      has_bpl_card: true,
      is_student: true
    });
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div>
        <span className="text-[11px] font-bold text-teal-800 bg-teal-50 border border-teal-200 px-2 py-0.5 rounded uppercase tracking-wider inline-block mb-1">
          Direct Rule Engine Evaluator
        </span>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Eligibility Checker & Rule Sandbox
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
          Test any profile against scheme constraints and inspect the exact matched and failed criteria.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Scheme selector & Sandbox controls (5 cols) */}
        <div className="lg:col-span-5 bg-white p-5 sm:p-6 rounded-2xl border border-slate-200 shadow-sm space-y-5">
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1.5">
              Select Scheme to Test:
            </label>
            <select
              value={selectedSchemeId}
              onChange={(e) => setSelectedSchemeId(e.target.value)}
              className="w-full px-3 py-2 text-xs sm:text-sm rounded-xl border border-slate-200 bg-slate-50 font-semibold text-slate-900 focus:ring-2 focus:ring-teal-700 focus:outline-none"
            >
              {schemes.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.short_name ? `${s.short_name} - ${s.name}` : s.name} ({s.category})
                </option>
              ))}
            </select>
          </div>

          {/* Quick Preset Buttons */}
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 block mb-1.5">
              Preset Demo Personas:
            </span>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={handleResetToRahul}
                className="flex-1 py-1.5 px-2 bg-teal-50 border border-teal-200 text-teal-900 rounded-lg text-xs font-semibold hover:bg-teal-100 transition-colors"
              >
                Farmer (Rahul, 28)
              </button>
              <button
                type="button"
                onClick={handleResetToStudent}
                className="flex-1 py-1.5 px-2 bg-blue-50 border border-blue-200 text-blue-900 rounded-lg text-xs font-semibold hover:bg-blue-100 transition-colors"
              >
                Student (SC, 20)
              </button>
            </div>
          </div>

          <div className="border-t border-slate-100 pt-4 space-y-4">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-900 block">
              Adjust Profile Parameters:
            </span>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-medium text-slate-600 mb-1">Age</label>
                <input
                  type="number"
                  value={testProfile.age}
                  onChange={(e) => setTestProfile({ ...testProfile, age: parseInt(e.target.value) || 18 })}
                  className="w-full px-2.5 py-1.5 text-xs rounded-lg border border-slate-200"
                />
              </div>

              <div>
                <label className="block text-[11px] font-medium text-slate-600 mb-1">State</label>
                <select
                  value={testProfile.state}
                  onChange={(e) => setTestProfile({ ...testProfile, state: e.target.value })}
                  className="w-full px-2.5 py-1.5 text-xs rounded-lg border border-slate-200"
                >
                  <option value="Maharashtra">Maharashtra</option>
                  <option value="Gujarat">Gujarat</option>
                  <option value="Uttar Pradesh">Uttar Pradesh</option>
                  <option value="Karnataka">Karnataka</option>
                  <option value="Tamil Nadu">Tamil Nadu</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-medium text-slate-600 mb-1">Occupation</label>
                <select
                  value={testProfile.occupation}
                  onChange={(e) => setTestProfile({ 
                    ...testProfile, 
                    occupation: e.target.value,
                    is_student: e.target.value === 'Student'
                  })}
                  className="w-full px-2.5 py-1.5 text-xs rounded-lg border border-slate-200"
                >
                  <option value="Farmer">Farmer</option>
                  <option value="Student">Student</option>
                  <option value="Street Vendor">Street Vendor</option>
                  <option value="Artisan">Artisan</option>
                  <option value="Self-Employed">Self-Employed</option>
                  <option value="Senior Citizen">Senior Citizen</option>
                  <option value="Daily Wage">Daily Wage</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-medium text-slate-600 mb-1">Annual Income</label>
                <input
                  type="number"
                  step="20000"
                  value={testProfile.annual_income}
                  onChange={(e) => setTestProfile({ ...testProfile, annual_income: parseFloat(e.target.value) || 0 })}
                  className="w-full px-2.5 py-1.5 text-xs rounded-lg border border-slate-200"
                />
              </div>

              <div>
                <label className="block text-[11px] font-medium text-slate-600 mb-1">Category</label>
                <select
                  value={testProfile.social_category}
                  onChange={(e) => setTestProfile({ ...testProfile, social_category: e.target.value })}
                  className="w-full px-2.5 py-1.5 text-xs rounded-lg border border-slate-200"
                >
                  <option value="General">General</option>
                  <option value="OBC">OBC</option>
                  <option value="SC">SC</option>
                  <option value="ST">ST</option>
                  <option value="EWS">EWS</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-medium text-slate-600 mb-1">Land (Acres)</label>
                <input
                  type="number"
                  step="0.5"
                  value={testProfile.landholding_acres}
                  onChange={(e) => setTestProfile({ ...testProfile, landholding_acres: parseFloat(e.target.value) || 0 })}
                  className="w-full px-2.5 py-1.5 text-xs rounded-lg border border-slate-200"
                />
              </div>
            </div>

            <div className="space-y-2 pt-2">
              <label className="flex items-center gap-2 text-xs text-slate-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={testProfile.is_rural}
                  onChange={(e) => setTestProfile({ ...testProfile, is_rural: e.target.checked })}
                  className="w-3.5 h-3.5 text-teal-700 rounded"
                />
                <span>Rural Household Resident</span>
              </label>

              <label className="flex items-center gap-2 text-xs text-slate-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={testProfile.has_bpl_card}
                  onChange={(e) => setTestProfile({ ...testProfile, has_bpl_card: e.target.checked })}
                  className="w-3.5 h-3.5 text-teal-700 rounded"
                />
                <span>BPL / Priority Ration Card Holder</span>
              </label>

              <label className="flex items-center gap-2 text-xs text-slate-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={testProfile.is_disabled}
                  onChange={(e) => setTestProfile({ ...testProfile, is_disabled: e.target.checked })}
                  className="w-3.5 h-3.5 text-teal-700 rounded"
                />
                <span>Person with Disability (Divyangjan)</span>
              </label>
            </div>

            <button
              type="button"
              onClick={handleEvaluate}
              disabled={loading}
              className="w-full py-2.5 px-4 rounded-xl bg-teal-800 hover:bg-teal-900 text-white font-bold text-xs shadow-sm transition-colors flex items-center justify-center gap-1.5"
            >
              <Cpu className="w-4 h-4 text-teal-300" />
              <span>{loading ? 'Evaluating Rules...' : 'Re-Evaluate Eligibility'}</span>
            </button>
          </div>
        </div>

        {/* Right Column: Live Backend Assessment Report (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          {report ? (
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6">
              {/* Header with Status & Score */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
                <div>
                  <span className="text-[11px] uppercase tracking-wider font-bold text-slate-500 block mb-0.5">
                    Evaluated Scheme
                  </span>
                  <h2 className="text-lg sm:text-xl font-bold text-slate-900">
                    {report.scheme_name}
                  </h2>
                </div>

                <div className="flex items-center gap-2">
                  <EligibilityBadge status={report.status} score={report.score} />
                </div>
              </div>

              {/* Summary Reason */}
              <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs">
                <span className="font-bold text-slate-900 block mb-1">
                  Engine Assessment Summary:
                </span>
                <p className="text-slate-700 leading-relaxed font-normal">
                  {report.summary_reason}
                </p>
                {report.action_tip && (
                  <p className="text-teal-900 font-semibold mt-2 text-[11px]">
                    Tip: {report.action_tip}
                  </p>
                )}
              </div>

              {/* Matched Rules List */}
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-800 mb-2 flex items-center gap-1.5">
                  <Check className="w-4 h-4 text-emerald-600" />
                  <span>Matched Rules ({report.matched_rules?.length || 0}):</span>
                </h3>
                {report.matched_rules?.length > 0 ? (
                  <ul className="space-y-1.5">
                    {report.matched_rules.map((m, idx) => (
                      <li key={idx} className="p-2.5 rounded-lg bg-emerald-50/70 border border-emerald-200 text-xs text-emerald-950 flex items-start gap-2">
                        <Check className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                        <span>{m}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-xs text-slate-400 italic">No specific rules matched.</p>
                )}
              </div>

              {/* Failed Rules List (if any) */}
              {report.failed_rules?.length > 0 && (
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-rose-800 mb-2 flex items-center gap-1.5">
                    <X className="w-4 h-4 text-rose-600" />
                    <span>Failed Rules / Ineligibility Grounds ({report.failed_rules.length}):</span>
                  </h3>
                  <ul className="space-y-1.5">
                    {report.failed_rules.map((f, idx) => (
                      <li key={idx} className="p-2.5 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-900 flex items-start gap-2">
                        <X className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
                        <span>{f}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Neutral / Informational Rules */}
              {report.neutral_rules?.length > 0 && (
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-2 flex items-center gap-1.5">
                    <HelpCircle className="w-4 h-4 text-slate-400" />
                    <span>Missing / Profile Informational Notes:</span>
                  </h3>
                  <ul className="space-y-1">
                    {report.neutral_rules.map((n, idx) => (
                      <li key={idx} className="text-xs text-slate-600 flex items-start gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-slate-400 mt-1.5" />
                        <span>{n}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="p-12 text-center bg-white rounded-2xl border border-slate-200">
              <CheckSquare className="w-8 h-8 text-slate-300 mx-auto mb-2" />
              <p className="text-xs text-slate-500">Select a scheme and click "Evaluate" to compute results.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
