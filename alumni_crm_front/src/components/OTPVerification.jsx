import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useTheme } from '../contexts/theme';
import './otpEffects.css';

const FLIGHT_STEP_MS = 90;
const FLIGHT_DURATION_MS = 520;
const ERROR_FLASH_MS = 900;
const REDUCED_MOTION_QUERY = '(prefers-reduced-motion: reduce)';

const SHOW_DEV_PREVIEW =
  import.meta.env.DEV && (import.meta.env.VITE_OTP_MODE || 'console') === 'console';

const PARTICLE_COLORS = {
  light: ['#06b6d4', '#0d9488', '#2563eb', '#14b8a6', '#047857'],
  dark: ['#22d3ee', '#5eead4', '#60a5fa', '#2dd4bf', '#34d399'],
};

function prefersReducedMotion() {
  return (
    typeof window !== 'undefined' &&
    typeof window.matchMedia === 'function' &&
    window.matchMedia(REDUCED_MOTION_QUERY).matches
  );
}

function nextFrame(cb) {
  if (typeof window !== 'undefined' && typeof window.requestAnimationFrame === 'function') {
    return window.requestAnimationFrame(cb);
  }
  return window.setTimeout(cb, 16);
}

function cancelFrame(id) {
  if (typeof window !== 'undefined' && typeof window.cancelAnimationFrame === 'function') {
    window.cancelAnimationFrame(id);
  } else {
    window.clearTimeout(id);
  }
}

function ParticleField() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const colors = PARTICLE_COLORS[isDark ? 'dark' : 'light'];

  const [particles] = useState(() =>
    Array.from({ length: 22 }, (_, i) => {
      const angle = (i / 22) * Math.PI * 2 + (Math.random() * 0.6 - 0.3);
      const distance = 70 + Math.random() * 90;
      return {
        id: i,
        dx: Math.cos(angle) * distance,
        dy: Math.sin(angle) * distance,
        size: 4 + Math.random() * 7,
        round: Math.random() > 0.45,
        color: colors[i % colors.length],
        delay: Math.random() * 120,
        life: 650 + Math.random() * 350,
      };
    }),
  );

  return (
    <div className="otp-particle-layer" aria-hidden="true">
      {particles.map((p) => (
        <span
          key={p.id}
          className="otp-particle"
          style={{
            '--dx': `${p.dx}px`,
            '--dy': `${p.dy}px`,
            '--life': `${p.life}ms`,
            '--delay': `${p.delay}ms`,
            width: `${p.size}px`,
            height: `${p.size}px`,
            borderRadius: p.round ? '9999px' : '2px',
            background: p.color,
          }}
        />
      ))}
    </div>
  );
}

