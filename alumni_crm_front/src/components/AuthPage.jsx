import { useState, useEffect, useCallback } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { loginAPI } from '../services/api';
import { useTheme } from '../contexts/theme';
import OTPVerification from './OTPVerification';
import ionisStmLogo from '../assets/ionis-stm-logo.png';

const OTP_LENGTH = 6;
const OTP_MODE = import.meta.env.VITE_OTP_MODE || 'console';
const IS_CONSOLE_MODE = OTP_MODE === 'console';
const IS_RESEND_MODE = OTP_MODE === 'resend';
// Doit rester aligné sur le rate-limit serveur (60 s entre deux demandes OTP)
// pour que le bouton « Renvoyer le code » ne se réactive pas avant que le
// serveur n'autorise réellement un nouvel envoi.
const RESEND_COOLDOWN = 60;
const OTP_SUCCESS_DURATION = 3000;

function AbstractBackground() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
      <svg className="absolute h-full w-full" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <filter id="blobBlur" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="70" />
          </filter>
          <linearGradient id="blob1Grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.35" />
            <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0.15" />
          </linearGradient>
          <linearGradient id="blob2Grad" x1="0%" y1="100%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.25" />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.12" />
          </linearGradient>
          <linearGradient id="blob3Grad" x1="100%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#6366f1" stopOpacity="0.2" />
            <stop offset="100%" stopColor="#0ea5e9" stopOpacity="0.1" />
          </linearGradient>
        </defs>
        <g filter="url(#blobBlur)">
          <ellipse cx="18%" cy="22%" rx="280" ry="240" fill="url(#blob1Grad)" />
          <ellipse cx="82%" cy="78%" rx="320" ry="260" fill="url(#blob2Grad)" />
          <ellipse cx="78%" cy="15%" rx="200" ry="180" fill="url(#blob3Grad)" />
          <ellipse cx="15%" cy="85%" rx="220" ry="180" fill="url(#blob2Grad)" />
        </g>
      </svg>

      <svg
        className="absolute right-[-6%] top-[12%] h-[280px] w-[280px] opacity-[0.07] sm:h-[380px] sm:w-[380px]"
        viewBox="0 0 200 200"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          fill="#60a5fa"
          d="M44.5,-55.1C57.2,-46.2,66.2,-32.1,71.2,-16.1C76.2,-0.1,77.2,17.8,69.4,32.1C61.6,46.4,44.9,57.1,28.4,63.8C11.9,70.6,-4.5,73.4,-20.2,69.8C-35.8,66.2,-50.7,56.2,-60.7,42.2C-70.7,28.2,-75.8,10.2,-73.2,-6.7C-70.6,-23.6,-60.3,-39.3,-47.1,-48.1C-33.9,-56.9,-17.9,-58.7,-0.1,-58.5C17.7,-58.4,31.8,-64,44.5,-55.1Z"
          transform="translate(100 100)"
        />
      </svg>

      <svg
        className="absolute bottom-[8%] left-[-4%] h-[260px] w-[260px] opacity-[0.06] sm:h-[360px] sm:w-[360px]"
        viewBox="0 0 200 200"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          fill="#38bdf8"
          d="M39.9,-65.7C51.1,-60.2,59.1,-48.1,66.2,-35.1C73.3,-22.1,79.5,-8.2,77.1,4.5C74.7,17.2,63.7,28.7,53.4,39.5C43.1,50.3,33.4,60.4,21,66.5C8.6,72.6,-6.5,74.7,-20.3,70.6C-34.1,66.5,-46.6,56.2,-56.5,43.5C-66.4,30.8,-73.7,15.7,-74.5,0.6C-75.3,-14.5,-69.6,-29.5,-60.3,-41.1C-51,-52.7,-38.1,-60.9,-24.8,-66.3C-11.5,-71.7,2.3,-74.3,15.6,-72.3C28.9,-70.3,41.7,-63.7,39.9,-65.7Z"
          transform="translate(100 100)"
        />
      </svg>
    </div>
  );
}

