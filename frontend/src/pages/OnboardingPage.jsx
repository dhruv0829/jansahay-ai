import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  User, 
  MapPin, 
  Briefcase, 
  IndianRupee, 
  HeartHandshake, 
  CheckCircle2, 
  ArrowRight, 
  ArrowLeft,
  Sparkles,
  ShieldCheck
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export const OnboardingPage = () => {
  const navigate = useNavigate();
  const { user, refreshUser } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form State
  const [formData, setFormData] = useState({
    age: 28,
    gender: 'Male',
    education_level: '12th Pass',
    state: 'Maharashtra',
    district: 'Pune',
    is_rural: true,
    occupation: 'Farmer',
    landholding_acres: 3.5,
    annual_income: 240000,
    has_bpl_card: false,
    social_category: 'OBC',
    is_disabled: false,
    minority: false,
    is_student: false
  });

  const steps = [
    { num: 1, label: 'About You', icon: User },
    { num: 2, label: 'Location', icon: MapPin },
    { num: 3, label: 'Work', icon: Briefcase },
    { num: 4, label: 'Income', icon: IndianRupee },
    { num: 5, label: 'Needs', icon: HeartHandshake },
    { num: 6, label: 'Review', icon: CheckCircle2 },
  ];

  const indianStates = [
    'Maharashtra', 'Uttar Pradesh', 'Gujarat', 'Karnataka', 'Tamil Nadu',
    'Rajasthan', 'Madhya Pradesh', 'Bihar', 'West Bengal', 'Punjab',
    'Haryana', 'Telangana', 'Andhra Pradesh', 'Kerala', 'Odisha', 'Assam'
  ];

  const occupations = [
    { id: 'Farmer', label: 'Farmer / Cultivator', desc: 'Owns or works on agricultural land' },
    { id: 'Student', label: 'Student', desc: 'Enrolled in school, college, or university' },
    { id: 'Self-Employed', label: 'Self-Employed / MSME', desc: 'Small business owner, shopkeeper, trader' },
    { id: 'Street Vendor', label: 'Street Vendor / Hawker', desc: 'Urban or rural mobile/static vending' },
    { id: 'Artisan', label: 'Artisan / Traditional Craft', desc: 'Weaver, potter, blacksmith, carpenter' },
    { id: 'Daily Wage', label: 'Daily Wage / Construction', desc: 'Manual labour or unorganized worker' },
    { id: 'Unemployed', label: 'Job Seeker / Unemployed', desc: 'Looking for employment or skill training' },
  ];

  const incomeBrackets = [
    { val: 120000, label: 'Under ₹1.2 Lakh', desc: 'Priority welfare bracket' },
    { val: 240000, label: '₹1.2 Lakh – ₹2.5 Lakh', desc: 'Lower income threshold' },
    { val: 500000, label: '₹2.5 Lakh – ₹5.0 Lakh', desc: 'Middle demographic bracket' },
    { val: 800000, label: '₹5.0 Lakh – ₹8.0 Lakh', desc: 'EWS upper limit' },
    { val: 1200000, label: 'Above ₹8.0 Lakh', desc: 'Standard citizen' },
  ];

  const handleQuickFillRahul = () => {
    setFormData({
      age: 28,
      gender: 'Male',
      education_level: '12th Pass',
      state: 'Maharashtra',
      district: 'Pune',
      is_rural: true,
      occupation: 'Farmer',
      landholding_acres: 3.5,
      annual_income: 240000,
      has_bpl_card: false,
      social_category: 'OBC',
      is_disabled: false,
      minority: false,
      is_student: false
    });
    setCurrentStep(6);
  };

  const handleNext = () => {
    if (currentStep < 6) setCurrentStep(currentStep + 1);
  };

  const handleBack = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      await api.updateProfile(formData);
      await refreshUser();
      navigate('/dashboard');
    } catch (e) {
      console.error("Failed to save profile", e);
      // Even if offline/local, route to dashboard
      navigate('/dashboard');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 sm:px-6">
      {/* Top Banner */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-teal-800 bg-teal-50 px-2.5 py-0.5 rounded border border-teal-200">
            Citizen Profile Setup
          </span>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 mt-1">
            Let's Match Schemes to Your Profile
          </h1>
        </div>

        <button
          onClick={handleQuickFillRahul}
          type="button"
          className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-teal-50 text-teal-800 border border-teal-200 hover:bg-teal-100 transition-colors shadow-sm hidden sm:block"
          title="Fills demo data for Rahul Sharma (Farmer, Maharashtra, 28, ₹2.4L)"
        >
          ⚡ Quick Demo Fill (Rahul Sharma)
        </button>
      </div>

      {/* Stepper Progress Bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 mb-6 shadow-sm">
        <div className="grid grid-cols-6 gap-2">
          {steps.map((s) => {
            const isCompleted = s.num < currentStep;
            const isCurrent = s.num === currentStep;
            return (
              <button
                key={s.num}
                onClick={() => setCurrentStep(s.num)}
                className={`flex flex-col items-center text-center p-1.5 rounded-lg transition-all ${
                  isCurrent
                    ? 'bg-teal-800 text-white font-bold'
                    : isCompleted
                    ? 'text-teal-800 hover:bg-teal-50'
                    : 'text-slate-400'
                }`}
              >
                <span className="text-[10px] tracking-wider block">
                  0{s.num}
                </span>
                <span className="text-xs hidden sm:block truncate w-full">
                  {s.label}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Step Form Card */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8">
        {/* Step 1: About You */}
        {currentStep === 1 && (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Basic Information</h2>
              <p className="text-xs text-slate-500">Tell us your age and gender to check age-bracketed welfare programs.</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Age (Years)
                </label>
                <input
                  type="number"
                  min="1"
                  max="105"
                  value={formData.age}
                  onChange={(e) => setFormData({ ...formData, age: parseInt(e.target.value) || 18 })}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-200 text-sm focus:ring-2 focus:ring-teal-700 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Gender
                </label>
                <select
                  value={formData.gender}
                  onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-200 text-sm focus:ring-2 focus:ring-teal-700 focus:outline-none"
                >
                  <option value="Male">Male</option>
                  <option value="Female">Female (Eligible for specialized women's programs)</option>
                  <option value="Transgender">Transgender</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div className="sm:col-span-2">
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Highest Education Level
                </label>
                <select
                  value={formData.education_level}
                  onChange={(e) => setFormData({ ...formData, education_level: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-200 text-sm focus:ring-2 focus:ring-teal-700 focus:outline-none"
                >
                  <option value="Primary School">Below 10th</option>
                  <option value="10th Pass">10th Standard (Matric)</option>
                  <option value="12th Pass">12th Standard (Higher Secondary)</option>
                  <option value="Graduate">Undergraduate Degree</option>
                  <option value="Post Graduate">Post Graduate / PhD</option>
                  <option value="Vocational / ITI">ITI / Diploma / Vocational</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Location */}
        {currentStep === 2 && (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Your Location</h2>
              <p className="text-xs text-slate-500">State and rural/urban classification filter state-specific and rural development schemes.</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  State of Residence
                </label>
                <select
                  value={formData.state}
                  onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-200 text-sm focus:ring-2 focus:ring-teal-700 focus:outline-none"
                >
                  {indianStates.map((st) => (
                    <option key={st} value={st}>{st}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  District
                </label>
                <input
                  type="text"
                  value={formData.district}
                  onChange={(e) => setFormData({ ...formData, district: e.target.value })}
                  placeholder="e.g. Pune, Nagpur, Nashik"
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-200 text-sm focus:ring-2 focus:ring-teal-700 focus:outline-none"
                />
              </div>

              <div className="sm:col-span-2 pt-2">
                <label className="block text-xs font-semibold text-slate-700 mb-2">
                  Area Classification
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setFormData({ ...formData, is_rural: true })}
                    className={`p-3 rounded-xl border text-left transition-all ${
                      formData.is_rural
                        ? 'border-teal-700 bg-teal-50/60 ring-2 ring-teal-700'
                        : 'border-slate-200 hover:bg-slate-50'
                    }`}
                  >
                    <span className="font-bold text-xs text-slate-900 block">Rural Area</span>
                    <span className="text-[11px] text-slate-500">Village, Gram Panchayat, Farmland</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setFormData({ ...formData, is_rural: false })}
                    className={`p-3 rounded-xl border text-left transition-all ${
                      !formData.is_rural
                        ? 'border-teal-700 bg-teal-50/60 ring-2 ring-teal-700'
                        : 'border-slate-200 hover:bg-slate-50'
                    }`}
                  >
                    <span className="font-bold text-xs text-slate-900 block">Urban / Semi-Urban</span>
                    <span className="text-[11px] text-slate-500">Municipal Corporation, Town, City</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Work */}
        {currentStep === 3 && (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Your Occupation & Livelihood</h2>
              <p className="text-xs text-slate-500">Crucial for unlocking farm subsidies, vendor credit, artisan support, and scholarships.</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {occupations.map((occ) => {
                const isSelected = formData.occupation === occ.id;
                return (
                  <button
                    key={occ.id}
                    type="button"
                    onClick={() => setFormData({ 
                      ...formData, 
                      occupation: occ.id,
                      is_student: occ.id === 'Student'
                    })}
                    className={`p-3 rounded-xl border text-left transition-all ${
                      isSelected
                        ? 'border-teal-700 bg-teal-50/60 ring-2 ring-teal-700'
                        : 'border-slate-200 hover:bg-slate-50'
                    }`}
                  >
                    <span className="font-bold text-xs text-slate-900 block">{occ.label}</span>
                    <span className="text-[11px] text-slate-500">{occ.desc}</span>
                  </button>
                );
              })}
            </div>

            {formData.occupation === 'Farmer' && (
              <div className="p-4 bg-teal-50/60 border border-teal-200 rounded-xl space-y-2">
                <label className="block text-xs font-semibold text-teal-950">
                  Agricultural Landholding (Acres in Applicant's / Family Name)
                </label>
                <input
                  type="number"
                  step="0.5"
                  min="0"
                  max="100"
                  value={formData.landholding_acres}
                  onChange={(e) => setFormData({ ...formData, landholding_acres: parseFloat(e.target.value) || 0 })}
                  className="w-full max-w-xs px-3.5 py-2 rounded-lg border border-slate-200 text-sm focus:ring-2 focus:ring-teal-700 bg-white"
                />
                <span className="text-[11px] text-slate-500 block">
                  Small & Marginal Farmer bracket: ≤ 5 acres (2 hectares)
                </span>
              </div>
            )}
          </div>
        )}

        {/* Step 4: Income */}
        {currentStep === 4 && (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Annual Family Income</h2>
              <p className="text-xs text-slate-500">Government schemes enforce income ceilings (e.g. ₹2.5L for welfare, ₹8L for EWS/scholarships).</p>
            </div>

            <div className="space-y-3">
              {incomeBrackets.map((inc) => {
                const isSelected = formData.annual_income === inc.val;
                return (
                  <button
                    key={inc.val}
                    type="button"
                    onClick={() => setFormData({ ...formData, annual_income: inc.val })}
                    className={`w-full p-3 rounded-xl border text-left transition-all flex items-center justify-between ${
                      isSelected
                        ? 'border-teal-700 bg-teal-50/60 ring-2 ring-teal-700'
                        : 'border-slate-200 hover:bg-slate-50'
                    }`}
                  >
                    <div>
                      <span className="font-bold text-xs text-slate-900 block">{inc.label}</span>
                      <span className="text-[11px] text-slate-500">{inc.desc}</span>
                    </div>
                    {isSelected && (
                      <CheckCircle2 className="w-5 h-5 text-teal-700 flex-shrink-0" />
                    )}
                  </button>
                );
              })}
            </div>

            <div className="pt-2">
              <label className="flex items-center gap-2.5 p-3 rounded-xl border border-slate-200 hover:bg-slate-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.has_bpl_card}
                  onChange={(e) => setFormData({ ...formData, has_bpl_card: e.target.checked })}
                  className="w-4 h-4 text-teal-700 rounded focus:ring-teal-600"
                />
                <div className="text-xs">
                  <span className="font-bold text-slate-900 block">Household holds a Below Poverty Line (BPL) or Antyodaya Ration Card</span>
                  <span className="text-slate-500 text-[11px]">Unlocks housing grants and free healthcare enrollment without additional income certificates.</span>
                </div>
              </label>
            </div>
          </div>
        )}

        {/* Step 5: Needs & Demographics */}
        {currentStep === 5 && (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Social Category & Special Conditions</h2>
              <p className="text-xs text-slate-500">Helps identify targeted reservations, fee reimbursements, and assistive subsidies.</p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-2">
                Social Category
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                {['General', 'OBC', 'SC', 'ST', 'EWS'].map((cat) => (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => setFormData({ ...formData, social_category: cat })}
                    className={`py-2 px-3 rounded-lg border text-center text-xs font-bold transition-all ${
                      formData.social_category === cat
                        ? 'border-teal-700 bg-teal-800 text-white'
                        : 'border-slate-200 text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-3 pt-2">
              <label className="flex items-center gap-2.5 p-3 rounded-xl border border-slate-200 hover:bg-slate-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.is_disabled}
                  onChange={(e) => setFormData({ ...formData, is_disabled: e.target.checked })}
                  className="w-4 h-4 text-teal-700 rounded focus:ring-teal-600"
                />
                <div className="text-xs">
                  <span className="font-bold text-slate-900 block">Person with Disability (Divyangjan / UDID Card)</span>
                  <span className="text-slate-500 text-[11px]">Qualifies for 40%+ benchmark disability aids, assistive equipment & concessional loans.</span>
                </div>
              </label>

              <label className="flex items-center gap-2.5 p-3 rounded-xl border border-slate-200 hover:bg-slate-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.minority}
                  onChange={(e) => setFormData({ ...formData, minority: e.target.checked })}
                  className="w-4 h-4 text-teal-700 rounded focus:ring-teal-600"
                />
                <div className="text-xs">
                  <span className="font-bold text-slate-900 block">Religious / Linguistic Minority Community</span>
                  <span className="text-slate-500 text-[11px]">Muslim, Christian, Sikh, Buddhist, Jain, Parsi.</span>
                </div>
              </label>
            </div>
          </div>
        )}

        {/* Step 6: Review */}
        {currentStep === 6 && (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Review Your Profile</h2>
              <p className="text-xs text-slate-500">Confirm your parameters before our rule engine computes your personalized recommendations.</p>
            </div>

            <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-3 text-xs">
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-y-3 gap-x-4">
                <div>
                  <span className="text-slate-500 block text-[11px]">Age & Gender</span>
                  <span className="font-bold text-slate-900">{formData.age} years • {formData.gender}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[11px]">Location</span>
                  <span className="font-bold text-slate-900">{formData.district}, {formData.state}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[11px]">Area Type</span>
                  <span className="font-bold text-slate-900">{formData.is_rural ? 'Rural' : 'Urban'}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[11px]">Occupation</span>
                  <span className="font-bold text-slate-900">{formData.occupation}</span>
                </div>
                {formData.occupation === 'Farmer' && (
                  <div>
                    <span className="text-slate-500 block text-[11px]">Landholding</span>
                    <span className="font-bold text-slate-900">{formData.landholding_acres} Acres</span>
                  </div>
                )}
                <div>
                  <span className="text-slate-500 block text-[11px]">Annual Income</span>
                  <span className="font-bold text-slate-900">₹{formData.annual_income.toLocaleString('en-IN')}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[11px]">Social Category</span>
                  <span className="font-bold text-slate-900">{formData.social_category}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[11px]">Special Priority</span>
                  <span className="font-bold text-slate-900">
                    {[
                      formData.has_bpl_card ? 'BPL Card' : null,
                      formData.is_disabled ? 'Divyangjan' : null,
                      formData.minority ? 'Minority' : null
                    ].filter(Boolean).join(', ') || 'Standard'}
                  </span>
                </div>
              </div>
            </div>

            <div className="p-3.5 bg-teal-50/70 border border-teal-200 rounded-xl flex items-start gap-2.5 text-xs text-teal-950">
              <Sparkles className="w-4 h-4 text-teal-700 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-bold block">Engine Match Ready</span>
                <span>Submitting will evaluate 20+ national and state schemes against these exact criteria.</span>
              </div>
            </div>
          </div>
        )}

        {/* Bottom Actions */}
        <div className="mt-8 pt-4 border-t border-slate-100 flex items-center justify-between">
          {currentStep > 1 ? (
            <button
              type="button"
              onClick={handleBack}
              className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back</span>
            </button>
          ) : <div />}

          {currentStep < 6 ? (
            <button
              type="button"
              onClick={handleNext}
              className="inline-flex items-center gap-1.5 px-5 py-2.5 text-xs font-semibold text-white bg-teal-800 hover:bg-teal-900 rounded-lg shadow-sm transition-colors"
            >
              <span>Continue</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          ) : (
            <button
              type="button"
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="inline-flex items-center gap-2 px-6 py-2.5 text-xs font-bold text-white bg-teal-800 hover:bg-teal-900 rounded-lg shadow-md transition-colors"
            >
              <Sparkles className="w-4 h-4 text-teal-300" />
              <span>{isSubmitting ? 'Evaluating Rules...' : 'Generate My Recommendations'}</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
