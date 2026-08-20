export default function KPICard({ title, value, subtitle, icon, highlighted = false, href = undefined, onClick = undefined, progress = null }) {
  const cardBase = 'dash-lift rounded-2xl border bg-white dark:bg-slate-800 p-5 sm:p-7 transition-all duration-200';
  const cardShadow = 'shadow-[0_1px_2px_rgba(15,23,42,0.05),0_12px_32px_-12px_rgba(15,23,42,0.18)] dark:shadow-none';
  const cardBorder = highlighted
    ? 'border-blue-200/80 dark:border-blue-900/60 ring-1 ring-blue-100/70 dark:ring-blue-500/20'
    : 'border-gray-200/70 dark:border-slate-700/80';

  const interactiveClasses = (href || onClick)
    ? 'cursor-pointer hover:-translate-y-0.5 hover:border-blue-200 dark:hover:border-blue-800 hover:shadow-[0_4px_16px_rgba(15,23,42,0.08),0_20px_48px_-16px_rgba(15,23,42,0.28)]'
    : '';

  const Wrapper = href ? 'a' : 'div';
  const wrapperProps = href ? { href } : onClick ? { onClick, role: 'button', tabIndex: 0 } : {};

  // Barre de progression optionnelle (0-100) : donne une lecture visuelle
  // immediate du pourcentage principal sans remplacer le chiffre.
  const normalizedProgress = typeof progress === 'number' && Number.isFinite(progress)
    ? Math.max(0, Math.min(100, progress))
    : null;

  return (
    <Wrapper
      {...wrapperProps}
      className={`group relative ${cardBase} ${cardShadow} ${cardBorder} ${interactiveClasses}`}
    >
      {highlighted && (
        <div className="absolute -top-px left-6 right-6 h-0.5 rounded-full bg-gradient-to-r from-blue-600 to-indigo-500" />
      )}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <p className={`text-sm font-semibold ${highlighted ? 'text-blue-600' : 'text-gray-600 dark:text-slate-300'}`}>{title}</p>
          <p className={`mt-2 text-3xl font-bold tracking-tight sm:text-4xl ${highlighted ? 'text-blue-700 dark:text-blue-400' : 'text-gray-900 dark:text-white'}`}>{value}</p>
          {normalizedProgress !== null && (
            <div
              className="mt-2.5 h-1.5 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-slate-700"
              role="progressbar"
              aria-valuenow={Math.round(normalizedProgress)}
              aria-valuemin={0}
              aria-valuemax={100}
            >
              <div
                className="dash-bar-fill h-full rounded-full bg-gradient-to-r from-blue-600 to-indigo-500 transition-all duration-700 ease-out"
                style={{ width: `${normalizedProgress}%` }}
              />
            </div>
          )}
          {subtitle && (
            <p className="mt-1.5 text-sm text-gray-400 dark:text-slate-400">{subtitle}</p>
          )}
        </div>
        {icon && (
          <div className="inline-flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600 ring-1 ring-inset ring-blue-100/80 dark:bg-blue-500/10 dark:text-blue-400 dark:ring-blue-400/20">
            {icon}
          </div>
        )}
      </div>
      {(href || onClick) && (
        <div className="absolute inset-y-0 right-4 flex items-center opacity-0 transition-opacity group-hover:opacity-100">
          <svg className="h-4 w-4 text-gray-400 dark:text-slate-500" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
          </svg>
        </div>
      )}
    </Wrapper>
  );
}
