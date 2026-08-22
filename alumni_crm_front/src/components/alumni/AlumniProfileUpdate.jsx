import { useState, useEffect } from 'react';
import { alumniAPI, careerAPI } from '../../services/api';
import { SECTORS } from '../../constants';
import LoadingSpinner from '../shared/LoadingSpinner';
import ErrorMessage from '../shared/ErrorMessage';

const SALARY_RANGES = [
  { label: 'Non renseigné', value: '' },
  { label: '< 20 000 €', value: '15000' },
  { label: '20 000 - 25 000 €', value: '22500' },
  { label: '25 000 - 30 000 €', value: '27500' },
  { label: '30 000 - 35 000 €', value: '32500' },
  { label: '35 000 - 40 000 €', value: '37500' },
  { label: '40 000 - 45 000 €', value: '42500' },
  { label: '45 000 - 50 000 €', value: '47500' },
  { label: '50 000 - 60 000 €', value: '55000' },
  { label: '60 000 - 70 000 €', value: '65000' },
  { label: '70 000 - 80 000 €', value: '75000' },
  { label: '> 80 000 €', value: '85000' },
];

const EMPTY_CAREER = {
  company: '',
  position: '',
  sector: '',
  custom_sector: '',
  start_date: '',
  end_date: '',
  salary_range: '',
  is_current: false,
  description: '',
  pays: '',
  ville: '',
};