export default function AuthPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();

  const [adminMode, setAdminMode] = useState(false);

  // ── Alumni state (OTP flow) ──
  const [step, setStep] = useState('EMAIL_STEP');
  const [email, setEmail] = useState(location.state?.prefillEmail || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [cooldown, setCooldown] = useState(0);
  const [otpError, setOtpError] = useState(null);
  const [otpErrorKey, setOtpErrorKey] = useState(0);
  const [otpResetKey, setOtpResetKey] = useState(0);
  const [otpSuccess, setOtpSuccess] = useState(false);
  const [otpAttemptsLeft, setOtpAttemptsLeft] = useState(null);

  // ── Admin state (code flow) ──
  const [adminCode, setAdminCode] = useState('');
  const [adminLoading, setAdminLoading] = useState(false);
  const [adminError, setAdminError] = useState(null);
  const [showAdminCode, setShowAdminCode] = useState(false);

  useEffect(() => {
    if (cooldown <= 0) return;
    const timer = setTimeout(() => setCooldown((c) => c - 1), 1000);
    return () => clearTimeout(timer);
  }, [cooldown]);

  // ── Alumni handlers ──
  const handleRequestOTP = async (e) => {
    e.preventDefault();
    const trimmed = email.trim();
    if (!trimmed) return;
    setLoading(true);
    setError(null);
    try {
      await loginAPI.requestOTP(trimmed);
      setOtpSuccess(false);
      setStep('OTP_STEP');
      setCooldown(RESEND_COOLDOWN);
      setOtpError(null);
      setOtpAttemptsLeft(null);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(detail || 'Impossible d\'envoyer le code. Vérifiez votre email.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = useCallback(async (code) => {
    setOtpError(null);
    setLoading(true);
    try {
      const result = await loginAPI.verifyOTP(email, code);
      const role = result.data?.role;
      setOtpSuccess(true);
      setTimeout(() => {
        navigate(role === 'admin' ? '/admin' : '/alumni');
      }, OTP_SUCCESS_DURATION);
    } catch (err) {
      const detail = err.response?.data?.detail;
      const status = err.response?.status;

      setOtpErrorKey((k) => k + 1);
      if (status === 429) {
        setOtpError(detail || 'Trop de tentatives. Veuillez réessayer plus tard.');
        setOtpAttemptsLeft(0);
        setTimeout(() => setStep('EMAIL_STEP'), 3000);
      } else if (status === 410) {
        setOtpError('Ce code a expiré. Un nouveau code a été envoyé.');
        setCooldown(RESEND_COOLDOWN);
      } else {
        const match = (detail || '').match(/(\d+)\s*(tentative|essai)/i);
        const left = match ? parseInt(match[1], 10) : null;
        setOtpAttemptsLeft(left);
        setOtpError(detail || 'Code incorrect. Veuillez réessayer.');
      }
    } finally {
      setLoading(false);
    }
  }, [email, navigate]);

  const handleResend = async () => {
    if (cooldown > 0) return;
    setLoading(true);
    try {
      await loginAPI.requestOTP(email);
      setCooldown(RESEND_COOLDOWN);
      setOtpError(null);
      setOtpErrorKey((k) => k + 1);
      setOtpResetKey((k) => k + 1);
      setOtpSuccess(false);
      setOtpAttemptsLeft(null);
    } catch (err) {
      const detail = err.response?.data?.detail;
      const retryAfter = parseInt(err.response?.headers?.['retry-after'], 10);
      if (!Number.isNaN(retryAfter) && retryAfter > 0) {
        setCooldown(retryAfter);
      }
      setOtpError(detail || 'Impossible de renvoyer le code. Veuillez réessayer.');
      setOtpErrorKey((k) => k + 1);
    } finally {
      setLoading(false);
    }
  };

  const handleBackToEmail = () => {
    setStep('EMAIL_STEP');
    setLoading(false);
    setOtpError(null);
    setOtpErrorKey((k) => k + 1);
    setOtpSuccess(false);
    setOtpAttemptsLeft(null);
    setError(null);
  };

  // ── Admin handler ──
  const handleAdminLogin = async (e) => {
    e.preventDefault();
    if (!adminCode.trim()) return;
    setAdminLoading(true);
    setAdminError(null);
    try {
      await loginAPI.adminLogin(adminCode.trim());
      navigate('/admin');
    } catch (err) {
      const detail = err.response?.data?.detail;
      const status = err.response?.status;
      if (status === 429) {
        setAdminError(detail || 'Trop de tentatives. Réessayez dans quelques minutes.');
      } else {
        setAdminError(detail || 'Code d\'accès incorrect.');
      }
    } finally {
      setAdminLoading(false);
    }
  };

  const toggleAdminMode = () => {
    setAdminMode((prev) => !prev);
    setStep('EMAIL_STEP');
    setOtpError(null);
    setOtpAttemptsLeft(null);
    setError(null);
    setEmail('');
    setAdminCode('');
    setAdminError(null);
    setShowAdminCode(false);
  };

  const isDark = theme === 'dark';

  return (
    <div className={`relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-8 sm:px-6 ${isDark ? 'bg-gradient-to-br from-[#0a1628] via-[#0f2247] to-[#162d5a]' : 'bg-gradient-to-br from-blue-50 via-blue-100 to-indigo-100'}`}>
      <AbstractBackground />

      <button
        onClick={toggleTheme}
        type="button"
        aria-label={isDark ? 'Passer en mode clair' : 'Passer en mode sombre'}
        className={`absolute right-4 top-4 z-20 flex h-11 w-11 items-center justify-center rounded-full backdrop-blur-sm transition sm:right-6 sm:top-6 ${isDark ? 'border border-white/10 bg-white/5 text-white/60 hover:bg-white/10 hover:text-white/90' : 'border border-gray-300 bg-white/70 text-gray-500 hover:bg-white hover:text-gray-800 shadow-sm'}`}
      >
        {isDark ? (
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m6.364.386-1.591 1.591M21 12h-2.25m-.386 6.364-1.591-1.591M12 18.75V21m-4.773-4.227-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0Z" />
          </svg>
        ) : (
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.72 9.72 0 0 1 18 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 0 0 3 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 0 0 9.002-5.998Z" />
          </svg>
        )}
      </button>

      <div className="relative z-10 w-full max-w-[420px]">
        <div className={`rounded-3xl p-8 backdrop-blur-xl sm:p-10 ${isDark ? 'border border-white/[0.08] bg-[#0d1f3c]/80 shadow-[0_25px_60px_-12px_rgba(0,0,0,0.5)]' : 'border border-gray-200 bg-white/80 shadow-xl'}`}>
          <div className="mb-8 flex flex-col items-center text-center">
            {adminMode ? (
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 to-blue-500 shadow-lg shadow-blue-500/20">
                <svg className="h-7 w-7 text-white" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z" />
                </svg>
              </div>
            ) : (
              <img
                src={ionisStmLogo}
                alt="Logo IONIS STM"
                className="mb-4 h-14 w-auto max-w-[220px] object-contain"
              />
            )}
            <h1 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Alumni CRM</h1>
            <p className={`mt-1 text-sm ${isDark ? 'text-blue-200/60' : 'text-gray-500'}`}>
              {adminMode ? 'Espace administrateur' : 'Réseau des anciens'}
            </p>
          </div>

          {adminMode ? (
            // ── Mode admin : connexion par code d'accès fixe ──
            <>
              <div className="mb-6 text-center">
                <h2 className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Connexion Administration</h2>
                <p className={`mt-1.5 text-sm ${isDark ? 'text-blue-200/50' : 'text-gray-500'}`}>
                  Saisissez le code d'accès administrateur
                </p>
              </div>

              <form onSubmit={handleAdminLogin}>
                <div className="mb-5">
                  <label htmlFor="admin-code" className={`mb-2 block text-sm font-medium ${isDark ? 'text-blue-100/80' : 'text-gray-700'}`}>
                    Code d'accès
                  </label>
                  <div className="relative">
                    <input
                      id="admin-code"
                      type={showAdminCode ? 'text' : 'password'}
                      value={adminCode}
                      onChange={(e) => setAdminCode(e.target.value)}
                      placeholder="Entrez votre code d'accès"
                      required
                      autoFocus
                      className={`w-full rounded-xl px-4 py-3.5 pr-12 text-base outline-none transition-all sm:text-sm ${isDark ? 'border border-white/[0.08] bg-white/[0.06] text-white placeholder-blue-200/30 focus:border-cyan-400/40 focus:bg-white/[0.1] focus:ring-2 focus:ring-cyan-400/20' : 'border border-gray-300 bg-white text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500'}`}
                    />
                    <button
                      type="button"
                      onClick={() => setShowAdminCode((v) => !v)}
                      className={`absolute right-3 top-1/2 -translate-y-1/2 transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center ${isDark ? 'text-blue-200/40 hover:text-blue-200/70' : 'text-gray-400 hover:text-gray-600'}`}
                      tabIndex={-1}
                    >
                      {showAdminCode ? (
                        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88" />
                        </svg>
                      ) : (
                        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                          <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                        </svg>
                      )}
                    </button>
                  </div>
                </div>

                {adminError && (
                  <div className="mb-5 flex items-start gap-3 rounded-xl border border-red-500/20 bg-red-50 dark:bg-red-500/10 p-4">
                    <svg className="mt-0.5 h-5 w-5 flex-shrink-0 text-red-500 dark:text-red-400" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
                    </svg>
                    <p className="break-words text-sm text-red-600 dark:text-red-300">{adminError}</p>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={adminLoading || !adminCode.trim()}
                    className="inline-flex w-full min-h-[44px] items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-4 py-3.5 text-base font-semibold text-white shadow-lg shadow-blue-500/25 transition-all hover:from-cyan-400 hover:to-blue-500 hover:shadow-xl hover:shadow-blue-500/30 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none sm:text-sm"
                >
                  {adminLoading ? (
                    <>
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                      Connexion...
                    </>
                  ) : (
                    <>
                      Se connecter
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
                      </svg>
                    </>
                  )}
                </button>
              </form>
            </>
          ) : (
            // ── Mode alumni : flux OTP classique ──
            step === 'EMAIL_STEP' ? (
              <>
                <div className="mb-6 text-center">
                  <h2 className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Se connecter</h2>
                  <p className={`mt-1.5 text-sm ${isDark ? 'text-blue-200/50' : 'text-gray-500'}`}>
                    Entrez votre email pour recevoir un code de connexion
                  </p>
                </div>

                <form onSubmit={handleRequestOTP}>
                  <div className="mb-5">
                    <label htmlFor="email" className={`mb-2 block text-sm font-medium ${isDark ? 'text-blue-100/80' : 'text-gray-700'}`}>
                      Adresse email
                    </label>
                    <input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="votre.email@exemple.com"
                      required
                      className={`w-full rounded-xl px-4 py-3.5 text-base outline-none transition-all sm:text-sm ${isDark ? 'border border-white/[0.08] bg-white/[0.06] text-white placeholder-blue-200/30 focus:border-cyan-400/40 focus:bg-white/[0.1] focus:ring-2 focus:ring-cyan-400/20' : 'border border-gray-300 bg-white text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500'}`}
                    />
                  </div>

                  {error && (
                    <div className="mb-5 flex items-start gap-3 rounded-xl border border-red-500/20 bg-red-50 dark:bg-red-500/10 p-4">
                      <svg className="mt-0.5 h-5 w-5 flex-shrink-0 text-red-500 dark:text-red-400" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
                      </svg>
                      <p className="break-words text-sm text-red-600 dark:text-red-300">{error}</p>
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={loading || !email.trim()}
                  className="inline-flex w-full min-h-[44px] items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-4 py-3.5 text-base font-semibold text-white shadow-lg shadow-blue-500/25 transition-all hover:from-cyan-400 hover:to-blue-500 hover:shadow-xl hover:shadow-blue-500/30 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none sm:text-sm"
                  >
                    {loading ? (
                      <>
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                        Envoi en cours...
                      </>
                    ) : (
                      <>
                        Envoyer le code
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
                        </svg>
                      </>
                    )}
                  </button>
                  
                </form>
              </>
            ) : (
              <>
                <div className="mb-6 text-center">
                  <h2 className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Vérification</h2>
                  <p className={`mt-1.5 text-sm ${isDark ? 'text-blue-200/50' : 'text-gray-500'}`}>
                    Code envoyé à <span className={isDark ? 'text-blue-200/70' : 'text-gray-700'}>{email}</span>
                  </p>
                </div>

                <div className="mb-6">
                  {!otpSuccess && (
                    <p className={`mb-3 block text-center text-sm font-medium ${isDark ? 'text-blue-100/80' : 'text-gray-700'}`}>
                      Saisissez le code à 6 chiffres
                    </p>
                  )}
                  <OTPVerification
                    length={OTP_LENGTH}
                    onComplete={handleVerifyOTP}
                    disabled={loading}
                    error={otpError}
                    errorKey={otpErrorKey}
                    resetKey={otpResetKey}
                    success={otpSuccess}
                  />
                  {!otpSuccess && import.meta.env.DEV && IS_CONSOLE_MODE && (
                    <p className={`mt-3 text-center text-xs ${isDark ? 'text-blue-200/30' : 'text-gray-400'}`}>
                      (En mode développement, le code correct est affiché dans la console du navigateur)
                    </p>
                  )}
                  {!otpSuccess && IS_RESEND_MODE && (
                    <p className={`mt-3 text-center text-xs ${isDark ? 'text-blue-200/50' : 'text-gray-500'}`}>
                      Vérifier votre email
                    </p>
                  )}
                </div>

                {loading && (
                  <div className={`mb-5 flex items-center justify-center gap-2 text-sm ${isDark ? 'text-blue-200/60' : 'text-gray-500'}`}>
                    <div className={`h-4 w-4 animate-spin rounded-full border-2 ${isDark ? 'border-blue-200/30 border-t-blue-200' : 'border-gray-300 border-t-blue-600'}`} />
                    Vérification en cours...
                  </div>
                )}

                {otpError && (
                  <div className="mb-5 flex items-start gap-3 rounded-xl border border-red-500/20 bg-red-50 dark:bg-red-500/10 p-4">
                    <svg className="mt-0.5 h-5 w-5 flex-shrink-0 text-red-500 dark:text-red-400" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
                    </svg>
                    <div className="text-sm text-red-600 dark:text-red-300">
                      <p>{otpError}</p>
                      {otpAttemptsLeft != null && otpAttemptsLeft > 0 && (
                        <p className="mt-1 text-xs text-red-500/70 dark:text-red-400/70">
                          Il vous reste {otpAttemptsLeft} tentative{otpAttemptsLeft > 1 ? 's' : ''}.
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {!otpSuccess && (
                  <div className="flex flex-col items-center gap-3">
                    <button
                      type="button"
                      onClick={handleResend}
                      disabled={cooldown > 0 || loading}
                      className={`inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium transition-colors disabled:cursor-not-allowed min-h-[44px] ${isDark ? 'text-cyan-400 hover:text-cyan-300 hover:bg-white/5 disabled:text-blue-200/30' : 'text-blue-600 hover:text-blue-800 hover:bg-blue-50 disabled:text-gray-400'}`}
                    >
                      {cooldown > 0
                        ? `Renvoyer le code dans ${cooldown}s`
                        : 'Renvoyer le code'}
                    </button>

                    <button
                      type="button"
                      onClick={handleBackToEmail}
                      disabled={loading}
                      className={`inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium transition-colors disabled:opacity-50 min-h-[44px] ${isDark ? 'text-blue-200/40 hover:text-blue-200/70 hover:bg-white/5' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'}`}
                    >
                      Modifier l'email
                    </button>
                  </div>
                )}
              </>
            )
          )}

          <div className="mt-6 flex flex-col items-center gap-3">
            {!adminMode && (
              <p className={`text-sm ${isDark ? 'text-blue-200/50' : 'text-gray-500'}`}>
                Pas encore de compte ?{' '}
                <Link to="/alumni/register" className={`inline-flex items-center rounded-lg px-2 py-1 font-medium transition-colors min-h-[44px] ${isDark ? 'text-cyan-400 hover:text-cyan-300 hover:bg-white/5' : 'text-blue-600 hover:text-blue-800 hover:bg-blue-50'}`}>
                  S'inscrire
                </Link>
              </p>
            )}
            <button
              type="button"
              onClick={toggleAdminMode}
              className={`inline-flex items-center rounded-lg px-4 py-2 text-xs font-medium no-underline transition-colors min-h-[44px] ${isDark ? 'text-blue-200/30 hover:text-blue-200/60 hover:bg-white/5' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'}`}
            >
              {adminMode ? 'Retour — Connexion alumni' : 'Accès Administration'}
            </button>
          </div>
        </div>

        <div className="mt-6 flex items-center justify-center gap-6 sm:gap-8">
          <div className="text-center">
            <p className={`text-lg font-bold sm:text-xl ${isDark ? 'text-white' : 'text-gray-900'}`}>2 500+</p>
            <p className={`text-xs ${isDark ? 'text-blue-200/40' : 'text-gray-500'}`}>Alumni actifs</p>
          </div>
          <div className={`h-6 w-px ${isDark ? 'bg-white/10' : 'bg-gray-300'}`} />
          <div className="text-center">
            <p className={`text-lg font-bold sm:text-xl ${isDark ? 'text-white' : 'text-gray-900'}`}>150+</p>
            <p className={`text-xs ${isDark ? 'text-blue-200/40' : 'text-gray-500'}`}>Entreprises</p>
          </div>
          <div className={`h-6 w-px ${isDark ? 'bg-white/10' : 'bg-gray-300'}`} />
          <div className="text-center">
            <p className={`text-lg font-bold sm:text-xl ${isDark ? 'text-white' : 'text-gray-900'}`}>35+</p>
            <p className={`text-xs ${isDark ? 'text-blue-200/40' : 'text-gray-500'}`}>Promotions</p>
          </div>
        </div>

        <p className={`mt-6 text-center text-[11px] ${isDark ? 'text-blue-200/25' : 'text-gray-400'}`}>
          Alumni CRM &mdash; Prototype fonctionnel
        </p>
      </div>
    </div>
  );
}