export default function OTPVerification({
  length = 6,
  disabled = false,
  onComplete,
  error = null,
  errorKey = 0,
  resetKey = 0,
  success = false,
}) {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [digits, setDigits] = useState(() => Array(length).fill(''));
  const [sourceDigits, setSourceDigits] = useState(() => Array(length).fill(''));
  const [ghosts, setGhosts] = useState([]);
  const [errorActive, setErrorActive] = useState(false);

  const inputRefs = useRef([]);
  const slotRefs = useRef([]);
  const sourceSlotRefs = useRef([]);
  const fillTimerRef = useRef(null);
  const fillRafRef = useRef(null);
  const errorTimerRef = useRef(null);
  const onCompleteRef = useRef(onComplete);

  const reducedMotion = useMemo(() => prefersReducedMotion(), []);

  useEffect(() => {
    onCompleteRef.current = onComplete;
  }, [onComplete]);

  useEffect(() => {
    if (!disabled && !success) {
      inputRefs.current[0]?.focus();
    }
  }, [disabled, success]);

  useEffect(() => {
    setDigits(Array(length).fill(''));
    setSourceDigits(Array(length).fill(''));
    setGhosts([]);
    inputRefs.current[0]?.focus();
  }, [resetKey, length]);

  useEffect(() => {
    if (!error) return;
    setErrorActive(true);
    setDigits(Array(length).fill(''));
    setSourceDigits(Array(length).fill(''));
    setGhosts([]);
    if (errorTimerRef.current) window.clearTimeout(errorTimerRef.current);
    errorTimerRef.current = window.setTimeout(() => setErrorActive(false), ERROR_FLASH_MS);
    inputRefs.current[0]?.focus();
  }, [error, errorKey, length]);

  useEffect(
    () => () => {
      if (fillTimerRef.current) window.clearTimeout(fillTimerRef.current);
      if (errorTimerRef.current) window.clearTimeout(errorTimerRef.current);
      if (fillRafRef.current) cancelFrame(fillRafRef.current);
    },
    [],
  );

  const commitAndVerify = useCallback(
    (code) => {
      const normalized = code.replace(/\D/g, '').slice(0, length);
      if (normalized.length !== length) return;
      setDigits(normalized.split(''));
      setGhosts([]);
      setSourceDigits(Array(length).fill(''));
      onCompleteRef.current(normalized);
    },
    [length],
  );

  const fillCode = useCallback(
    (code) => {
      if (disabled || success) return;
      const normalized = code.replace(/\D/g, '').slice(0, length);
      if (normalized.length !== length) return;

      if (prefersReducedMotion()) {
        commitAndVerify(normalized);
        return;
      }

      setSourceDigits(normalized.split(''));
      if (fillTimerRef.current) window.clearTimeout(fillTimerRef.current);
      if (fillRafRef.current) cancelFrame(fillRafRef.current);

      fillRafRef.current = nextFrame(() => {
        fillRafRef.current = nextFrame(() => {
          const sources = sourceSlotRefs.current.map((el) => el?.getBoundingClientRect());
          const targets = slotRefs.current.map((el) => el?.getBoundingClientRect());

          const next = normalized.split('').map((digit, i) => {
            const fallback = { left: 0, top: 0, width: 0, height: 0 };
            const t = targets[i] || fallback;
            const s = sources[i];
            const origin = s && s.width > 0 && s.height > 0 ? s : t;
            return {
              id: `${Date.now()}-${i}`,
              digit,
              fx: origin.left + origin.width / 2,
              fy: origin.top + origin.height / 2,
              tx: t.left + t.width / 2,
              ty: t.top + t.height / 2,
              delay: i * FLIGHT_STEP_MS,
              flying: false,
            };
          });

          setGhosts(next);
          nextFrame(() => {
            setGhosts((prev) => prev.map((g) => ({ ...g, flying: true })));
          });

          if (fillTimerRef.current) window.clearTimeout(fillTimerRef.current);
          fillTimerRef.current = window.setTimeout(
            () => commitAndVerify(normalized),
            FLIGHT_DURATION_MS + (length - 1) * FLIGHT_STEP_MS,
          );
        });
      });
    },
    [disabled, success, length, commitAndVerify],
  );

  const handleChange = useCallback(
    (index, e) => {
      if (disabled || success || ghosts.length > 0) return;
      const raw = e.target.value;
      const cleaned = raw.replace(/\D/g, '');
      if (cleaned.length === 0) {
        e.target.value = '';
        return;
      }

      if (cleaned.length > 1) {
        e.target.value = '';
        fillCode(cleaned);
        return;
      }

      const next = [...digits];
      next[index] = cleaned;
      setDigits(next);

      if (index < length - 1) {
        inputRefs.current[index + 1]?.focus();
      }

      if (next.every((d) => d !== '')) {
        onCompleteRef.current(next.join(''));
      }
    },
    [disabled, success, ghosts.length, digits, length, fillCode],
  );

  const handleKeyDown = useCallback(
    (index, e) => {
      if (disabled || success) return;
      if (e.key === 'Backspace') {
        e.preventDefault();
        const next = [...digits];
        if (next[index]) {
          next[index] = '';
          setDigits(next);
        } else if (index > 0) {
          next[index - 1] = '';
          setDigits(next);
          inputRefs.current[index - 1]?.focus();
        }
      } else if (e.key === 'ArrowLeft' && index > 0) {
        e.preventDefault();
        inputRefs.current[index - 1]?.focus();
      } else if (e.key === 'ArrowRight' && index < length - 1) {
        e.preventDefault();
        inputRefs.current[index + 1]?.focus();
      }
    },
    [disabled, success, digits, length],
  );

  const handlePaste = useCallback(
    (e) => {
      if (disabled || success) return;
      e.preventDefault();
      const text = e.clipboardData?.getData('text') || '';
      fillCode(text);
    },
    [disabled, success, fillCode],
  );

  if (success) {
    return (
      <div className="otp-verification">
        <div className="otp-success-area" role="status" aria-live="polite">
          {!reducedMotion && <ParticleField />}
          <div className="otp-check-wrapper">
            <svg viewBox="0 0 64 64" aria-hidden="true">
              <circle className="otp-check-circle" cx="32" cy="32" r="29" pathLength="100" />
              <path className="otp-check-path" d="M19 33 L28 42 L45 24" pathLength="100" />
            </svg>
          </div>
          <p className="otp-success-title text-gray-900 dark:text-white">E-mail vérifié</p>
          <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300">
            <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z" />
            </svg>
            Vérifié et sécurisé
          </span>
        </div>
      </div>
    );
  }

  const status = errorActive ? 'error' : '';

  return (
    <div className="otp-verification" data-status={status}>
      {SHOW_DEV_PREVIEW && (
        <div className="otp-source mb-5 flex items-center gap-3 rounded-xl border p-3" aria-hidden="true">
          <div className={`flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg ${isDark ? 'bg-cyan-400/10 text-cyan-300' : 'bg-blue-100 text-blue-600'}`}>
            <svg className="h-4.5 w-4.5" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75" />
            </svg>
          </div>
          <div className="min-w-0 flex-1 text-left">
            <p className={`truncate text-xs font-semibold ${isDark ? 'text-white/90' : 'text-gray-700'}`}>Code de connexion</p>
            <p className={`text-[11px] ${isDark ? 'text-blue-200/40' : 'text-gray-400'}`}>Aperçu de l'e-mail reçu</p>
            <div className="mt-1.5 flex gap-1">
              {sourceDigits.map((d, i) => (
                <span
                  key={i}
                  ref={(el) => { sourceSlotRefs.current[i] = el; }}
                  className={`flex h-6 w-5 items-center justify-center rounded text-[11px] font-bold ${isDark ? 'bg-white/[0.06] text-cyan-300' : 'border border-gray-200 bg-white text-blue-700'}`}
                >
                  {d || '•'}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="otp-boxes flex justify-center gap-2.5 sm:gap-3" role="group" aria-label={`Code à ${length} chiffres`}>
        {digits.map((d, i) => (
          <div key={i} ref={(el) => { slotRefs.current[i] = el; }} className="otp-slot">
            <input
              ref={(el) => { inputRefs.current[i] = el; }}
              type="text"
              inputMode="numeric"
              autoComplete="one-time-code"
              maxLength={6}
              aria-label={`Chiffre ${i + 1}`}
              value={d}
              disabled={disabled}
              onChange={(e) => handleChange(i, e)}
              onKeyDown={(e) => handleKeyDown(i, e)}
              onPaste={handlePaste}
              className={`otp-input h-12 w-11 rounded-xl text-center text-lg font-bold outline-none disabled:opacity-40 sm:h-14 sm:w-12 ${isDark ? 'border border-white/[0.08] bg-white/[0.06] text-white' : 'border border-gray-300 bg-white text-gray-900'}`}
            />
          </div>
        ))}
      </div>

      {ghosts.length > 0 && (
        <div aria-hidden="true">
          {ghosts.map((g) => (
            <span
              key={g.id}
              className={`otp-ghost${g.flying ? ' is-flying' : ''}`}
              style={{
                '--fx': `${g.fx}px`,
                '--fy': `${g.fy}px`,
                '--tx': `${g.tx}px`,
                '--ty': `${g.ty}px`,
                '--delay': `${g.delay}ms`,
              }}
            >
              {g.digit}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