function CareerForm({ career, index, onChange, onRemove, canRemove }) {
  const handleChange = (field, value) => {
    onChange(index, { ...career, [field]: value });
  };

  return (
    <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-slate-700 dark:bg-slate-700/50">
      <div className="mb-3 flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700 dark:text-slate-300">
          {career.is_current ? 'Poste actuel' : `Poste #${index + 1}`}
        </span>
        {canRemove && (
          <button
            type="button"
            onClick={() => onRemove(index)}
            className="text-sm text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
          >
            Supprimer
          </button>
        )}
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
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
          <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Secteur</label>
          <select
            value={career.sector}
            onChange={(e) => {
              const val = e.target.value;
              onChange(index, { ...career, sector: val, custom_sector: val !== 'Autre' ? '' : career.custom_sector });
            }}
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
          <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Tranche salariale annuelle (brut)</label>
          <select
            value={career.salary_range}
            onChange={(e) => handleChange('salary_range', e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
          >
            {SALARY_RANGES.map((r) => (
              <option key={r.value} value={r.value}>{r.label}</option>
            ))}
          </select>
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
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-100 disabled:text-gray-400 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100 dark:disabled:bg-slate-800 dark:disabled:text-slate-500"
          />
        </div>
        <div className="sm:col-span-2">
          <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Description</label>
          <textarea
            value={career.description}
            onChange={(e) => handleChange('description', e.target.value)}
            rows={2}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
            placeholder="Description des missions..."
          />
        </div>
        <div className="sm:col-span-2">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={career.is_current}
              onChange={(e) => {
                handleChange('is_current', e.target.checked);
                if (e.target.checked) handleChange('end_date', '');
              }}
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-800"
            />
            <span className="text-sm text-gray-700 dark:text-slate-300">Poste actuel</span>
          </label>
        </div>
      </div>
    </div>
  );
}

export default function AlumniProfileUpdate() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [alumniId, setAlumniId] = useState(null);

  const [profile, setProfile] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    country: '',
    linkedin: '',
  });

  const [careers, setCareers] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const storedId = localStorage.getItem('alumni_id');
        if (storedId) {
          setAlumniId(storedId);
          const [profileRes, careersRes] = await Promise.all([
            alumniAPI.getById(storedId),
            careerAPI.getByAlumni(storedId).catch(() => ({ data: [] })),
          ]);
          setProfile({
            first_name: profileRes.data.first_name || '',
            last_name: profileRes.data.last_name || '',
            email: profileRes.data.email || '',
            phone: profileRes.data.phone || '',
            address: profileRes.data.address || '',
            city: profileRes.data.city || '',
            country: profileRes.data.country || '',
            linkedin: profileRes.data.linkedin || '',
          });
          setCareers(careersRes.data || []);
        }
      } catch {
        setError('Impossible de charger votre profil. Veuillez réessayer.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfile((prev) => ({ ...prev, [name]: value }));
  };

  const handleCareerChange = (index, updatedCareer) => {
    setCareers((prev) => {
      const next = [...prev];
      next[index] = updatedCareer;
      return next;
    });
  };

  const addCareer = () => {
    setCareers((prev) => [...prev, { ...EMPTY_CAREER }]);
  };

  const removeCareer = (index) => {
    setCareers((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSaveProfile = async () => {
    if (!alumniId) return;
    setSaving(true);
    setError(null);
    try {
      await alumniAPI.partialUpdate(alumniId, profile);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la sauvegarde du profil.');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveCareers = async () => {
    if (!alumniId) return;
    setSaving(true);
    setError(null);
    try {
      const existingRes = await careerAPI.getByAlumni(alumniId);

      for (const career of existingRes.data || []) {
        await careerAPI.delete(alumniId, career.id);
      }

      for (const career of careers) {
        if (career.company && career.position) {
          const sectorToSend = career.sector === 'Autre' && career.custom_sector
            ? career.custom_sector
            : career.sector;
          await careerAPI.add(alumniId, { ...career, sector: sectorToSend });
        }
      }

      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la sauvegarde du parcours.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <LoadingSpinner text="Chargement de votre profil..." />;

  const inputClass = 'w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100';
  const labelClass = 'mb-1 block text-sm font-medium text-gray-700 dark:text-slate-300';

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-slate-100">Mon Profil</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">
          Mettez à jour vos informations personnelles et votre parcours professionnel
        </p>
      </div>

      {error && <ErrorMessage message={error} onRetry={() => setError(null)} />}

      {success && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-4 dark:border-green-800 dark:bg-green-950">
          <div className="flex items-center gap-2">
            <svg className="h-5 w-5 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
            </svg>
            <p className="text-sm font-medium text-green-800 dark:text-green-300">Sauvegarde réussie !</p>
          </div>
        </div>
      )}

      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">Informations personnelles</h2>
          <button
            onClick={handleSaveProfile}
            disabled={saving}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? (
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
            ) : (
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
              </svg>
            )}
            Sauvegarder
          </button>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className={labelClass}>Prénom</label>
            <input type="text" name="first_name" value={profile.first_name} onChange={handleProfileChange} className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>Nom</label>
            <input type="text" name="last_name" value={profile.last_name} onChange={handleProfileChange} className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>Email</label>
            <input type="email" name="email" value={profile.email} onChange={handleProfileChange} className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>Téléphone</label>
            <input type="tel" name="phone" value={profile.phone} onChange={handleProfileChange} className={inputClass} />
          </div>
          <div className="sm:col-span-2">
            <label className={labelClass}>Adresse</label>
            <input type="text" name="address" value={profile.address} onChange={handleProfileChange} className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>Ville</label>
            <input type="text" name="city" value={profile.city} onChange={handleProfileChange} className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>Pays</label>
            <input type="text" name="country" value={profile.country} onChange={handleProfileChange} className={inputClass} />
          </div>
          <div className="sm:col-span-2">
            <label className={labelClass}>LinkedIn</label>
            <input type="url" name="linkedin" value={profile.linkedin} onChange={handleProfileChange} placeholder="https://linkedin.com/in/..." className={inputClass} />
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">Parcours professionnel</h2>
          <div className="flex gap-2">
            <button
              onClick={addCareer}
              className="inline-flex items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
              </svg>
              Ajouter
            </button>
            <button
              onClick={handleSaveCareers}
              disabled={saving}
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? (
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
              ) : (
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                </svg>
              )}
              Sauvegarder le parcours
            </button>
          </div>
        </div>

        {careers.length === 0 ? (
          <div className="rounded-lg border border-dashed border-gray-300 bg-gray-50 py-10 text-center dark:border-slate-600 dark:bg-slate-700/50">
            <svg className="mx-auto h-10 w-10 text-gray-300 dark:text-slate-500" fill="none" viewBox="0 0 24 24" strokeWidth="1" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 0 0 .75-1.661V8.706c0-1.081-.768-2.015-1.837-2.175a48.114 48.114 0 0 0-3.413-.387m4.5 8.006c-.194.165-.42.295-.673.38A23.978 23.978 0 0 1 12 15.75c-2.648 0-5.195-.429-7.577-1.22a2.016 2.016 0 0 1-.673-.38m0 0A2.18 2.18 0 0 1 3 12.489V8.706c0-1.081.768-2.015 1.837-2.175a48.111 48.111 0 0 1 3.413-.387m7.5 0V5.25A2.25 2.25 0 0 0 13.5 3h-3a2.25 2.25 0 0 0-2.25 2.25v.894m7.5 0a48.667 48.667 0 0 0-7.5 0" />
            </svg>
            <p className="mt-2 text-sm text-gray-500 dark:text-slate-400">Aucun parcours enregistré</p>
            <p className="mt-1 text-xs text-gray-400 dark:text-slate-500">Ajoutez votre premier poste pour constituer votre historique</p>
          </div>
        ) : (
          <div className="space-y-4">
            {careers.map((career, idx) => (
              <CareerForm
                key={idx}
                career={career}
                index={idx}
                onChange={handleCareerChange}
                onRemove={removeCareer}
                canRemove={careers.length > 1}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
