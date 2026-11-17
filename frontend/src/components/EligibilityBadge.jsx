import React from 'react';
import { CheckCircle2, AlertCircle, XCircle, HelpCircle, Info } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export const EligibilityBadge = ({ status, score = null, size = 'md' }) => {
  const { t } = useLanguage();

  const configs = {
    likely_eligible: {
      label: t.status.likelyEligible || "Likely Eligible",
      icon: CheckCircle2,
      bg: 'bg-emerald-50',
      text: 'text-emerald-800',
      border: 'border-emerald-200',
      indicator: 'bg-emerald-600',
    },
    more_info_required: {
      label: t.status.moreInfoRequired || "More Info Required",
      icon: HelpCircle,
      bg: 'bg-amber-50',
      text: 'text-amber-800',
      border: 'border-amber-200',
      indicator: 'bg-amber-500',
    },
    possibly_eligible: {
      label: t.status.possiblyEligible || "Possibly Eligible",
      icon: AlertCircle,
      bg: 'bg-amber-50',
      text: 'text-amber-800',
      border: 'border-amber-200',
      indicator: 'bg-amber-500',
    },
    conditions_not_met: {
      label: t.status.conditionsNotMet || "Conditions Not Met",
      icon: XCircle,
      bg: 'bg-rose-50',
      text: 'text-rose-700',
      border: 'border-rose-200',
      indicator: 'bg-rose-500',
    },
    not_eligible: {
      label: t.status.notEligible || "Not Eligible",
      icon: XCircle,
      bg: 'bg-slate-100',
      text: 'text-slate-600',
      border: 'border-slate-200',
      indicator: 'bg-slate-400',
    },
    cannot_assess: {
      label: t.status.cannotAssess || "Broad Inclusion",
      icon: Info,
      bg: 'bg-blue-50',
      text: 'text-blue-800',
      border: 'border-blue-200',
      indicator: 'bg-blue-500',
    },
    default: {
      label: 'Criteria Assessment',
      icon: HelpCircle,
      bg: 'bg-slate-50',
      text: 'text-slate-700',
      border: 'border-slate-200',
      indicator: 'bg-slate-500',
    }
  };

  const config = configs[status] || configs.default;
  const Icon = config.icon;

  const sizeClasses = size === 'sm'
    ? 'text-xs px-2.5 py-1 gap-1.5'
    : 'text-xs font-medium px-3 py-1.5 gap-2';

  return (
    <span
      className={`inline-flex items-center rounded-full border ${config.bg} ${config.text} ${config.border} ${sizeClasses}`}
      title={config.label}
    >
      <Icon className={size === 'sm' ? "w-3.5 h-3.5" : "w-4 h-4"} />
      <span>{config.label}</span>
      {score !== null && (
        <span className="font-semibold ml-0.5 border-l border-current pl-1.5 opacity-90">
          {score}%
        </span>
      )}
    </span>
  );
};
