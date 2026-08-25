import { useState, useEffect, useId } from 'react';
import { statsAPI } from '../../services/api';
import KPICard from '../shared/KPICard';
import LoadingSpinner from '../shared/LoadingSpinner';
import ErrorMessage from '../shared/ErrorMessage';
import './adminDashboard.css';

const CHART_COLORS = [
  '#3b82f6', '#06b6d4', '#10b981', '#f59e0b',
  '#8b5cf6', '#ec4899', '#f97316', '#6366f1',
  '#14b8a6', '#84cc16',
];

// Couleur neutre reservee au segment "Non renseigne" : un gris volontairement
// distinct des couleurs vives des vrais secteurs pour bien signaler que ce
// segment ne represente pas une donnee reelle.
const NEUTRAL_COLOR = '#9ca3af';

const KPI_TAG_COLORS = ['amber', 'blue', 'green', 'purple', 'cyan', 'rose'];

const formatKpiValue = (kpi) => {
  if (kpi.nb_repondants <= 0) return '—';
  const value = kpi.valeur ?? kpi.pourcentage;
  if (value == null) return '—';
  if (kpi.unite === '%' || (kpi.unite == null && kpi.pourcentage != null)) {
    return `${value}%`;
  }
  if (typeof kpi.unite === 'string' && kpi.unite.startsWith('/')) {
    return `${value}${kpi.unite}`;
  }
  return `${value}`;
};

const formatKpiSubtitle = (kpi) => {
  if (kpi.nb_repondants <= 0) return 'Aucune donnée disponible';
  const parts = [];
  if (kpi.libelle_valeur) parts.push(kpi.libelle_valeur);
  if (kpi.detail) parts.push(kpi.detail);
  parts.push(
    `${kpi.nb_repondants} répondant${kpi.nb_repondants > 1 ? 's' : ''} concerné${kpi.nb_repondants > 1 ? 's' : ''}`,
  );
  return parts.join(' · ');
};

// Effet de comptage : 0 -> valeur finale (~800ms), pour donner une impression
// de "calcul en direct". Désactivé en mode test (rendu déterministe requis par
// les tests, on affiche directement la valeur finale) et pour les utilisateurs
// préférant réduire les animations.
function AnimatedKpi({ value, duration = 800 }) {
  const shouldSkip = import.meta.env?.MODE === 'test'
    || (typeof window !== 'undefined'
      && typeof window.matchMedia === 'function'
      && window.matchMedia('(prefers-reduced-motion: reduce)').matches);

  const formatInitial = () => {
    if (shouldSkip) return String(value ?? '');
    const m = String(value ?? '').match(/^(-?\d+(?:[.,]\d+)?)(.*)$/);
    return m ? `0${m[2]}` : String(value ?? '');
  };
  const [display, setDisplay] = useState(formatInitial);

  useEffect(() => {
    const target = String(value ?? '');
    const m = target.match(/^(-?\d+(?:[.,]\d+)?)(.*)$/);
    if (shouldSkip || !m) {
      setDisplay(target);
      return;
    }
    const targetNum = parseFloat(m[1].replace(',', '.'));
    const suffix = m[2];
    let raf;
    let start = null;
    const step = (ts) => {
      if (start == null) start = ts;
      const p = Math.min((ts - start) / duration, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      setDisplay(`${Math.round(targetNum * eased)}${suffix}`);
      if (p < 1) raf = requestAnimationFrame(step);
      else setDisplay(target);
    };
    raf = requestAnimationFrame(step);
    return () => { if (raf) cancelAnimationFrame(raf); };
  }, [value, duration, shouldSkip]);

  return <>{display}</>;
}

// Grand format "hero" du total alumni : dégradé doux + halos, nombre animé.
// `extra` permet d'enrichir la carte avec un petit complément d'information
// (micro-répartition actifs/sans expérience) pour occuper l'espace
// horizontalement sans hauteur disproportionnée par rapport au contenu.
function HeroTotalCard({ title, value, subtitle, icon, extra }) {
  return (
    <div className="dash-lift relative flex h-full flex-col overflow-hidden rounded-2xl border border-blue-200/80 bg-gradient-to-br from-blue-50 via-white to-indigo-50 p-5 shadow-[0_1px_2px_rgba(15,23,42,0.05),0_12px_32px_-12px_rgba(15,23,42,0.18)] sm:p-6 dark:border-blue-900/60 dark:from-blue-950/50 dark:via-slate-900 dark:to-indigo-950/40 dark:shadow-none">
      <div aria-hidden="true" className="absolute -right-12 -top-12 h-40 w-40 rounded-full bg-blue-200/40 blur-3xl dark:bg-blue-500/10" />
      <div aria-hidden="true" className="absolute -bottom-16 -left-8 h-44 w-44 rounded-full bg-indigo-200/40 blur-3xl dark:bg-indigo-500/10" />
      <div className="absolute inset-x-6 top-0 h-0.5 rounded-full bg-gradient-to-r from-blue-600 via-blue-500 to-indigo-500" />
      <div className="relative flex flex-1 flex-col items-start justify-between gap-4">
        <div className="flex items-start justify-between gap-4 self-stretch">
          <p className="text-sm font-semibold text-blue-600 dark:text-blue-400">{title}</p>
          <div className="inline-flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl bg-white/80 text-blue-600 ring-1 ring-inset ring-blue-100/80 dark:bg-blue-500/10 dark:text-blue-400 dark:ring-blue-400/20">
            {icon}
          </div>
        </div>
        <div className="flex w-full flex-1 flex-col justify-center">
          <p className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-5xl">
            <AnimatedKpi value={value} />
          </p>
          {subtitle && (
            <p className="mt-1.5 text-sm text-gray-500 dark:text-slate-400">{subtitle}</p>
          )}
          {extra}
        </div>
      </div>
    </div>
  );
}

// Pastille "données fraîches" : heure de la dernière requête.
function FreshnessBadge({ lastUpdated }) {
  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200/70 bg-emerald-50/70 px-3 py-1.5 text-xs font-medium text-emerald-700 dark:border-emerald-500/20 dark:bg-emerald-500/10 dark:text-emerald-300">
      Dernière mise à jour : {formatLastUpdate(lastUpdated)}
    </div>
  );
}

function formatLastUpdate(ts) {
  if (!ts) return null;
  const diffSec = Math.max(0, Math.floor((Date.now() - ts) / 1000));
  if (diffSec < 60) return 'à l\'instant';
  const mins = Math.floor(diffSec / 60);
  if (mins < 60) return `il y a ${mins} min`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `il y a ${hours} h`;
  return 'aujourd\'hui';
}

