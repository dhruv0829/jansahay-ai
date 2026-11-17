import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldCheck, Lock, Mail, ArrowRight, UserCheck, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';

export const LoginPage = () => {
  const { login, quickDemoLogin, isLoading } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Failed to login');
    }
  };

  const handleDemoCitizen = async () => {
    setError(null);
    try {
      await quickDemoLogin('citizen');
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Demo login failed');
    }
  };

  const handleDemoAdmin = async () => {
    setError(null);
    try {
      await quickDemoLogin('admin');
      navigate('/admin');
    } catch (err) {
      setError(err.message || 'Demo admin login failed');
    }
  };

  return (
    <div className="min-h-[calc(100vh-14rem)] flex items-center justify-center p-4 py-12">
      <div className="max-w-md w-full bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="w-10 h-10 rounded-xl bg-teal-800 text-white flex items-center justify-center mx-auto mb-3 shadow-sm">
            <ShieldCheck className="w-6 h-6 text-teal-200" />
          </div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            Sign In to {t.appName}
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Access your personalized schemes, applications, and AI assistant
          </p>
        </div>

        {/* Demo accounts are compiled into development builds only. */}
        {import.meta.env.DEV && <div className="mb-6 p-3.5 bg-teal-50/70 border border-teal-200 rounded-xl space-y-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-teal-900 block">
            Academic Demo One-Click Access:
          </span>
          <div className="grid grid-cols-1 gap-2">
            <button
              type="button"
              onClick={handleDemoCitizen}
              disabled={isLoading}
              className="w-full text-left px-3 py-2 bg-white rounded-lg border border-teal-200 hover:border-teal-400 hover:shadow-sm text-xs transition-all flex items-center justify-between"
            >
              <div>
                <span className="font-bold text-slate-900 block">Rameshwar Patil (Citizen)</span>
                <span className="text-[11px] text-slate-500">Farmer • Nashik, Maharashtra • ₹1.8 Lakh</span>
              </div>
              <span className="text-[10px] font-bold text-teal-800 bg-teal-100 px-2 py-0.5 rounded">
                1-Click Login
              </span>
            </button>

            <button
              type="button"
              onClick={handleDemoAdmin}
              disabled={isLoading}
              className="w-full text-left px-3 py-2 bg-white rounded-lg border border-slate-200 hover:border-slate-300 text-xs transition-all flex items-center justify-between"
            >
              <div>
                <span className="font-bold text-slate-900 block">Portal Administrator</span>
                <span className="text-[11px] text-slate-500">Government Officer • Verification Desk</span>
              </div>
              <span className="text-[10px] font-bold text-slate-700 bg-slate-100 px-2 py-0.5 rounded">
                Admin
              </span>
            </button>
          </div>
        </div>}

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-800 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@example.com"
                className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-700 focus:border-teal-700"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-700 focus:border-teal-700"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2.5 px-4 rounded-lg bg-teal-800 hover:bg-teal-900 text-white font-semibold text-xs shadow transition-colors flex items-center justify-center gap-1.5"
          >
            <span>{isLoading ? 'Signing In...' : 'Sign In'}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </form>

        <div className="mt-6 pt-4 border-t border-slate-100 text-center text-xs text-slate-500">
          <span>New here? </span>
          <Link to="/signup" className="font-semibold text-teal-800 hover:underline">
            Create an account
          </Link>
        </div>
      </div>
    </div>
  );
};
