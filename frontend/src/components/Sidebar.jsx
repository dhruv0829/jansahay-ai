import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Sparkles, 
  Search, 
  CheckSquare, 
  Bot, 
  FileText,
  User, 
  Settings, 
  ShieldAlert,
  ArrowUpRight
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';

export const Sidebar = () => {
  const { user } = useAuth();
  const { t } = useLanguage();

  const links = [
    { to: '/dashboard', label: t.nav.dashboard, icon: LayoutDashboard },
    { to: '/recommendations', label: t.nav.recommendations, icon: Sparkles },
    { to: '/schemes', label: t.nav.schemes, icon: Search },
    { to: '/eligibility', label: t.nav.eligibility, icon: CheckSquare },
    { to: '/chat', label: t.nav.chat, icon: Bot, badge: 'AI' },
    { to: '/documents', label: t.nav.documents || 'Document Center', icon: FileText },
    { to: '/profile', label: t.nav.profile, icon: User },
    { to: '/settings', label: t.nav.settings, icon: Settings },
  ];

  if (user?.is_admin) {
    links.push({ to: '/admin', label: t.nav.admin, icon: ShieldAlert, badge: 'Staff' });
  }

  return (
    <aside className="w-64 bg-white border-r border-slate-200 min-h-[calc(100vh-4rem)] flex flex-col justify-between p-4 hidden md:flex">
      <div className="space-y-6">
        {/* User Snapshot Card */}
        {user && (
          <div className="p-3 bg-slate-50 border border-slate-200/80 rounded-xl">
            <div className="flex items-center gap-2.5 mb-2">
              <div className="w-8 h-8 rounded-full bg-emerald-800 text-white font-bold text-xs flex items-center justify-center">
                {user.full_name?.charAt(0) || 'U'}
              </div>
              <div className="overflow-hidden">
                <span className="block text-xs font-bold text-slate-900 truncate">
                  {user.full_name}
                </span>
                <span className="block text-[11px] text-emerald-800 font-medium truncate">
                  {user.profile?.occupation || 'Citizen of India'}
                </span>
              </div>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
              <div className="bg-emerald-700 h-1.5 rounded-full" style={{ width: '85%' }} />
            </div>
            <div className="flex justify-between items-center mt-1 text-[10px] text-slate-500">
              <span>Verified Civic Profile</span>
              <span className="font-semibold text-emerald-800">85%</span>
            </div>
          </div>
        )}

        {/* Navigation Links */}
        <nav className="space-y-1">
          {links.map((link) => {
            const Icon = link.icon;
            return (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-emerald-700 text-white shadow-sm shadow-emerald-700/20'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4" />
                  <span>{link.label}</span>
                </div>
                {link.badge && (
                  <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded-md bg-emerald-100 text-emerald-800">
                    {link.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Official Bottom Seal */}
      <div className="pt-4 border-t border-slate-100 text-[11px] text-slate-400">
        <p className="font-medium text-slate-600">JanSahay AI v1.0</p>
        <p className="mt-0.5">73 Verified Central & State Programs</p>
      </div>
    </aside>
  );
};