function DonutChart({ data, size = 140, total }) {
  const maxItems = 6;
  const visible = data.slice(0, maxItems);
  const remaining = data.slice(maxItems);
  const items = remaining.length > 0
    ? [...visible, { label: 'Autres', count: remaining.reduce((s, d) => s + d.count, 0) }]
    : visible;

  const computedTotal = total || items.reduce((s, d) => s + d.count, 0);
  if (computedTotal === 0) {
    return (
      <div className="flex items-center justify-center" style={{ width: size, height: size }}>
        <div className="flex h-24 w-24 items-center justify-center rounded-full border-4 border-dashed border-gray-200 dark:border-slate-600">
          <span className="text-xs font-medium text-gray-400 dark:text-slate-500">—</span>
        </div>
      </div>
    );
  }

  let acc = 0;
  const segments = items.map((item, i) => {
    const pct = (item.count / computedTotal) * 100;
    const start = acc;
    acc += pct;
    return {
      ...item,
      pct,
      start,
      color: item.nonRenseigne ? NEUTRAL_COLOR : CHART_COLORS[i % CHART_COLORS.length],
    };
  });

  // Donut SVG : r sur 100, angle 0° = 12h, sens horaire (identique au
  // conic-gradient d'origine). Chaque segment se dessine via stroke-dashoffset.
  const r = 40;
  const cx = 50;
  const cy = 50;
  const circumference = 2 * Math.PI * r;
  const polar = (deg) => {
    const rad = (deg * Math.PI) / 180;
    return [cx + r * Math.sin(rad), cy - r * Math.cos(rad)];
  };

  return (
    <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:gap-6">
      <div className="dash-donut relative flex-shrink-0" style={{ width: size, height: size }}>
        <svg viewBox="0 0 100 100" className="h-full w-full" aria-hidden="true">
          <circle
            cx={cx}
            cy={cy}
            r={r}
            fill="none"
            strokeWidth="28"
            className="stroke-gray-100 dark:stroke-slate-700/60"
          />
        </svg>
        {segments.map((s, i) => {
          const startDeg = (s.start / 100) * 360;
          const endDeg = ((s.start + s.pct) / 100) * 360;
          const [x0, y0] = polar(startDeg);
          const [x1, y1] = polar(endDeg);
          const largeArc = s.pct > 50 ? 1 : 0;
          const d = `M ${x0.toFixed(3)} ${y0.toFixed(3)} A ${r} ${r} 0 ${largeArc} 1 ${x1.toFixed(3)} ${y1.toFixed(3)}`;
          const segLen = Math.max(circumference * (s.pct / 100) - 0.9, 0.1);
          const fullCircle = s.pct >= 99.95;
          const tipX = cx + r * Math.sin(((startDeg + endDeg) / 2) * (Math.PI / 180));
          const tipY = cy - r * Math.cos(((startDeg + endDeg) / 2) * (Math.PI / 180));
          return (
            <div key={s.label} className="dash-donut-seg">
              <svg viewBox="0 0 100 100" className="h-full w-full" aria-hidden="true">
                <path
                  d={fullCircle ? `M ${cx + r} ${cy} A ${r} ${r} 0 1 1 ${cx - r} ${cy} A ${r} ${r} 0 1 1 ${cx + r} ${cy}` : d}
                  fill="none"
                  stroke={s.color}
                  strokeWidth="28"
                  className="donut-seg"
                  style={{
                    strokeDasharray: `${segLen} ${circumference}`,
                    strokeDashoffset: segLen,
                    ['--seg-len']: segLen,
                    animation: 'donut-seg 1s cubic-bezier(0.16, 1, 0.3, 1) both',
                    animationDelay: `${i * 140}ms`,
                  }}
                />
              </svg>
              <div
                role="tooltip"
                className="dash-donut-tip"
                style={{ left: `${tipX}%`, top: `${tipY}%` }}
              >
                {s.label} : {s.count} alumni ({s.pct.toFixed(0)}%)
              </div>
            </div>
          );
        })}
        <div className="absolute inset-0 m-auto flex h-[70px] w-[70px] items-center justify-center rounded-full bg-white dark:bg-slate-800">
          <span className="text-sm font-bold text-gray-900 dark:text-slate-100">
            <AnimatedKpi value={computedTotal} />
          </span>
        </div>
      </div>
      <div className="flex flex-1 flex-wrap gap-x-4 gap-y-1.5">
        {segments.map((s) => (
          <div key={s.label} className="flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ backgroundColor: s.color }} />
            <span className="text-xs text-gray-600 dark:text-slate-400">{s.label}</span>
            <span className="text-xs font-semibold text-gray-900 dark:text-slate-100">{s.pct.toFixed(0)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// Graphique en barres verticales, utilisé quand plusieurs promotions existent.
// Scalable : une barre par promotion, hauteur proportionnelle au max.
function VerticalBarChart({ data, total }) {
  const maxCount = Math.max(...data.map((d) => d.count), 1);
  return (
    <div className="flex h-44 items-end gap-2.5 sm:gap-3">
      {data.map((stat, i) => {
        const percentage = stat.percentage || (stat.count / Math.max(total, 1)) * 100;
        const heightPct = Math.max((stat.count / maxCount) * 100, 4);
        const color = CHART_COLORS[i % CHART_COLORS.length];
        return (
          <div key={stat.promotion || stat.name || i} className="flex h-full min-w-0 flex-1 flex-col items-center justify-end gap-1.5">
            <span className="text-xs font-semibold text-gray-900 dark:text-slate-100">{stat.count}</span>
            <div
              className="flex w-full flex-1 items-end"
              style={{
                transformOrigin: 'bottom',
                animation: 'grow-y 700ms cubic-bezier(0.16, 1, 0.3, 1) both',
                animationDelay: `${i * 90}ms`,
              }}
            >
              <div
                className="dash-vbar w-full rounded-t-md"
                style={{
                  height: `${heightPct}%`,
                  backgroundColor: color,
                }}
                tip={`${stat.promotion || stat.name} : ${stat.count} alumni (${Number(percentage).toFixed(0)}%)`}
              />
            </div>
            <span className="max-w-full truncate text-[11px] font-medium text-gray-600 dark:text-slate-300">
              {stat.promotion || stat.name}
            </span>
            <span className="text-[10px] text-gray-400 dark:text-slate-500">{Number(percentage).toFixed(0)}%</span>
          </div>
        );
      })}
    </div>
  );
}

function HorizontalBarChart({ data, total }) {
  const maxCount = Math.max(...data.map((d) => d.count), 1);
  return (
    <div className="space-y-3">
      {data.map((stat, i) => {
        const percentage = stat.percentage || (stat.count / Math.max(total, 1)) * 100;
        const barWidth = (stat.count / maxCount) * 100;
        return (
          <div key={stat.promotion || stat.name || i} className="dash-hbar-row">
            <div className="mb-1.5 flex flex-wrap items-center justify-between text-sm">
              <span className="font-medium text-gray-700 dark:text-slate-300">{stat.promotion || stat.name}</span>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400 dark:text-slate-500">{stat.count} alumni</span>
                <span className="inline-flex min-w-[3ch] items-center justify-center rounded bg-blue-50 px-1.5 py-0.5 text-xs font-semibold text-blue-700">
                  {Number(percentage).toFixed(0)}%
                </span>
              </div>
            </div>
            <div className="h-2.5 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-slate-700">
              <div
                className="dash-hbar-fill h-full rounded-full transition-all duration-700 ease-out"
                style={{
                  width: `${Math.min(barWidth, 100)}%`,
                  backgroundColor: CHART_COLORS[i % CHART_COLORS.length],
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

// Sparkline SVG (sans dépendance) : trace l'évolution du taux d'emploi.
// Prête à l'emploi avec un historique de points ; avec une seule valeur
// ponctuelle elle affiche un palier en pointillés + point pulsant.
function Sparkline({ value, points }) {
  const uid = useId().replace(/[^a-zA-Z0-9]/g, '');
  const W = 200;
  const H = 56;
  const PAD = 5;
  const hasHistory = Array.isArray(points) && points.length >= 2;
  const series = hasHistory ? points.slice(0, 24) : [Number(value) || 0];
  const yAt = (v) => PAD + (H - PAD * 2) * (1 - Math.max(0, Math.min(100, v)) / 100);
  const xAt = (i) => PAD + (i / Math.max(series.length - 1, 1)) * (W - PAD * 2);

  const pts = series.map((v, i) => [xAt(i), yAt(v)]);
  const linePath = pts.map(([px, py], i) => `${i === 0 ? 'M' : 'L'} ${px.toFixed(1)} ${py.toFixed(1)}`).join(' ');
  const last = pts[pts.length - 1];

  const segLen = (a, b) => Math.hypot(b[0] - a[0], b[1] - a[1]);
  const totalLen = hasHistory
    ? pts.slice(1).reduce((s, p, i) => s + segLen(pts[i], p), 0)
    : W - PAD * 2;

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="h-full w-full" preserveAspectRatio="none" aria-hidden="true">
      <defs>
        <linearGradient id={`spark-fill-${uid}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#10b981" stopOpacity="0.30" />
          <stop offset="100%" stopColor="#10b981" stopOpacity="0" />
        </linearGradient>
        <linearGradient id={`spark-line-${uid}`} x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#34d399" />
          <stop offset="100%" stopColor="#047857" />
        </linearGradient>
      </defs>
      {!hasHistory && (
        <line
          x1={PAD}
          y1={last[1]}
          x2={W - PAD}
          y2={last[1]}
          stroke="#94a3b8"
          strokeWidth="1.5"
          strokeDasharray="4 4"
          opacity="0.5"
        />
      )}
      {hasHistory && (
        <path
          d={`${linePath} L ${last[0].toFixed(1)} ${(H - PAD).toFixed(1)} L ${pts[0][0].toFixed(1)} ${(H - PAD).toFixed(1)} Z`}
          fill={`url(#spark-fill-${uid})`}
        />
      )}
      <path
        d={linePath}
        fill="none"
        stroke={`url(#spark-line-${uid})`}
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        style={{
          strokeDasharray: totalLen,
          strokeDashoffset: totalLen,
          ['--spark-len']: totalLen,
          animation: 'spark-draw 1.1s cubic-bezier(0.16, 1, 0.3, 1) both',
        }}
      />
      <circle cx={last[0]} cy={last[1]} r="4" fill="#10b981" />
      <circle
        cx={last[0]}
        cy={last[1]}
        r="8"
        fill="none"
        stroke="#10b981"
        strokeWidth="1.5"
        opacity="0.5"
        className="animate-ping"
        style={{ transformOrigin: `${last[0]}px ${last[1]}px` }}
      />
    </svg>
  );
}

function DistributionBars({ distribution }) {
  const items = Array.isArray(distribution)
    ? distribution.filter((d) => d && typeof d.pourcentage === 'number')
    : [];
  if (items.length === 0) return null;
  const segments = items.slice(0, 8);

  return (
    <div className="rounded-xl border border-gray-200/70 dark:border-slate-700/80 bg-white/70 dark:bg-slate-800/60 p-3.5 shadow-sm">
      <div
        className="flex h-2.5 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-slate-700"
        role="img"
        aria-label="Répartition des réponses"
      >
        {segments.map((d, i) => (
          <div
            key={`${d.label}-${i}`}
            className="h-full"
            style={{
              width: `${Math.max(d.pourcentage, 0)}%`,
              backgroundColor: CHART_COLORS[i % CHART_COLORS.length],
            }}
            title={`${d.label} : ${d.pourcentage}%`}
          />
        ))}
      </div>
      <div className="mt-2.5 space-y-1.5">
        {segments.map((d, i) => (
          <div key={`${d.label}-${i}`} className="flex items-center justify-between gap-2 text-sm">
            <span className="flex min-w-0 items-center gap-1.5 text-gray-600 dark:text-slate-300">
              <span
                className="inline-block h-2.5 w-2.5 flex-shrink-0 rounded-full"
                style={{ backgroundColor: CHART_COLORS[i % CHART_COLORS.length] }}
              />
              <span className="truncate">{d.label}</span>
            </span>
            <span className="flex flex-shrink-0 items-center gap-2">
              {typeof d.nb === 'number' && (
                <span className="text-xs text-gray-400 dark:text-slate-500">{d.nb}</span>
              )}
              <span className="font-semibold text-gray-900 dark:text-slate-100">{d.pourcentage}%</span>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function StarIcon() {
  return (
    <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.563.563 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.563.563 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5z" />
    </svg>
  );
}

function RatingVisual({ valeur, unite }) {
  const maxMatch = typeof unite === 'string' ? unite.match(/^\/(\d+)$/) : null;
  const max = maxMatch ? parseInt(maxMatch[1], 10) : 5;
  const score = Number(valeur);
  const clamped = Number.isFinite(score) ? Math.max(0, Math.min(max, score)) : 0;
  // Étoiles pleines : partie entière de la note (floor plutôt que round pour
  // ne pas gonfler visuellement une note non entière, ex. 3.6 -> 3 étoiles).
  const etoilesPleines = Math.floor(clamped);

  return (
    <div className="rounded-xl border border-gray-200/70 dark:border-slate-700/80 bg-white/70 dark:bg-slate-800/60 p-3.5 shadow-sm">
      <div className="flex items-center justify-center gap-3">
        <div className="relative inline-flex" title={`${clamped}/${max}`}>
          <div className="flex text-gray-300 dark:text-slate-600">
            {Array.from({ length: max }, (_, i) => <StarIcon key={i} />)}
          </div>
          <div className="absolute inset-y-0 left-0 overflow-hidden">
            <div className="flex text-amber-400">
              {Array.from({ length: etoilesPleines }, (_, i) => <StarIcon key={i} />)}
            </div>
          </div>
        </div>
        <span className="text-sm font-semibold text-gray-900 dark:text-slate-100">
          {Number.isFinite(score) ? `${score}${unite || ''}` : '—'}
        </span>
      </div>
    </div>
  );
}

// ── Section "Indicateurs complémentaires" ─────────────────────────────
// Nouvelles cartes en bas du Dashboard : types de graphiques
// volontairement différents de ceux déjà utilisés (donut secteurs, barres
// promotion) : jauge "compteur" demi-cercle, anneau à 2 segments, barres
// horizontales multi-couleurs et timeline de maturité des cohortes.
// Toujours en CSS/SVG pur, aucune dépendance graphique ajoutée.

// ── Fourchette de la jauge "Salaire moyen" ─────────────────────────────
// IMPORTANT (cohérence sujet de stage) : cette fourchette est ENTIÈREMENT
// DÉRIVÉE DES DONNÉES INTERNES DU CRM — min/max RÉELS des salaires
// renseignés sur les postes en cours (poste_actuel / expérience en cours,
// salaire > 0, alumni non anonymisés, même périmètre que le salaire
// moyen et le taux d'emploi, exposés par GET /admin/indicateurs). Aucune
// fourchette codée en dur, aucune référence de marché externe : le sujet
// de stage exige des indicateurs d'insertion calculés uniquement à partir
// des données collectées par le CRM (voir aussi
// Rapport/methodologie_indicateurs_dashboard.docx).
//
// Règles de calcul de la fourchette affichée :
//   - Échantillon suffisant (>= SEUIL_ECHANTILLON_SALAIRE salaires) :
//     [min réel - 10 %, max réel + 10 %] — marge de confort pour que le
//     curseur de la jauge ne soit jamais collé au bord.
//   - Échantillon limité (< seuil, ex : 1 seul salaire) : pas de dispersion
//     réelle exploitable, donc on élargit artificiellement autour de la
//     valeur observée ([valeur - 30 %, valeur + 30 %]) et la jauge affiche
//     explicitement la mention "Fourchette indicative — échantillon limité"
//     tant que le seuil n'est pas atteint.
const SEUIL_ECHANTILLON_SALAIRE = 5;
const MARGE_FOURCHETTE_STANDARD = 0.10;
const MARGE_FOURCHETTE_LIMITED = 0.30;

function calculerFourchetteSalaire({ salaireMoyen, salaireMin, salaireMax, salairesRenseignes }) {
  const n = Number(salairesRenseignes) || 0;
  if (n <= 0) return null;
  // min/max réels en base ; à défaut (ex. backend antérieur sans ces champs),
  // repli sur le salaire moyen comme point unique de l'échantillon.
  const minReel = Number.isFinite(Number(salaireMin)) && Number(salaireMin) > 0
    ? Number(salaireMin)
    : Number(salaireMoyen);
  const maxReel = Number.isFinite(Number(salaireMax)) && Number(salaireMax) > 0
    ? Number(salaireMax)
    : Number(salaireMoyen);
  if (!Number.isFinite(minReel) || !Number.isFinite(maxReel)) return null;
  const echLimite = n < SEUIL_ECHANTILLON_SALAIRE;
  const marge = echLimite ? MARGE_FOURCHETTE_LIMITED : MARGE_FOURCHETTE_STANDARD;
  const bas = Math.round(Math.min(minReel, maxReel) * (1 - marge));
  const haut = Math.round(Math.max(minReel, maxReel) * (1 + marge));
  if (haut <= bas) return null;
  return { bas, haut, echantillonLimite: echLimite, nbSalaires: n };
}

// Palette dédiée aux types de contrat (code couleur stable par libellé,
// les autres valeurs tombent dans la palette commune).
const CONTRACT_TYPE_COLORS = {
  'CDI': '#3b82f6',
  'CDD': '#f59e0b',
  'Stage': '#8b5cf6',
  'Alternance': '#10b981',
  'Contrat d’alternance': '#10b981',
  'Apprentissage': '#10b981',
  'Contrat de professionnalisation': '#14b8a6',
  'Freelance': '#ec4899',
  'Indépendant': '#ec4899',
  'Interim': '#f97316',
  'Intérim': '#f97316',
};

const contractTypeColor = (label, index, nonRenseigne) => {
  if (nonRenseigne) return NEUTRAL_COLOR;
  return CONTRACT_TYPE_COLORS[label] || CHART_COLORS[(index + 2) % CHART_COLORS.length];
};

const formatEuros = (v) => new Intl.NumberFormat('fr-FR', {
  style: 'currency',
  currency: 'EUR',
  maximumFractionDigits: 0,
}).format(v);

// Valeur en euros animée (comptage 0 -> valeur) avec formatage monétaire à
// chaque frame ; reprend la logique d'AnimatedKpi mais sur un nombre brut.
function SalaryValue({ value, duration = 800 }) {
  const shouldSkip = import.meta.env?.MODE === 'test'
    || (typeof window !== 'undefined'
      && typeof window.matchMedia === 'function'
      && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  const target = Number.isFinite(Number(value)) ? Math.round(Number(value)) : 0;
  const [display, setDisplay] = useState(shouldSkip ? target : 0);

  useEffect(() => {
    if (shouldSkip || !Number.isFinite(Number(value))) {
      setDisplay(target);
      return undefined;
    }
    let raf;
    let start = null;
    const step = (ts) => {
      if (start == null) start = ts;
      const p = Math.min((ts - start) / duration, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      setDisplay(Math.round(target * eased));
      if (p < 1) raf = requestAnimationFrame(step);
      else setDisplay(target);
    };
    raf = requestAnimationFrame(step);
    return () => { if (raf) cancelAnimationFrame(raf); };
  }, [target, duration, shouldSkip, value]);

  return <>{formatEuros(display)}</>;
}

// Jauge "compteur" demi-cercle : situe le salaire dans la fourchette
// DYNAMIQUE issue des données réelles du CRM (voir calculerFourchetteSalaire,
// dérivée du min/max des salaires renseignés — pas de fourchette codée en dur
// ni de référence de marché externe). Graduations + marqueur, visuellement
// différent des barres de progression utilisées ailleurs.
function SalaryGauge({ value, fourchette }) {
  const uid = useId().replace(/[^a-zA-Z0-9]/g, '');
  const bornes = fourchette || {};
  const { bas = 0, haut = 0, echantillonLimite = false, nbSalaires = 0 } = bornes;
  const amplitude = haut - bas;
  const hasValue = Number.isFinite(Number(value)) && Number(value) > 0 && amplitude > 0;
  const clamped = Math.max(bas, Math.min(haut, Number(value) || bas));
  const pct = hasValue ? (clamped - bas) / amplitude : 0;
  const W = 240;
  const H = 138;
  const cx = W / 2;
  const cy = H - 26;
  const r = 88;
  const arcLen = Math.PI * r;
  const segLen = Math.max(pct * arcLen, 0.1);
  const arcPoint = (t) => {
    const a = Math.PI * (1 - t);
    return [cx + r * Math.cos(a), cy - r * Math.sin(a)];
  };
  const [vx, vy] = arcPoint(pct);
  const arcPath = `M ${(cx - r).toFixed(2)} ${cy} A ${r} ${r} 0 0 1 ${(cx + r).toFixed(2)} ${cy}`;
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((t) => {
    const a = Math.PI * (1 - t);
    return {
      t,
      x1: cx + (r + 10) * Math.cos(a),
      y1: cy - (r + 10) * Math.sin(a),
      x2: cx + (r + 15) * Math.cos(a),
      y2: cy - (r + 15) * Math.sin(a),
    };
  });

  return (
    <div className="flex flex-col items-center">
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="w-full max-w-[300px]"
        role="img"
        aria-label={`Salaire moyen situé dans la fourchette ${formatEuros(bas)} à ${formatEuros(haut)}`}
      >
        <defs>
          <linearGradient id={`gauge-grad-${uid}`} x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#60a5fa" />
            <stop offset="100%" stopColor="#10b981" />
          </linearGradient>
        </defs>
        <path
          d={arcPath}
          fill="none"
          strokeWidth="14"
          strokeLinecap="round"
          className="stroke-gray-100 dark:stroke-slate-700/60"
        />
        {ticks.map((tk) => (
          <line
            key={tk.t}
            x1={tk.x1.toFixed(2)}
            y1={tk.y1.toFixed(2)}
            x2={tk.x2.toFixed(2)}
            y2={tk.y2.toFixed(2)}
            strokeWidth="2"
            strokeLinecap="round"
            opacity="0.9"
            className="stroke-gray-300 dark:stroke-slate-500"
          />
        ))}
        {hasValue && pct > 0 && (
          <path
            d={arcPath}
            fill="none"
            stroke={`url(#gauge-grad-${uid})`}
            strokeWidth="14"
            strokeLinecap="round"
            className="donut-seg dash-gauge-arc"
            style={{
              strokeDasharray: `${segLen} ${arcLen}`,
              strokeDashoffset: segLen,
              ['--seg-len']: segLen,
              animation: 'donut-seg 1s cubic-bezier(0.16, 1, 0.3, 1) both',
            }}
          />
        )}
        {hasValue && (
          <circle
            cx={vx.toFixed(2)}
            cy={vy.toFixed(2)}
            r="6"
            className="fill-white stroke-blue-600 dark:fill-slate-800"
            strokeWidth="3"
          />
        )}
        <text x={cx + r + 6} y={cy + 18} textAnchor="end" className="fill-gray-400 dark:fill-slate-500" fontSize="11" fontWeight="600">
          {Math.round(haut / 1000)}K €
        </text>
        <text x={cx - r - 6} y={cy + 18} textAnchor="start" className="fill-gray-400 dark:fill-slate-500" fontSize="11" fontWeight="600">
          {Math.round(bas / 1000)}K €
        </text>
      </svg>
      {fourchette && (
        <p
          className={`mt-1 text-center text-xs font-medium ${echantillonLimite ? 'text-amber-600 dark:text-amber-400' : 'text-gray-500 dark:text-slate-400'}`}
          data-testid="jauge-salaire-mention"
        >
          {echantillonLimite
            ? `Fourchette indicative — échantillon limité (${nbSalaires} salaire${nbSalaires > 1 ? 's' : ''} renseigné${nbSalaires > 1 ? 's' : ''})`
            : 'Fourchette issue du min/max des salaires renseignés'}
        </p>
      )}

    </div>
  );
}

// Anneau à 2 segments (rempli / vide) : % d'alumni actifs ayant au moins
// une expérience. Plus petit que le donut des secteurs, couleur unique
// émeraude pour s'en distinguer nettement.
function CoverageRing({ pct, avecExp, sansExp }) {
  const p = Math.max(0, Math.min(100, Number(pct) || 0));
  const r = 36;
  const C = 2 * Math.PI * r;
  const segLen = Math.max((p / 100) * C - 1.5, 0.1);

  return (
    <div className="flex items-center justify-center gap-6 sm:justify-start">
      <div className="relative flex-shrink-0" style={{ width: 104, height: 104 }}>
        <svg viewBox="0 0 100 100" className="h-full w-full" aria-hidden="true" style={{ transform: 'rotate(-90deg)' }}>
          <circle
            cx="50"
            cy="50"
            r={r}
            fill="none"
            strokeWidth="14"
            className="stroke-gray-100 dark:stroke-slate-700/60"
          />
          {p > 0 && (
            <circle
              cx="50"
              cy="50"
              r={r}
              fill="none"
              stroke="#10b981"
              strokeWidth="14"
              strokeLinecap="round"
              className="donut-seg dash-gauge-arc"
              style={{
                strokeDasharray: `${segLen} ${C}`,
                strokeDashoffset: segLen,
                ['--seg-len']: segLen,
                animation: 'donut-seg 1s cubic-bezier(0.16, 1, 0.3, 1) both',
              }}
            />
          )}
        </svg>
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
          <span className="text-xl font-bold text-gray-900 dark:text-slate-100">
            <AnimatedKpi value={`${Math.round(p)}%`} />
          </span>
        </div>
      </div>
      <div className="space-y-2.5 text-sm">
        <div className="flex items-center gap-2">
          <span className="inline-block h-3 w-3 flex-shrink-0 rounded-full bg-emerald-500" />
          <span className="text-gray-600 dark:text-slate-300">
            {avecExp} avec expérience
            <span className="ml-1.5 font-semibold text-gray-900 dark:text-slate-100">{Math.round(p)}%</span>
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-block h-3 w-3 flex-shrink-0 rounded-full bg-gray-200 dark:bg-slate-600" />
          <span className="text-gray-600 dark:text-slate-300">
            {sansExp} sans expérience
          </span>
        </div>
      </div>
    </div>
  );
}

// Barres horizontales multi-couleurs : une ligne par type de contrat
// (comptage d'expériences EN COURS, pas d'alumni). Style distinct des
// barres horizontales existantes : couleur par type, barre pleine avec
// le compteur affiché dedans.
function ContractTypesChart({ types }) {
  const total = types.reduce((s, t) => s + t.count, 0);
  const maxCount = Math.max(...types.map((t) => t.count), 1);

  return (
    <div className="space-y-4">
      {types.map((t, i) => {
        const color = contractTypeColor(t.type_contrat, i, t.nonRenseigne);
        const widthPct = Math.max((t.count / maxCount) * 100, 6);
        const pct = total > 0 ? Math.round((t.count / total) * 100) : 0;
        return (
          <div key={t.type_contrat || `type-${i}`}>
            <div className="mb-1.5 flex items-center justify-between gap-2 text-sm">
              <span className="flex items-center gap-1.5 font-medium text-gray-700 dark:text-slate-300">
                <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ backgroundColor: color }} />
                {t.type_contrat}
              </span>
              <span className="text-xs text-gray-400 dark:text-slate-500">{pct}% du total</span>
            </div>
            <div
              className="h-4 w-full overflow-hidden rounded-md bg-gray-100 dark:bg-slate-700/70"
              role="img"
              aria-label={`${t.type_contrat} : ${t.count} expérience${t.count > 1 ? 's' : ''}`}
            >
              <div
                className="dash-typebar flex h-full items-center justify-end rounded-md pr-1.5"
                style={{
                  width: `${widthPct}%`,
                  backgroundColor: color,
                  transformOrigin: 'left',
                  animation: 'grow-x 700ms cubic-bezier(0.16, 1, 0.3, 1) both',
                  animationDelay: `${i * 90}ms`,
                }}
              >
                <span className="text-[10px] font-bold leading-none text-white">
                  {t.count}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// Timeline horizontale de maturité des cohortes pour le calcul à 6 mois :
// réutilise taux_emploi_6mois_par_promotion (statut mature / en_attente).
function CohortMaturityTimeline({ promos }) {
  const sorted = [...promos].sort(
    (a, b) => (a.annee_diplome - b.annee_diplome)
      || String(a.nom_promotion).localeCompare(String(b.nom_promotion)),
  );

  return (
    <div>
      <div className="relative">
        <div aria-hidden="true" className="absolute left-2 right-2 top-[8px] h-0.5 rounded-full bg-gray-200 dark:bg-slate-700" />
        <ol className="relative flex flex-wrap justify-start gap-6 sm:flex-nowrap sm:justify-between sm:gap-3">
          {sorted.map((p) => {
            const mature = p.statut_maturite === 'mature';
            const taux = p.taux_emploi_6mois_pourcentage;
            const refMois = p.date_reference ? p.date_reference.slice(0, 7).split('-') : null;
            const refLabel = refMois ? `${refMois[1]}/${refMois[0]}` : null;
            return (
              <li key={`${p.nom_promotion}-${p.annee_diplome}`} className="flex min-w-0 flex-1 flex-col items-center text-center" style={{ minWidth: 110 }}>
                <span
                  aria-hidden="true"
                  className={`z-10 inline-block h-[17px] w-[17px] rounded-full border-4 ${mature ? 'border-emerald-500' : 'border-amber-400'} bg-white dark:bg-slate-800`}
                />
                <span className="mt-2 max-w-full truncate text-sm font-semibold text-gray-900 dark:text-slate-100">
                  {p.nom_promotion}
                </span>
                <span className="text-xs text-gray-400 dark:text-slate-500">
                  Diplômés {p.annee_diplome} · {p.total_diplomes ?? 0} élève{(p.total_diplomes ?? 0) > 1 ? 's' : ''}
                </span>
                <span className={`mt-2 inline-flex max-w-full items-center gap-1 truncate rounded-full px-2.5 py-1 text-xs font-semibold ${mature ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300' : 'bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-300'}`}>
                  {mature ? `Mature${taux != null ? ` · ${taux}%` : ''}` : 'En attente'}
                  {!mature && refLabel && <span className="font-normal opacity-80">(réf. {refLabel})</span>}
                </span>
              </li>
            );
          })}
        </ol>
      </div>
      <p className="mt-4 text-xs text-gray-400 dark:text-slate-500">
        Méthodologie : hypothèse de diplômation en juin, date de référence à +6 mois (1er décembre).
        Une cohorte est "mature" quand la fenêtre de 6 mois est écoulée.
      </p>
    </div>
  );
}

// Enveloppe commune des cartes de la section complémentaire (même style
// bento que les cartes de charts existantes).
function ComplementCard({ title, subtitle, delay = 0, children }) {
  return (
    <div className="dash-card-in" style={{ animationDelay: delay }}>
      <div className="dash-lift h-full rounded-2xl border border-gray-200/70 dark:border-slate-700/80 bg-white dark:bg-slate-800 p-6 shadow-[0_1px_2px_rgba(15,23,42,0.05),0_12px_32px_-12px_rgba(15,23,42,0.18)] dark:shadow-none sm:p-7">
        <h2 className="text-lg font-semibold tracking-tight text-gray-900 dark:text-slate-100">{title}</h2>
        {subtitle && <p className="mb-5 mt-1 text-xs text-gray-400 dark:text-slate-500">{subtitle}</p>}
        {children}
      </div>
    </div>
  );
}

export default function AdminDashboard() {
  const [kpis, setKpis] = useState(null);
  const [sectorStats, setSectorStats] = useState([]);
  const [promotionStats, setPromotionStats] = useState([]);
  const [kpiTags, setKpiTags] = useState([]);
  const [complement, setComplement] = useState(null);
  const [typesContrat, setTypesContrat] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [kpisRes, sectorRes, promoRes, kpiTagsRes, complementRes, typesRes] = await Promise.all([
        statsAPI.getKPIs().catch(() => ({ data: null })),
        statsAPI.getBySector().catch(() => ({ data: [] })),
        statsAPI.getByPromotion().catch(() => ({ data: [] })),
        statsAPI.getKpiTags().catch(() => ({ data: [] })),
        statsAPI.getIndicateursComplementaires().catch(() => ({ data: null })),
        statsAPI.getTypesContrat().catch(() => ({ data: [] })),
      ]);
      setKpis(kpisRes.data);
      setSectorStats(sectorRes.data || []);
      setPromotionStats(promoRes.data || []);
      setKpiTags(kpiTagsRes.data || []);
      setComplement(complementRes.data || null);
      setTypesContrat(typesRes.data || []);
      setLastUpdated(Date.now());
    } catch (err) {
      setError(err.response?.data?.detail || 'Impossible de charger les statistiques.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) return <LoadingSpinner text="Chargement du tableau de bord..." />;
  if (error) return <ErrorMessage message={error} onRetry={fetchData} />;

  const mockKPIs = kpis || {
    total_alumni: 0,
    employment_rate_6m: 0,
    employment_rate_brut: 0,
    avg_response_rate: 0,
    active_alumni: 0,
    recent_updates: 0,
  };

  // Micro-répartition affichée dans la carte hero : part des alumni actifs
  // (au moins 1 expérience) parmi le total. Le pourcentage n'est affiché que
  // si les données sont cohérentes (actifs <= total).
  const activePct = mockKPIs.total_alumni > 0
    && mockKPIs.active_alumni <= mockKPIs.total_alumni
    ? Math.round((mockKPIs.active_alumni / mockKPIs.total_alumni) * 100)
    : null;

  const inactiveAlumni = mockKPIs.total_alumni - mockKPIs.active_alumni;

  // ── Données dérivées pour la section "Indicateurs complémentaires" ──
  const comp = complement || {
    salaire_moyen: null,
    salaires_renseignes: 0,
    salaire_min: null,
    salaire_max: null,
    taux_emploi_6mois_par_promotion: [],
    alumni_actifs: mockKPIs.active_alumni,
    taux_couverture: mockKPIs.avg_response_rate || 0,
  };
  const salaireMoyen = Number(comp.salaire_moyen);
  // Fourchette de la jauge salaire : calculée DYNAMIQUEMENT depuis les
  // salaires réels en base (min/max exposés par l'API), jamais codée en dur.
  const fourchetteSalaire = calculerFourchetteSalaire({
    salaireMoyen,
    salaireMin: comp.salaire_min,
    salaireMax: comp.salaire_max,
    salairesRenseignes: comp.salaires_renseignes,
  });
  const tauxCouverture = Math.round(comp.taux_couverture || 0);
  const cohortes = comp.taux_emploi_6mois_par_promotion || [];
  const aDesComplementaires = comp.salaire_moyen != null
    || typesContrat.length > 0
    || tauxCouverture > 0
    || cohortes.length > 0;

  return (
    <div className="space-y-8">
      {/* En-tête + indicateur de fraîcheur des données */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-slate-100">Tableau de bord</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">
            Vue d'ensemble des indicateurs Alumni
          </p>
        </div>
        {lastUpdated && <FreshnessBadge lastUpdated={lastUpdated} />}
      </div>

      {/* Bento grid : KPIs principaux — hiérarchie visuelle sans vide flagrant :
          hero (7/12) + emploi 6 mois (5/12), puis 3 cartes égales (4/12). */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-12 xl:gap-6">
        <div className="dash-card-in sm:col-span-2 xl:col-span-7" style={{ animationDelay: '40ms' }}>
          <HeroTotalCard
            title="Total Alumni actifs"
            value={mockKPIs.total_alumni}
            subtitle="Comptes non anonymisés"
            extra={
              activePct != null ? (
                <div className="mt-4 w-full">
                  <div
                    className="flex h-2 w-full overflow-hidden rounded-full bg-indigo-100 dark:bg-slate-700"
                    role="img"
                    aria-label={`${activePct}% des alumni ont au moins une expérience`}
                  >
                    <div className="dash-bar-fill h-full rounded-full bg-gradient-to-r from-blue-600 to-indigo-500" style={{ width: `${activePct}%` }} />
                  </div>
                  <div className="mt-2 flex items-center justify-between gap-3 text-xs text-gray-500 dark:text-slate-400">
                    <span className="inline-flex items-center gap-1.5">
                      <span className="inline-block h-2 w-2 rounded-full bg-blue-600" />
                      {mockKPIs.active_alumni} actifs · {activePct}%
                    </span>
                    <span className="inline-flex items-center gap-1.5">
                      <span className="inline-block h-2 w-2 rounded-full bg-indigo-200 dark:bg-slate-600" />
                      {inactiveAlumni} sans expérience
                    </span>
                  </div>
                </div>
              ) : null
            }
            icon={
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z" />
              </svg>
            }
          />
        </div>

        <div className="dash-card-in sm:col-span-2 xl:col-span-5" style={{ animationDelay: '120ms' }}>
          <KPICard
            title="Taux d'emploi à 6 mois"
            value={<AnimatedKpi value={`${mockKPIs.employment_rate_6m}%`} />}
            subtitle="Diplômés en emploi < 6 mois"
            progress={mockKPIs.employment_rate_6m}
            color="green"
            highlighted
            icon={
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 0 0 .75-1.661V8.706c0-1.081-.768-2.015-1.837-2.175a48.114 48.114 0 0 0-3.413-.387m4.5 8.006c-.194.165-.42.295-.673.38A23.978 23.978 0 0 1 12 15.75c-2.648 0-5.195-.429-7.577-1.22a2.016 2.016 0 0 1-.673-.38m0 0A2.18 2.18 0 0 1 3 12.489V8.706c0-1.081.768-2.015 1.837-2.175a48.111 48.111 0 0 1 3.413-.387m7.5 0V5.25A2.25 2.25 0 0 0 13.5 3h-3a2.25 2.25 0 0 0-2.25 2.25v.894m7.5 0a48.667 48.667 0 0 0-7.5 0" />
              </svg>
            }
          />
        </div>

        <div className="dash-card-in relative sm:col-span-2 xl:col-span-4" style={{ animationDelay: '200ms' }}>
          <KPICard
            title="Taux d'emploi global"
            value={<AnimatedKpi value={`${mockKPIs.employment_rate_brut}%`} />}
            subtitle="Tous diplômés confondus"
            progress={mockKPIs.employment_rate_brut}
            color="green"
            icon={
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3v11.25A2.25 2.25 0 0 0 6 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0 1 18 16.5h-2.25m-7.5 0h7.5m-7.5 0-1 3m8.5-3 1 3m0 0 .5 1.5m-.5-1.5h-9.5m0 0-.5 1.5m.75-9 3-3 2.148 2.148A12.061 12.061 0 0 1 16.5 7.605" />
              </svg>
            }
          />
          <div className="pointer-events-none absolute bottom-4 right-4 h-10 w-1/3">
            <Sparkline value={mockKPIs.employment_rate_brut} />
          </div>
        </div>

        <div className="dash-card-in xl:col-span-4" style={{ animationDelay: '280ms' }}>
          <KPICard
            title="Alumni actifs"
            value={<AnimatedKpi value={mockKPIs.active_alumni} />}
            subtitle="Au moins 1 expérience"
            color="cyan"
            icon={
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.362 5.214A8.252 8.252 0 0 1 12 21 8.25 8.25 0 0 1 6.038 7.047 8.287 8.287 0 0 0 9 9.601a8.983 8.983 0 0 1 3.361-6.867 8.21 8.21 0 0 0 3 2.48Z" />
              </svg>
            }
          />
        </div>

        <div className="dash-card-in xl:col-span-4" style={{ animationDelay: '360ms' }}>
          <KPICard
            title="Taux de complétion"
            value={<AnimatedKpi value={mockKPIs.avg_response_rate ? `${mockKPIs.avg_response_rate}%` : '0%'} />}
            subtitle="Profil avec expérience"
            progress={mockKPIs.avg_response_rate}
            color="purple"
            icon={
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15a2.25 2.25 0 0 1 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25ZM6.75 12h.008v.008H6.75V12Zm0 3h.008v.008H6.75V15Zm0 3h.008v.008H6.75V18Z" />
              </svg>
            }
          />
        </div>
      </div>

      {/* Indicateurs des enquêtes - cartes générées dynamiquement à partir des tags */}
      {kpiTags.length > 0 && (
        <div>
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">Indicateurs des enquêtes</h2>
            <p className="mt-0.5 text-sm text-gray-500 dark:text-slate-400">
              Calculés automatiquement depuis les tags des questions actives
            </p>
          </div>
          <div className="grid grid-cols-1 gap-6 lg:gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {kpiTags.map((kpi, i) => {
              const estBooleanOuChoice = kpi.question_type === 'boolean' || kpi.question_type === 'choice';
              const montreDistribution = estBooleanOuChoice
                && Array.isArray(kpi.distribution)
                && kpi.distribution.length > 0;
              const montreRating = kpi.question_type === 'rating'
                && kpi.valeur != null
                && kpi.nb_repondants > 0;
              return (
                <div
                  key={kpi.tag}
                  className="dash-card-in flex flex-col gap-2"
                  style={{ animationDelay: `${440 + i * 70}ms` }}
                >
                  <KPICard
                    title={kpi.libelle || kpi.tag}
                    value={formatKpiValue(kpi)}
                    subtitle={formatKpiSubtitle(kpi)}
                    color={KPI_TAG_COLORS[i % KPI_TAG_COLORS.length]}
                    icon={
                      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3v11.25A2.25 2.25 0 0 0 6 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0 1 18 16.5h-2.25m-7.5 0h7.5m-7.5 0-1 3m8.5-3 1 3m0 0 .5 1.5m-.5-1.5h-9.5m0 0-.5 1.5" />
                      </svg>
                    }
                  />
                  {montreRating && <RatingVisual valeur={kpi.valeur} unite={kpi.unite} />}
                  {montreDistribution && <DistributionBars distribution={kpi.distribution} />}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2 lg:gap-6">
        <div className="dash-card-in" style={{ animationDelay: '440ms' }}>
          <div className="dash-lift h-full rounded-2xl border border-gray-200/70 dark:border-slate-700/80 bg-white dark:bg-slate-800 p-6 sm:p-7 shadow-[0_1px_2px_rgba(15,23,42,0.05),0_12px_32px_-12px_rgba(15,23,42,0.18)] dark:shadow-none">
            <h2 className="mb-5 text-lg font-semibold tracking-tight text-gray-900 dark:text-slate-100">Répartition par secteur</h2>
            {sectorStats.length === 0 ? (
              <div className="flex flex-col items-center py-10">
                <svg className="mb-3 h-10 w-10 text-gray-300" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6A2.25 2.25 0 0 1 6 3.75h2.25A2.25 2.25 0 0 1 10.5 6v2.25a2.25 2.25 0 0 1-2.25 2.25H6a2.25 2.25 0 0 1-2.25-2.25V6Zm0 9.75A2.25 2.25 0 0 1 6 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 18v-2.25Zm9.75 0A2.25 2.25 0 0 1 16 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H16a2.25 2.25 0 0 1-2.25-2.25v-2.25Z" />
                </svg>
                <p className="text-sm text-gray-400 dark:text-slate-500">Aucune donnée sectorielle disponible</p>
              </div>
            ) : (
              <DonutChart
                data={sectorStats.map((s) => ({
                  label: s.sector || s.name,
                  count: s.count,
                  nonRenseigne: s.nonRenseigne,
                }))}
                total={mockKPIs.total_alumni}
              />
            )}
          </div>
        </div>

        <div className="dash-card-in" style={{ animationDelay: '520ms' }}>
          <div className="dash-lift h-full rounded-2xl border border-gray-200/70 dark:border-slate-700/80 bg-white dark:bg-slate-800 p-6 sm:p-7 shadow-[0_1px_2px_rgba(15,23,42,0.05),0_12px_32px_-12px_rgba(15,23,42,0.18)] dark:shadow-none">
            <h2 className="mb-5 text-lg font-semibold tracking-tight text-gray-900 dark:text-slate-100">Alumni par promotion</h2>
            {promotionStats.length === 0 ? (
              <div className="flex flex-col items-center py-10">
                <svg className="mb-3 h-10 w-10 text-gray-300" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.62 48.62 0 0 1 12 20.904a48.62 48.62 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347m-15.482 0a50.636 50.636 0 0 0-2.658-.813A59.906 59.906 0 0 1 12 3.493a59.903 59.903 0 0 1 10.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.717 50.717 0 0 1 12 13.489a50.702 50.702 0 0 1 7.74-3.342" />
                </svg>
                <p className="text-sm text-gray-400 dark:text-slate-500">Aucune donnée promotion disponible</p>
              </div>
            ) : promotionStats.length > 1 ? (
              <VerticalBarChart data={promotionStats} total={mockKPIs.total_alumni} />
            ) : (
              <HorizontalBarChart data={promotionStats} total={mockKPIs.total_alumni} />
            )}
          </div>
        </div>
      </div>

      {/* Indicateurs complémentaires : types de graphiques distincts de ceux
          déjà utilisés (gauge compteur, anneau 2 segments, barres horizontales
          multi-couleurs, timeline de maturité des cohortes). */}
      {aDesComplementaires && (
        <div>
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">Indicateurs complémentaires</h2>
            <p className="mt-0.5 text-sm text-gray-500 dark:text-slate-400">
              Lecture croisée des données déjà consolidées côté backend
            </p>
          </div>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-3 xl:gap-6">
            <ComplementCard
              title="Salaire moyen"
              subtitle="Postes en cours, salaires renseignés uniquement"
              delay="600ms"
            >
              {Number.isFinite(salaireMoyen) && salaireMoyen > 0 ? (
                <>
                  <p className="mb-4 text-3xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
                    <SalaryValue value={salaireMoyen} />
                  </p>
                  {fourchetteSalaire && (
                    <SalaryGauge value={salaireMoyen} fourchette={fourchetteSalaire} />
                  )}
                  <p className="mt-3 text-xs text-gray-400 dark:text-slate-500">
                    Calculé sur {comp.salaires_renseignes} salaire{comp.salaires_renseignes > 1 ? 's' : ''} brut{comp.salaires_renseignes > 1 ? 's' : ''} annuel{comp.salaires_renseignes > 1 ? 's' : ''}
                  </p>
                </>
              ) : (
                <p className="py-10 text-center text-sm text-gray-400 dark:text-slate-500">
                  Aucun salaire renseigné sur les postes en cours
                </p>
              )}
            </ComplementCard>

            <ComplementCard
              title="Taux de couverture"
              subtitle="Alumni actifs avec au moins une expérience renseignée"
              delay="680ms"
            >
              <CoverageRing
                pct={tauxCouverture}
                avecExp={comp.alumni_actifs || 0}
                sansExp={inactiveAlumni}
              />
              <p className="mt-5 text-xs text-gray-400 dark:text-slate-500">
                Un taux faible signifie un taux d'emploi mécaniquement sous-estimé
                (alumni sans parcours déclaré exclus du numérateur).
              </p>
            </ComplementCard>

            <ComplementCard
              title="Types de contrat"
              subtitle="Expériences professionnelles en cours"
              delay="760ms"
            >
              {typesContrat.length === 0 ? (
                <p className="py-10 text-center text-sm text-gray-400 dark:text-slate-500">
                  Aucune expérience en cours à afficher
                </p>
              ) : (
                <ContractTypesChart types={typesContrat} />
              )}
            </ComplementCard>
          </div>

          {cohortes.length > 0 && (
            <div className="dash-card-in mt-5" style={{ animationDelay: '840ms' }}>
              <div className="dash-lift rounded-2xl border border-gray-200/70 dark:border-slate-700/80 bg-white dark:bg-slate-800 p-6 shadow-[0_1px_2px_rgba(15,23,42,0.05),0_12px_32px_-12px_rgba(15,23,42,0.18)] dark:shadow-none sm:p-7">
                <h2 className="mb-5 text-lg font-semibold tracking-tight text-gray-900 dark:text-slate-100">
                  Maturité des cohortes
                  <span className="ml-2 align-middle text-xs font-normal text-gray-400 dark:text-slate-500">(calcul à 6 mois)</span>
                </h2>
                <CohortMaturityTimeline promos={cohortes} />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
