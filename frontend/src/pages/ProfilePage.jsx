import React, { useState, useEffect } from 'react';
import { 
  User, 
  MapPin, 
  Briefcase, 
  IndianRupee, 
  Save, 
  CheckCircle2, 
  Printer, 
  Download,
  AlertCircle,
  ShieldCheck
} from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const ProfilePage = () => {
  const { user, refreshUser } = useAuth();
  const [profile, setProfile] = useState({
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
  const [completeness, setCompleteness] = useState(85);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await api.getProfile();
        setProfile(data);
        if (data.completeness_percentage) {
          setCompleteness(data.completeness_percentage);
        }
      } catch (e) {
        console.warn("Could not load remote profile, using active state", e);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSavedSuccess(false);
    try {
      const updated = await api.updateProfile(profile);
      setProfile(updated);
      setCompleteness(updated.completeness_percentage || 90);
      await refreshUser();
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      console.error("Save profile error", err);
    } finally {
      setSaving(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const indianStates = [
    'Maharashtra', 'Uttar Pradesh', 'Gujarat', 'Karnataka', 'Tamil Nadu',
    'Rajasthan', 'Madhya Pradesh', 'Bihar', 'West Bengal', 'Punjab',
    'Haryana', 'Telangana', 'Andhra Pradesh', 'Kerala'
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <span className="text-[11px] font-bold text-teal-800 bg-teal-50 border border-teal-200 px-2 py-0.5 rounded uppercase tracking-wider inline-block mb-1">
            Citizen Profile Registry
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            User Demographics & Eligibility Criteria
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            Parameters utilized by the JanSahay rule engine to recommend and filter government schemes.
          </p>
        </div>

        <button
          onClick={handlePrint}
          className="px-3.5 py-2 text-xs font-semibold rounded-lg border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 transition-colors flex items-center gap-1.5 self-start"
        >
          <Printer className="w-3.5 h-3.5 text-slate-400" />
          <span>Print / Export Summary</span>
        </button>
      </div>

      {/* Completeness Card */}
      <div className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <span className="font-bold text-sm text-slate-900 block">
            Profile Match Status: {completeness}% Complete
          </span>
          <span className="text-xs text-slate-500">
            Higher completeness enables our recommendation engine to detect secondary benefits, tax deductions, and regional quotas.
          </span>
          <div className="w-full sm:w-80 bg-slate-100 h-2 rounded-full overflow-hidden mt-2">
            <div className="bg-teal-700 h-2 rounded-full transition-all duration-500" style={{ width: `${completeness}%` }} />
          </div>
        </div>

        {savedSuccess && (
          <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 font-semibold flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Profile successfully updated</span>
          </div>
        )}
      </div>

      {/* Profile Form */}
      <form onSubmit={handleSave} className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6">
        <div>
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900 mb-3 flex items-center gap-2">
            <User className="w-4 h-4 text-teal-700" />
            <span>Personal & Demographic Information</span>
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Age</label>
              <input
                type="number"
                value={profile.age || ''}
                onChange={(e) => setProfile({ ...profile, age: parseInt(e.target.value) || 0 })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Gender</label>
              <select
                value={profile.gender || 'Male'}
                onChange={(e) => setProfile({ ...profile, gender: e.target.value })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200"
              >
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Education</label>
              <select
                value={profile.education_level || '12th Pass'}
                onChange={(e) => setProfile({ ...profile, education_level: e.target.value })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200"
              >
                <option value="Below 10th">Below 10th</option>
                <option value="10th Pass">10th Pass</option>
                <option value="12th Pass">12th Pass</option>
                <option value="Graduate">Graduate</option>
                <option value="Post Graduate">Post Graduate</option>
              </select>
            </div>
          </div>
        </div>

        <div className="border-t border-slate-100 pt-5">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900 mb-3 flex items-center gap-2">
            <MapPin className="w-4 h-4 text-teal-700" />
            <span>Geographic Domicile</span>
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">State</label>
              <select
                value={profile.state || 'Maharashtra'}
                onChange={(e) => setProfile({ ...profile, state: e.target.value })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200"
              >
                {indianStates.map((st) => (
                  <option key={st} value={st}>{st}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">District</label>
              <input
                type="text"
                value={profile.district || ''}
                onChange={(e) => setProfile({ ...profile, district: e.target.value })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Area Classification</label>
              <select
                value={profile.is_rural ? 'rural' : 'urban'}
                onChange={(e) => setProfile({ ...profile, is_rural: e.target.value === 'rural' })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200"
              >
                <option value="rural">Rural (Village / Panchayat)</option>
                <option value="urban">Urban (City / Town / ULB)</option>
              </select>
            </div>
          </div>
        </div>

        <div className="border-t border-slate-100 pt-5">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900 mb-3 flex items-center gap-2">
            <Briefcase className="w-4 h-4 text-teal-700" />
            <span>Occupation & Economic Indicators</span>
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Occupation</label>
              <select
                value={profile.occupation || 'Farmer'}
                onChange={(e) => setProfile({ ...profile, occupation: e.target.value })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200"
              >
                <option value="Farmer">Farmer / Cultivator</option>
                <option value="Student">Student</option>
                <option value="Street Vendor">Street Vendor</option>
                <option value="Artisan">Artisan / Weaver</option>
                <option value="Self-Employed">Self-Employed / MSME</option>
                <option value="Daily Wage">Daily Wage / Construction</option>
                <option value="Unemployed">Unemployed / Job Seeker</option>
                <option value="Senior Citizen">Senior Citizen / Retired</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Landholding (Acres)</label>
              <input
                type="number"
                step="0.5"
                value={profile.landholding_acres || 0}
                onChange={(e) => setProfile({ ...profile, landholding_acres: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Annual Income (₹)</label>
              <input
                type="number"
                step="10000"
                value={profile.annual_income || 0}
                onChange={(e) => setProfile({ ...profile, annual_income: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200"
              />
            </div>
          </div>
        </div>

        <div className="border-t border-slate-100 pt-5">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900 mb-3 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-teal-700" />
            <span>Social Category & Welfare Entitlements</span>
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Social Category</label>
              <select
                value={profile.social_category || 'General'}
                onChange={(e) => setProfile({ ...profile, social_category: e.target.value })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200"
              >
                <option value="General">General</option>
                <option value="OBC">OBC</option>
                <option value="SC">SC</option>
                <option value="ST">ST</option>
                <option value="EWS">EWS</option>
              </select>
            </div>

            <div className="space-y-2 pt-4">
              <label className="flex items-center gap-2 text-xs text-slate-700">
                <input
                  type="checkbox"
                  checked={profile.has_bpl_card || false}
                  onChange={(e) => setProfile({ ...profile, has_bpl_card: e.target.checked })}
                  className="w-4 h-4 text-teal-700 rounded"
                />
                <span>Holds BPL / Antyodaya Ration Card</span>
              </label>

              <label className="flex items-center gap-2 text-xs text-slate-700">
                <input
                  type="checkbox"
                  checked={profile.is_disabled || false}
                  onChange={(e) => setProfile({ ...profile, is_disabled: e.target.checked })}
                  className="w-4 h-4 text-teal-700 rounded"
                />
                <span>Person with Disability (Divyangjan)</span>
              </label>
            </div>
          </div>
        </div>

        <div className="pt-4 flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2.5 rounded-xl bg-teal-800 hover:bg-teal-900 text-white font-bold text-xs shadow-sm transition-colors flex items-center gap-1.5"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? 'Updating...' : 'Save Profile Changes'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
