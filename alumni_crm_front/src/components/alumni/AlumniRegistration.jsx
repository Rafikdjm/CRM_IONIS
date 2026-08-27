import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { alumniAPI, promotionsAPI } from '../../services/api';
import { buildAcademicEmail } from '../../utils/academicEmail';

const INITIAL_STATE = {
  first_name: '',
  last_name: '',
  email: '',
  email_academique: '',
  phone: '',
  date_of_birth: '',
  address: '',
  city: '',
  country: '',
  id_promotion: '',
  previous_education: '',
  previous_school: '',
  linkedin: '',
};

const STEPS = [
  { key: 'personal', label: 'Informations personnelles', icon: UserIcon },
  { key: 'academic', label: 'Parcours académique', icon: AcademicIcon },
  { key: 'social', label: 'Réseaux sociaux', icon: LinkIcon },
];

function UserIcon({ className }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
    </svg>
  );
}

function AcademicIcon({ className }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.62 48.62 0 0 1 12 20.904a48.62 48.62 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347m-15.482 0a50.636 50.636 0 0 0-2.658-.813A59.906 59.906 0 0 1 12 3.493a59.903 59.903 0 0 1 10.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.717 50.717 0 0 1 12 13.489a50.702 50.702 0 0 1 7.74-3.342" />
    </svg>
  );
}

function LinkIcon({ className }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 0 1 1.242 7.244l-4.5 4.5a4.5 4.5 0 0 1-6.364-6.364l1.757-1.757m9.86-4.09a4.5 4.5 0 0 0-1.242-7.244l-4.5-4.5a4.5 4.5 0 0 0-6.364 6.364L4.34 8.374" />
    </svg>
  );
}

function CheckIcon({ className }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
    </svg>
  );
}

function InfoTooltip({ text }) {
  const [show, setShow] = useState(false);
  return (
    <span className="relative z-10 ml-1.5 inline-flex">
      <button
        type="button"
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
        onClick={() => setShow((s) => !s)}
        className="inline-flex h-4 w-4 items-center justify-center rounded-full text-blue-400 transition-colors hover:bg-blue-50 hover:text-blue-600 dark:hover:bg-blue-950 dark:hover:text-blue-300 min-h-[44px] min-w-[44px]"
      >
        <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
        </svg>
      </button>
      {show && (
        <span className="absolute bottom-full left-1/2 z-30 mb-2 w-56 -translate-x-1/2 rounded-lg border border-gray-200 bg-gray-900 px-3 py-2 text-xs text-white shadow-lg dark:border-slate-600">
          {text}
          <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-900" />
        </span>
      )}
    </span>
  );
}

