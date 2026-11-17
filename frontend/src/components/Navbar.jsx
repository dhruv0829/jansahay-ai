import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { 
  ShieldCheck, 
  Globe, 
  Menu, 
  X, 
  User as UserIcon, 
  LogOut, 
  LayoutDashboard, 
  Bot, 
  Sparkles,
  ChevronDown,
  UserCheck
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';

export const Navbar = () => {
  const { user, isAuthenticated, logout, quickDemoLogin } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const [isDemoLoading, setIsDemoLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleDemoLogin = async () => {
    setIsDemoLoading(true);
    try {
      await quickDemoLogin('citizen');
      navigate('/dashboard');
    } catch (e) {
      console.error(e);
    } finally {
      setIsDemoLoading(false);
    }
  };

  const navLinks = [
    { name: t.nav.schemes, href: '/schemes' },
    { name: t.nav.eligibility, href: '/eligibility' },
    { name: t.nav.chat, href: '/chat' },
  ];

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200">
      {/* Top Civic Tricolor Accent Line */}
      <div className="h-1 w-full bg-gradient-to-r from-orange-500 via-white via-blue-600 to-emerald-600" />
      
      {/* Official Government of India / Civic Bar */}
      <div className="bg-slate-900 text-slate-300 text-[11px] py-1 px-4 sm:px-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-emerald-400" />
            <span className="font-medium tracking-wide">
              Government of India • Civic Technology Initiative
            </span>
          </div>
          <div className="flex items-center gap-4">
            <span className="hidden sm:inline text-slate-400">
              National Portal Prototype (Presentation Ready)
            </span>
            <div className="flex items-center gap-1.5 text-slate-200">
              <Globe className="w-3 h-3 text-teal-400" />
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="bg-transparent border-0 text-[11px] focus:ring-0 text-slate-200 cursor-pointer font-medium py-0 pr-5"
              >
                <option value="en" className="text-slate-900">English (EN)</option>
                <option value="hi" className="text-slate-900">हिन्दी (Hindi)</option>
                <option value="mr" className="text-slate-900">मराठी (Marathi)</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Main Navbar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <Link to="/" className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-lg bg-teal-800 text-white flex items-center justify-center shadow-sm">
                <ShieldCheck className="w-5 h-5 text-teal-200" />
              </div>
              <div>
                <span className="font-bold text-lg text-slate-900 tracking-tight flex items-center gap-1.5 leading-none">
                  {t.appName}
                  <span className="text-[10px] uppercase font-semibold tracking-wider bg-teal-50 text-teal-800 border border-teal-200 px-1.5 py-0.5 rounded">
                    AI Civic
                  </span>
                </span>
                <span className="text-[11px] text-slate-500 font-normal block leading-tight mt-0.5">
                  {t.tagline}
                </span>
              </div>
            </Link>
          </div>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-6">
            {navLinks.map((item) => (
              <Link
                key={item.href}
                to={item.href}
                className={`text-xs font-semibold tracking-wide transition-colors ${
                  location.pathname === item.href
                    ? 'text-teal-800 border-b-2 border-teal-800 pb-0.5'
                    : 'text-slate-600 hover:text-teal-800'
                }`}
              >
                {item.name}
              </Link>
            ))}

            {isAuthenticated && (
              <Link
                to="/dashboard"
                className={`text-xs font-semibold tracking-wide transition-colors ${
                  location.pathname === '/dashboard'
                    ? 'text-teal-800 border-b-2 border-teal-800 pb-0.5'
                    : 'text-slate-600 hover:text-teal-800'
                }`}
              >
                {t.nav.dashboard}
              </Link>
            )}
          </nav>

          {/* Actions & User */}
          <div className="hidden md:flex items-center gap-3">
            {!isAuthenticated ? (
              <>
                {import.meta.env.DEV && <button
                  onClick={handleDemoLogin}
                  disabled={isDemoLoading}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-teal-50 text-teal-800 border border-teal-200 hover:bg-teal-100 transition-colors shadow-sm"
                  title="Log in immediately as Rahul Sharma (Demo Farmer, Pune)"
                >
                  <UserCheck className="w-3.5 h-3.5 text-teal-600" />
                  <span>Demo Farmer (Rahul)</span>
                </button>}

                <Link
                  to="/login"
                  className="px-3.5 py-2 text-xs font-semibold text-slate-700 hover:text-slate-900 rounded-lg hover:bg-slate-100 transition-colors"
                >
                  {t.nav.login}
                </Link>

                <Link
                  to="/signup"
                  className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-lg bg-teal-800 text-white hover:bg-teal-900 transition-colors shadow-sm"
                >
                  <Sparkles className="w-3.5 h-3.5 text-teal-300" />
                  <span>{t.nav.getStarted}</span>
                </Link>
              </>
            ) : (
              <div className="relative">
                <button
                  onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                  className="flex items-center gap-2 p-1.5 rounded-lg border border-slate-200 hover:border-slate-300 text-left transition-colors"
                >
                  <div className="w-7 h-7 rounded-full bg-teal-100 text-teal-800 flex items-center justify-center font-bold text-xs">
                    {user?.full_name?.charAt(0) || 'U'}
                  </div>
                  <div className="hidden lg:block text-xs">
                    <span className="font-semibold text-slate-900 block leading-tight">
                      {user?.full_name || 'Citizen User'}
                    </span>
                    <span className="text-[10px] text-slate-500 block leading-none">
                      {user?.is_admin ? 'Admin' : 'Verified Citizen'}
                    </span>
                  </div>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                </button>

                {userDropdownOpen && (
                  <div 
                    className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-slate-200 py-1.5 z-50 animate-fade-in"
                    onMouseLeave={() => setUserDropdownOpen(false)}
                  >
                    <Link
                      to="/dashboard"
                      onClick={() => setUserDropdownOpen(false)}
                      className="flex items-center gap-2 px-4 py-2 text-xs text-slate-700 hover:bg-slate-50"
                    >
                      <LayoutDashboard className="w-4 h-4 text-slate-400" />
                      <span>{t.nav.dashboard}</span>
                    </Link>
                    <Link
                      to="/profile"
                      onClick={() => setUserDropdownOpen(false)}
                      className="flex items-center gap-2 px-4 py-2 text-xs text-slate-700 hover:bg-slate-50"
                    >
                      <UserIcon className="w-4 h-4 text-slate-400" />
                      <span>{t.nav.profile}</span>
                    </Link>
                    {user?.is_admin && (
                      <Link
                        to="/admin"
                        onClick={() => setUserDropdownOpen(false)}
                        className="flex items-center gap-2 px-4 py-2 text-xs text-teal-800 font-semibold hover:bg-teal-50"
                      >
                        <ShieldCheck className="w-4 h-4 text-teal-700" />
                        <span>{t.nav.admin}</span>
                      </Link>
                    )}
                    <div className="border-t border-slate-100 my-1" />
                    <button
                      onClick={() => {
                        setUserDropdownOpen(false);
                        logout();
                        navigate('/');
                      }}
                      className="flex items-center gap-2 w-full px-4 py-2 text-xs text-rose-600 hover:bg-rose-50"
                    >
                      <LogOut className="w-4 h-4 text-rose-500" />
                      <span>{t.nav.logout}</span>
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="flex md:hidden items-center gap-2">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 bg-white px-4 pt-3 pb-6 space-y-3">
          <div className="space-y-1">
            {navLinks.map((item) => (
              <Link
                key={item.href}
                to={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className="block px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 rounded-lg"
              >
                {item.name}
              </Link>
            ))}
            {isAuthenticated && (
              <Link
                to="/dashboard"
                onClick={() => setMobileMenuOpen(false)}
                className="block px-3 py-2 text-sm font-semibold text-teal-800 hover:bg-teal-50 rounded-lg"
              >
                {t.nav.dashboard}
              </Link>
            )}
          </div>

          <div className="pt-3 border-t border-slate-100 flex flex-col gap-2">
            {!isAuthenticated ? (
              <>
                {import.meta.env.DEV && <button
                  onClick={() => {
                    setMobileMenuOpen(false);
                    handleDemoLogin();
                  }}
                  className="w-full py-2 text-center text-xs font-semibold rounded-lg bg-teal-50 text-teal-800 border border-teal-200"
                >
                  Quick Demo Login (Rahul Sharma)
                </button>}
                <Link
                  to="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full py-2 text-center text-xs font-semibold text-slate-700 border border-slate-200 rounded-lg"
                >
                  {t.nav.login}
                </Link>
                <Link
                  to="/signup"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full py-2 text-center text-xs font-semibold bg-teal-800 text-white rounded-lg shadow-sm"
                >
                  {t.nav.getStarted}
                </Link>
              </>
            ) : (
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  logout();
                }}
                className="w-full py-2 text-center text-xs font-semibold text-rose-600 bg-rose-50 rounded-lg"
              >
                {t.nav.logout}
              </button>
            )}
          </div>
        </div>
      )}
    </header>
  );
};
