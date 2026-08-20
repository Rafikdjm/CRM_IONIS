import { useState, useEffect } from 'react';
import { careerAPI, alumniAPI } from '../../services/api';
import { SECTORS } from '../../constants';
import LoadingSpinner from '../shared/LoadingSpinner';
import ErrorMessage from '../shared/ErrorMessage';

const CONTRACT_TYPES = ['CDI', 'CDD', 'Freelance', 'Alternance', 'Stage', 'Intérim', 'Autre'];

const EMPTY_CAREER = {
  company: '',
  position: '',
  sector: '',
  custom_sector: '',
  type_contrat: '',
  start_date: '',
  end_date: '',
  salary_range: '',
  is_current: false,
  description: '',
  pays: '',
  ville: '',
};

const EMPTY_CERTIFICATION = {
  name: '',
  issuer: '',
  date_obtained: '',
};

function CareerForm({ career, index, onChange, onRemove }) {
  const handleChange = (field, value) => {
    onChange(index, { ...career, [field]: value });
  };

  return (
    <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-slate-600 dark:bg-slate-800/50">
      <div className="mb-3 flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700 dark:text-slate-300">
          {career.is_current ? 'Poste actuel' : `Poste #${index + 1}`}
          {!career.id && (
            <span className="ml-2 rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700 dark:bg-amber-950 dark:text-amber-300">
              Non sauvegardé
            </span>
          )}
        </span>
        <button
          type="button"
          onClick={() => onRemove(index)}
          title={career.id ? 'Supprimer ce poste (enregistré)' : 'Retirer ce poste du formulaire'}
          className="inline-flex items-center gap-1 rounded-lg px-3 py-1.5 text-sm font-medium text-red-500 hover:bg-red-50 hover:text-red-700 dark:hover:bg-red-950 min-h-[44px]"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
          </svg>
          Retirer
        </button>
      </div>
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Entreprise *</label>
          <input
            type="text"
            value={career.company}
            onChange={(e) => handleChange('company', e.target.value)}
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Poste *</label>
          <input
            type="text"
            value={career.position}
            onChange={(e) => handleChange('position', e.target.value)}
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Type de contrat</label>
          <select
            value={career.type_contrat || ''}
            onChange={(e) => handleChange('type_contrat', e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
          >
            <option value="">Sélectionner</option>
            {CONTRACT_TYPES.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Secteur</label>
          <select
            value={career.sector}
            onChange={(e) => handleChange('sector', e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
          >
            <option value="">Sélectionner</option>
            {SECTORS.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        {career.sector === 'Autre' && (
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Précisez votre secteur</label>
            <input
              type="text"
              value={career.custom_sector || ''}
              onChange={(e) => handleChange('custom_sector', e.target.value)}
              placeholder="Veuillez préciser votre secteur..."
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
            />
          </div>
        )}
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Tranche salariale</label>
          <input
            type="text"
            value={career.salary_range}
            onChange={(e) => handleChange('salary_range', e.target.value)}
            placeholder="Ex: 35k-45k EUR"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Ville de l'entreprise</label>
          <input
            type="text"
            value={career.ville || ''}
            onChange={(e) => handleChange('ville', e.target.value)}
            placeholder="Ex: Paris, Alger..."
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Pays de l'entreprise</label>
          <input
            type="text"
            value={career.pays || ''}
            onChange={(e) => handleChange('pays', e.target.value)}
            placeholder="Ex: France, Algérie..."
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Date de début</label>
          <input
            type="month"
            value={career.start_date}
            onChange={(e) => handleChange('start_date', e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Date de fin</label>
          <input
            type="month"
            value={career.end_date}
            onChange={(e) => handleChange('end_date', e.target.value)}
            disabled={career.is_current}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-100 disabled:text-gray-400 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100 dark:disabled:bg-slate-700 dark:disabled:text-slate-500"
          />
        </div>
        <div className="md:col-span-2">
          <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Description</label>
          <textarea
            value={career.description}
            onChange={(e) => handleChange('description', e.target.value)}
            rows={2}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
            placeholder="Description des missions..."
          />
        </div>
        <div className="md:col-span-2">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={career.is_current}
              onChange={(e) => {
                onChange(index, {
                  ...career,
                  is_current: e.target.checked,
                  end_date: e.target.checked ? '' : career.end_date,
                });
              }}
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700 dark:text-slate-300">Poste actuel</span>
          </label>
        </div>
      </div>
    </div>
  );
}

function CertificationForm({ cert, index, onChange, onRemove }) {
  const handleChange = (field, value) => {
    onChange(index, { ...cert, [field]: value });
  };

  return (
    <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-slate-600 dark:bg-slate-800/50">
      <div className="mb-3 flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700 dark:text-slate-300">
          Certification #{index + 1}
          {!cert.id && (
            <span className="ml-2 rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700 dark:bg-amber-950 dark:text-amber-300">
              Non sauvegardée
            </span>
          )}
        </span>
        <button
          type="button"
          onClick={() => onRemove(index)}
          title={cert.id ? 'Supprimer cette certification (enregistrée)' : 'Retirer cette certification du formulaire'}
          className="inline-flex items-center gap-1 rounded-lg px-3 py-1.5 text-sm font-medium text-red-500 hover:bg-red-50 hover:text-red-700 dark:hover:bg-red-950 min-h-[44px]"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
          </svg>
          Retirer
        </button>
      </div>
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        <div className="md:col-span-2">
          <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Nom de la certification *</label>
          <input
            type="text"
            value={cert.name}
            onChange={(e) => handleChange('name', e.target.value)}
            required
            placeholder="Ex: AWS Solutions Architect, PMP, Scrum Master..."
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Organisme émetteur</label>
          <input
            type="text"
            value={cert.issuer}
            onChange={(e) => handleChange('issuer', e.target.value)}
            placeholder="Ex: Amazon, PMI, Scrum.org..."
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Date d'obtention</label>
          <input
            type="month"
            value={cert.date_obtained}
            onChange={(e) => handleChange('date_obtained', e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
          />
        </div>
      </div>
    </div>
  );
}

export default function AlumniCareer() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [alumniId, setAlumniId] = useState(null);

  const [careers, setCareers] = useState([]);
  const [certifications, setCertifications] = useState([]);
  const [availabilityStatus, setAvailabilityStatus] = useState('');
  const [isAnonymised, setIsAnonymised] = useState(false);
  const [confirmTarget, setConfirmTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const storedId = localStorage.getItem('alumni_id');
        if (storedId) {
          setAlumniId(storedId);
          const [careersRes, certsRes, profileRes] = await Promise.all([
            careerAPI.getByAlumni(storedId).catch(() => ({ data: [] })),
            careerAPI.getCertifications(storedId).catch(() => ({ data: [] })),
            alumniAPI.getById(storedId).catch(() => ({ data: { availability_status: '', is_anonymised: false } })),
          ]);
          setCareers(careersRes.data || []);
          setCertifications(certsRes.data || []);
          setAvailabilityStatus(profileRes.data.availability_status || '');
          setIsAnonymised(Boolean(profileRes.data.is_anonymised));
        }
      } catch {
        setError('Impossible de charger votre parcours. Veuillez réessayer.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleCareerChange = (index, updatedCareer) => {
    setCareers((prev) => {
      const next = [...prev];
      next[index] = updatedCareer;
      return next;
    });
  };

  const addCareer = () => {
    if (isAnonymised) {
      setError('Votre compte est anonymisé (RGPD) : toute modification est impossible.');
      return;
    }
    setCareers((prev) => [...prev, { ...EMPTY_CAREER }]);
  };

  const removeCareer = (index) => {
    const career = careers[index];
    if (!career.id) {
      setCareers((prev) => prev.filter((_, i) => i !== index));
      return;
    }
    if (isAnonymised) {
      setError('Votre compte est anonymisé (RGPD) : la suppression est impossible.');
      return;
    }
    setConfirmTarget({
      type: 'career',
      index,
      id: career.id,
      label: `"${career.company || career.position || `Poste #${index + 1}`}"`,
    });
  };

  const handleCertChange = (index, updatedCert) => {
    setCertifications((prev) => {
      const next = [...prev];
      next[index] = updatedCert;
      return next;
    });
  };

  const addCertification = () => {
    if (isAnonymised) {
      setError('Votre compte est anonymisé (RGPD) : toute modification est impossible.');
      return;
    }
    setCertifications((prev) => [...prev, { ...EMPTY_CERTIFICATION }]);
  };

  const removeCertification = (index) => {
    const cert = certifications[index];
    if (!cert.id) {
      setCertifications((prev) => prev.filter((_, i) => i !== index));
      return;
    }
    if (isAnonymised) {
      setError('Votre compte est anonymisé (RGPD) : la suppression est impossible.');
      return;
    }
    setConfirmTarget({
      type: 'certification',
      index,
      id: cert.id,
      label: `"${cert.name || `Certification #${index + 1}`}"`,
    });
  };

  const confirmRemove = async () => {
    if (!confirmTarget || !alumniId) return;
    setDeleting(true);
    setError(null);
    try {
      if (confirmTarget.type === 'career') {
        await careerAPI.delete(alumniId, confirmTarget.id);
        setCareers((prev) => prev.filter((_, i) => i !== confirmTarget.index));
      } else {
        await careerAPI.deleteCertification(alumniId, confirmTarget.id);
        setCertifications((prev) => prev.filter((_, i) => i !== confirmTarget.index));
      }
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la suppression.');
    } finally {
      setDeleting(false);
      setConfirmTarget(null);
    }
  };

  const handleSaveCareers = async (e) => {
    e.preventDefault();
    if (!alumniId) return;
    if (isAnonymised) {
      setError('Votre compte est anonymisé (RGPD) : toute modification est impossible.');
      return;
    }
    setSaving(true);
    setError(null);
    setSuccess(false);
    const errors = [];

    try {
      const existingRes = await careerAPI.getByAlumni(alumniId);
      const existingCareers = existingRes.data || [];

      for (const career of existingCareers) {
        try {
          await careerAPI.delete(alumniId, career.id);
        } catch {
          errors.push(`Suppression poste "${career.company || career.position}" échouée`);
        }
      }

      for (const career of careers) {
        if (career.company && career.position) {
          try {
            const sectorToSend = career.sector === 'Autre' && career.custom_sector
              ? career.custom_sector
              : career.sector;
            await careerAPI.add(alumniId, { ...career, sector: sectorToSend });
          } catch {
            errors.push(`Ajout poste "${career.company}" échoué`);
          }
        }
      }

      const existingCertsRes = await careerAPI.getCertifications(alumniId).catch(() => ({ data: [] }));
      for (const cert of (existingCertsRes.data || [])) {
        try {
          await careerAPI.deleteCertification(alumniId, cert.id);
        } catch {
          errors.push(`Suppression certification "${cert.name}" échouée`);
        }
      }

      for (const cert of certifications) {
        if (cert.name) {
          try {
            await careerAPI.addCertification(alumniId, cert);
          } catch {
            errors.push(`Ajout certification "${cert.name}" échoué`);
          }
        }
      }

      const [refreshedCareersRes, refreshedCertsRes] = await Promise.all([
        careerAPI.getByAlumni(alumniId),
        careerAPI.getCertifications(alumniId).catch(() => ({ data: [] })),
      ]);
      setCareers(refreshedCareersRes.data || []);
      setCertifications(refreshedCertsRes.data || []);

      if (errors.length > 0) {
        setError(`${errors.length} opération(s) échouée(s) : ${errors.join('; ')}`);
      } else {
        setSuccess(true);
        setTimeout(() => setSuccess(false), 3000);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la sauvegarde du parcours.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <LoadingSpinner text="Chargement de votre parcours..." />;

  return (
    <>
    <form onSubmit={handleSaveCareers} className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-slate-100">Mon Parcours</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">
          Gérez votre parcours professionnel et vos certifications
        </p>
      </div>

      {error && <ErrorMessage message={error} onRetry={() => setError(null)} />}

      {isAnonymised && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-800 dark:bg-red-950">
          <p className="text-sm font-medium text-red-800 dark:text-red-200">
            Votre compte est anonymisé (RGPD) : l&apos;ajout, la modification et la suppression
            de postes ou de certifications ne sont plus possibles.
          </p>
        </div>
      )}

      {success && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-4 dark:border-green-900 dark:bg-green-950">
          <div className="flex items-center gap-2">
            <svg className="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
            </svg>
            <p className="text-sm font-medium text-green-800 dark:text-green-200">Parcours sauvegardé avec succès !</p>
          </div>
        </div>
      )}

      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">Parcours professionnel</h2>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={addCareer}
              className="inline-flex items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
              </svg>
              Ajouter
            </button>
          </div>
        </div>

        {careers.length > 0 && availabilityStatus === 'en_poste' && !careers.some((c) => c.is_current) && (
          <div className="mb-4 flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 p-4 dark:border-amber-800 dark:bg-amber-950">
            <svg className="mt-0.5 h-5 w-5 flex-shrink-0 text-amber-500" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-amber-800 dark:text-amber-200">Aucun poste coché comme « actuel »</p>
              <p className="mt-1 text-xs text-amber-700 dark:text-amber-300">
                Pour que votre poste correct s'affiche dans l'annuaire, cochez la case « Poste actuel »
                sur l'expérience correspondante. À défaut, c'est l'expérience la plus récente qui sera
                affichée automatiquement.
              </p>
            </div>
          </div>
        )}

        {careers.length === 0 ? (
          <div className="rounded-lg border border-dashed border-gray-300 bg-gray-50 py-10 text-center dark:border-slate-600 dark:bg-slate-800/50">
            <svg className="mx-auto h-10 w-10 text-gray-300" fill="none" viewBox="0 0 24 24" strokeWidth="1" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 0 0 .75-1.661V8.706c0-1.081-.768-2.015-1.837-2.175a48.114 48.114 0 0 0-3.413-.387m4.5 8.006c-.194.165-.42.295-.673.38A23.978 23.978 0 0 1 12 15.75c-2.648 0-5.195-.429-7.577-1.22a2.016 2.016 0 0 1-.673-.38m0 0A2.18 2.18 0 0 1 3 12.489V8.706c0-1.081.768-2.015 1.837-2.175a48.111 48.111 0 0 1 3.413-.387m7.5 0V5.25A2.25 2.25 0 0 0 13.5 3h-3a2.25 2.25 0 0 0-2.25 2.25v.894m7.5 0a48.667 48.667 0 0 0-7.5 0" />
            </svg>
            <p className="mt-2 text-sm text-gray-500 dark:text-slate-400">Aucun parcours enregistré</p>
            <p className="mt-1 text-xs text-gray-400 dark:text-slate-500">Ajoutez votre premier poste pour constituer votre historique</p>
          </div>
        ) : (
          <div className="space-y-4">
            {careers.map((career, idx) => (
              <CareerForm
                key={career.id ?? `nouveau-${idx}`}
                career={career}
                index={idx}
                onChange={handleCareerChange}
                onRemove={removeCareer}
              />
            ))}
          </div>
        )}
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">Certifications</h2>
          <button
            type="button"
            onClick={addCertification}
            className="inline-flex items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            Ajouter une certification
          </button>
        </div>

        {certifications.length === 0 ? (
          <div className="rounded-lg border border-dashed border-gray-300 bg-gray-50 py-10 text-center dark:border-slate-600 dark:bg-slate-800/50">
            <svg className="mx-auto h-10 w-10 text-gray-300" fill="none" viewBox="0 0 24 24" strokeWidth="1" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.62 48.62 0 0 1 12 20.904a48.62 48.62 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347m-15.482 0a50.636 50.636 0 0 0-2.658-.813A59.906 59.906 0 0 1 12 3.493a59.903 59.903 0 0 1 10.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.717 50.717 0 0 1 12 13.489a50.702 50.702 0 0 1 7.74-3.342" />
            </svg>
            <p className="mt-2 text-sm text-gray-500 dark:text-slate-400">Aucune certification enregistrée</p>
            <p className="mt-1 text-xs text-gray-400 dark:text-slate-500">Ajoutez vos certifications professionnelles</p>
          </div>
        ) : (
          <div className="space-y-4">
            {certifications.map((cert, idx) => (
              <CertificationForm
                key={cert.id ?? `nouvelle-${idx}`}
                cert={cert}
                index={idx}
                onChange={handleCertChange}
                onRemove={removeCertification}
              />
            ))}
          </div>
        )}
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={saving || isAnonymised}
          title={isAnonymised ? 'Compte anonymisé : modification impossible' : undefined}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700 disabled:opacity-50"
        >
          {saving ? (
            <>
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
              Sauvegarde en cours...
            </>
          ) : (
            <>
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
              </svg>
              Sauvegarder le parcours
            </>
          )}
        </button>
      </div>
    </form>

    {confirmTarget && (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={() => !deleting && setConfirmTarget(null)}>
        <div
          className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl dark:bg-slate-800"
          onClick={(e) => e.stopPropagation()}
          role="dialog"
          aria-modal="true"
        >
          <div className="flex items-start gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-red-100 dark:bg-red-950">
              <svg className="h-5 w-5 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
              </svg>
            </div>
            <div className="flex-1">
              <h2 className="text-lg font-bold text-gray-900 dark:text-slate-100">
                {confirmTarget.type === 'career' ? 'Supprimer ce poste' : 'Supprimer cette certification'}
              </h2>
              <p className="mt-2 text-sm text-gray-600 dark:text-slate-300">
                Supprimer définitivement {confirmTarget.label} ? Cette action est irréversible
                et sera immédiatement enregistrée côté serveur.
              </p>
            </div>
          </div>
          <div className="mt-6 flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setConfirmTarget(null)}
              disabled={deleting}
              className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 min-h-[44px]"
            >
              Annuler
            </button>
            <button
              type="button"
              onClick={confirmRemove}
              disabled={deleting}
              className="inline-flex items-center gap-2 rounded-lg bg-red-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50 min-h-[44px]"
            >
              {deleting ? (
                <>
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                  Suppression...
                </>
              ) : (
                'Supprimer définitivement'
              )}
            </button>
          </div>
        </div>
      </div>
    )}
    </>
  );
}