export default function AlumniRegistration() {
  const navigate = useNavigate();
  const [form, setForm] = useState(INITIAL_STATE);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [promotions, setPromotions] = useState([]);
  const [touched, setTouched] = useState({});
  const [activeStep, setActiveStep] = useState(0);
  const [emailAcademiqueEdited, setEmailAcademiqueEdited] = useState(false);

  useEffect(() => {
    promotionsAPI.getAll().then((res) => setPromotions(res.data || [])).catch(() => {});
  }, []);

  // Pré-remplissage temps réel de l'email académique dès que le prénom ET le
  // nom sont saisis. Le champ reste modifiable : dès que l'étudiant le touche,
  // on cesse de l'écraser.
  useEffect(() => {
    if (emailAcademiqueEdited) return;
    const first = (form.first_name || '').trim();
    const last = (form.last_name || '').trim();
    if (!first || !last) return;
    const auto = buildAcademicEmail(first, last);
    if (auto) {
      setForm((prev) => (prev.email_academique === auto ? prev : { ...prev, email_academique: auto }));
    }
  }, [form.first_name, form.last_name, emailAcademiqueEdited]);

  const sectionFields = useMemo(() => [
    ['first_name', 'last_name', 'email'],
    ['id_promotion'],
    [],
  ], []);

  const stepCompletion = useMemo(() => {
    return sectionFields.map((fields) => fields.every((f) => form[f] && String(form[f]).trim() !== ''));
  }, [form, sectionFields]);

  const completedSteps = stepCompletion.filter(Boolean).length;

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === 'email_academique') {
      setEmailAcademiqueEdited(true);
    }
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleBlur = (field) => {
    setTouched((prev) => ({ ...prev, [field]: true }));
  };

  const getFieldState = (name, required = false) => {
    if (!touched[name] || !form[name]) return 'default';
    if (required && !form[name].trim()) return 'error';
    if (name === 'email' && form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) return 'error';
    if (name === 'email_academique' && form.email_academique && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email_academique)) return 'error';
    if (name === 'phone' && form.phone && !/^[\d\s\-+()]*$/.test(form.phone)) return 'error';
    if (name === 'linkedin' && form.linkedin && !/^https?:\/\//.test(form.linkedin)) return 'error';
    return 'valid';
  };

  const inputClass = (name, required = false) => {
    const state = getFieldState(name, required);
    const base = 'w-full max-w-full rounded-lg border px-3 py-2.5 text-sm transition-all duration-200 outline-none sm:px-4';
    const focus = 'focus:ring-1 focus:ring-blue-500/20';
    if (state === 'error') return `${base} border-red-300 bg-red-50/30 focus:border-red-400 focus:ring-1 focus:ring-red-400/20 dark:border-red-800 dark:bg-red-950/30 dark:text-slate-100`;
    if (state === 'valid') return `${base} border-emerald-300 bg-emerald-50/20 focus:border-blue-500 ${focus} dark:border-emerald-700 dark:bg-emerald-950/20 dark:text-slate-100`;
    return `${base} border-gray-300 bg-white focus:border-blue-500 ${focus} dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100`;
  };

  const labelClass = 'mb-1 block text-sm font-medium text-gray-700 dark:text-slate-300';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const payload = { ...form, email: form.email.trim().toLowerCase() };
      const res = await alumniAPI.create(payload);
      void res;
      setSuccess(true);
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map((d) => d.msg).join(', '));
      } else {
        setError(detail || "Erreur lors de l'inscription. Veuillez réessayer.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (success) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900">
            <svg className="h-8 w-8 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-slate-100">Inscription réussie !</h2>
          <p className="mt-2 text-sm text-gray-500 dark:text-slate-400">
            Votre compte a été créé. Connectez-vous avec votre email pour recevoir un code OTP.
          </p>
          <div className="mt-6 flex justify-center gap-3">
            <button
              onClick={() => navigate('/', { state: { prefillEmail: form.email.trim().toLowerCase() } })}
              className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition-colors hover:bg-blue-700 min-h-[44px]"
            >
              Se connecter
            </button>
            <button
              onClick={() => { setForm(INITIAL_STATE); setSuccess(false); setTouched({}); setActiveStep(0); setEmailAcademiqueEdited(false); }}
              className="rounded-lg border border-gray-300 bg-white px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 min-h-[44px]"
            >
              Inscrire un autre
            </button>
          </div>
        </div>
      </div>
    );
  }

  const scrollToSection = (index) => {
    setActiveStep(index);
    const sectionIds = ['section-personal', 'section-academic', 'section-social'];
    document.getElementById(sectionIds[index])?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-slate-100">Inscription</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">
          Créez votre profil alumni en renseignant vos informations personnelles et votre parcours
        </p>
      </div>

      {/* Progress Stepper */}
      <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <div className="flex items-center justify-between">
          {STEPS.map((step, i) => {
            const StepIcon = step.icon;
            const isCompleted = stepCompletion[i];
            const isCurrent = i === activeStep;
            return (
              <div key={step.key} className="flex flex-1 items-center">
                <button
                  type="button"
                  onClick={() => scrollToSection(i)}
                  className="group flex flex-col items-center gap-1.5 min-h-[44px] min-w-[44px]"
                >
                  <div className={`flex h-11 w-11 items-center justify-center rounded-full border-2 transition-all duration-300 ${
                    isCompleted
                      ? 'border-blue-600 bg-blue-600 text-white shadow-sm shadow-blue-200 dark:shadow-blue-900'
                      : isCurrent
                        ? 'border-blue-600 bg-blue-50 text-blue-600 shadow-sm shadow-blue-100 dark:bg-blue-950 dark:text-blue-400 dark:shadow-blue-900'
                        : 'border-gray-300 bg-white text-gray-400 group-hover:border-blue-300 group-hover:text-blue-500 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-500 dark:group-hover:border-blue-400 dark:group-hover:text-blue-400'
                  }`}>
                    {isCompleted ? (
                      <CheckIcon className="h-5 w-5" />
                    ) : (
                      <StepIcon className="h-5 w-5" />
                    )}
                  </div>
                  <span className={`text-xs font-medium ${
                    isCurrent ? 'block' : 'hidden sm:block'
                  } ${
                    isCurrent ? 'text-blue-600' : isCompleted ? 'text-blue-600' : 'text-gray-400 dark:text-slate-500'
                  }`}>
                    {step.label}
                  </span>
                </button>
                {i < STEPS.length - 1 && (
                  <div className="mx-2 hidden h-px flex-1 sm:block">
            <div className={`h-full transition-colors duration-500 ${
              isCompleted ? 'bg-blue-400' : 'bg-gray-200 dark:bg-slate-600'
                    }`} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
        <div className="mt-3 flex items-center gap-2">
          <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-gray-100 dark:bg-slate-700">
            <div
              className="h-full rounded-full bg-blue-600 transition-all duration-500"
              style={{ width: `${(completedSteps / STEPS.length) * 100}%` }}
            />
          </div>
          <span className="text-xs font-medium text-gray-500 dark:text-slate-400">
            {completedSteps}/{STEPS.length} complété
          </span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Section: Informations personnelles */}
        <div id="section-personal" className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <div className="mb-5 flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50 text-blue-600 dark:bg-blue-950 dark:text-blue-400">
              <UserIcon className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">Informations personnelles</h2>
              <p className="text-xs text-gray-400 dark:text-slate-500">Vos coordonnées et informations de base</p>
            </div>
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 [&>*]:min-w-0">
            <div>
              <label className={labelClass}>
                Prénom <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="first_name"
                value={form.first_name}
                onChange={handleChange}
                onBlur={() => handleBlur('first_name')}
                required
                className={inputClass('first_name', true)}
              />
            </div>
            <div>
              <label className={labelClass}>
                Nom <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="last_name"
                value={form.last_name}
                onChange={handleChange}
                onBlur={() => handleBlur('last_name')}
                required
                className={inputClass('last_name', true)}
              />
            </div>
            <div>
              <label className={labelClass}>
                Email <span className="text-red-500">*</span>
              </label>
              <input
                type="email"
                name="email"
                value={form.email}
                onChange={handleChange}
                onBlur={() => handleBlur('email')}
                required
                className={inputClass('email', true)}
              />
              {getFieldState('email', true) === 'error' && form.email && (
                <p className="mt-1 text-xs text-red-500">Format email invalide</p>
              )}
            </div>
            <div>
              <label className={labelClass}>
                Email académique <InfoTooltip text="Généré automatiquement à partir de votre prénom et nom. Vous pouvez le personnaliser." />
              </label>
              <input
                type="email"
                name="email_academique"
                value={form.email_academique}
                onChange={handleChange}
                onBlur={() => handleBlur('email_academique')}
                placeholder="prenom.nom@ionis-stm.com"
                className={inputClass('email_academique')}
              />
              {getFieldState('email_academique') === 'error' && form.email_academique && (
                <p className="mt-1 text-xs text-red-500">Format email invalide</p>
              )}
            </div>
            <div>
              <label className={labelClass}>
                Téléphone <InfoTooltip text="Format attendu : +33 6 12 34 56 78 ou 06 12 34 56 78" />
              </label>
              <input
                type="tel"
                name="phone"
                value={form.phone}
                onChange={handleChange}
                onBlur={() => handleBlur('phone')}
                placeholder="+33 6 12 34 56 78"
                className={inputClass('phone')}
              />
              {getFieldState('phone') === 'error' && form.phone && (
                <p className="mt-1 text-xs text-red-500">Caractères non autorisés</p>
              )}
            </div>
            <div>
              <label className={labelClass}>Date de naissance</label>
              <input
                type="date"
                name="date_of_birth"
                value={form.date_of_birth}
                onChange={handleChange}
                className={inputClass('date_of_birth')}
              />
            </div>
            <div>
              <label className={labelClass}>Ville</label>
              <input
                type="text"
                name="city"
                value={form.city}
                onChange={handleChange}
                className={inputClass('city')}
              />
            </div>
            <div className="md:col-span-2">
              <label className={labelClass}>Adresse</label>
              <input
                type="text"
                name="address"
                value={form.address}
                onChange={handleChange}
                className={inputClass('address')}
              />
            </div>
            <div>
              <label className={labelClass}>Pays</label>
              <input
                type="text"
                name="country"
                value={form.country}
                onChange={handleChange}
                placeholder="France"
                className={inputClass('country')}
              />
            </div>
          </div>
        </div>

        {/* Section: Parcours académique */}
        <div id="section-academic" className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <div className="mb-5 flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50 text-blue-600 dark:bg-blue-950 dark:text-blue-400">
              <AcademicIcon className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">Parcours académique</h2>
              <p className="text-xs text-gray-400 dark:text-slate-500">Votre formation et établissement d'origine</p>
            </div>
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 [&>*]:min-w-0">
            <div>
              <label className={labelClass}>
                Promotion <span className="text-red-500">*</span>
              </label>
              <select
                name="id_promotion"
                value={form.id_promotion}
                onChange={handleChange}
                onBlur={() => handleBlur('id_promotion')}
                required
                className={inputClass('id_promotion', true)}
              >
                <option value="">Sélectionner une promotion</option>
                {promotions.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({p.year})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Formation précédente</label>
              <input
                type="text"
                name="previous_education"
                value={form.previous_education}
                onChange={handleChange}
                placeholder="Ex: Licence Informatique"
                className={inputClass('previous_education')}
              />
            </div>
            <div>
              <label className={labelClass}>Établissement précédent</label>
              <input
                type="text"
                name="previous_school"
                value={form.previous_school}
                onChange={handleChange}
                placeholder="Ex: Université Paris-Saclay"
                className={inputClass('previous_school')}
              />
            </div>
          </div>
        </div>

        {/* Section: Réseaux sociaux */}
        <div id="section-social" className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <div className="mb-5 flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50 text-blue-600 dark:bg-blue-950 dark:text-blue-400">
              <LinkIcon className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">Réseaux sociaux</h2>
              <p className="text-xs text-gray-400 dark:text-slate-500">Votre présence en ligne</p>
            </div>
          </div>
          <div>
            <label className={labelClass}>
              Profil LinkedIn <InfoTooltip text="Collez l'URL complète de votre profil LinkedIn" />
            </label>
            <input
              type="url"
              name="linkedin"
              value={form.linkedin}
              onChange={handleChange}
              onBlur={() => handleBlur('linkedin')}
              placeholder="https://linkedin.com/in/votre-profil"
              className={inputClass('linkedin')}
            />
            {getFieldState('linkedin') === 'error' && form.linkedin && (
              <p className="mt-1 text-xs text-red-500">L'URL doit commencer par http:// ou https://</p>
            )}
          </div>
        </div>

        {error && (
          <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-900 dark:bg-red-950">
            <svg className="mt-0.5 h-5 w-5 flex-shrink-0 text-red-500" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
            </svg>
            <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
          </div>
        )}

        <div className="flex justify-end gap-3 border-t border-gray-100 pt-6 dark:border-slate-700">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="rounded-lg border border-gray-300 bg-white px-5 py-2.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 min-h-[44px]"
          >
            Annuler
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white shadow-sm transition-all duration-200 hover:bg-blue-700 hover:shadow-md disabled:cursor-not-allowed disabled:opacity-50 min-h-[44px]"
          >
            {submitting ? (
              <>
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                Inscription en cours...
              </>
            ) : (
              <>
                S'inscrire
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
                </svg>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
