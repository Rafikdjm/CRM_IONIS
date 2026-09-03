import { useState, useEffect } from 'react';
import { alumniAPI } from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';
import ErrorMessage from '../shared/ErrorMessage';

const AVAILABILITY_OPTIONS = [
  { value: 'en_poste', label: 'En poste' },
  { value: 'a_lecoute', label: "À l'écoute d'opportunités" },
  { value: 'en_recherche', label: 'En recherche active' },
];

export default function AlumniProfile() {
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
    availability_status: '',
    sector: '',
    id_promotion: null,
    date_naissance: '',
    email_academique: '',
    parcours_anterieur: '',
  });

  const [skills, setSkills] = useState([]);
  const [skillInput, setSkillInput] = useState('');

  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true);
      try {
        const storedId = localStorage.getItem('alumni_id');
        if (storedId) {
          setAlumniId(storedId);
          const res = await alumniAPI.getById(storedId);
          setProfile({
            first_name: res.data.first_name || '',
            last_name: res.data.last_name || '',
            email: res.data.email || '',
            phone: res.data.phone || '',
            address: res.data.address || '',
            city: res.data.city || '',
            country: res.data.country || '',
            linkedin: res.data.linkedin || '',
            availability_status: res.data.availability_status || '',
            sector: res.data.sector || '',
            id_promotion: res.data.id_promotion || null,
            date_naissance: res.data.date_naissance || '',
            email_academique: res.data.email_academique || '',
            parcours_anterieur: res.data.parcours_anterieur || '',
          });
          setSkills(res.data.skills || []);
        }
      } catch {
        setError('Impossible de charger votre profil. Veuillez réessayer.');
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfile((prev) => ({ ...prev, [name]: value }));
  };

  const addSkill = () => {
    const trimmed = skillInput.trim();
    if (trimmed && !skills.includes(trimmed)) {
      setSkills((prev) => [...prev, trimmed]);
      setSkillInput('');
    }
  };

  const removeSkill = (skillToRemove) => {
    setSkills((prev) => prev.filter((s) => s !== skillToRemove));
  };

  const handleSkillKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addSkill();
    }
  };

  const [availabilityError, setAvailabilityError] = useState(false);

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    if (!alumniId) {
      setError('Aucun profil identifié. Veuillez vous inscrire ou vous connecter d\'abord.');
      return;
    }
    if (!profile.availability_status) {
      setAvailabilityError(true);
      setError('Veuillez sélectionner un statut de disponibilité avant de sauvegarder.');
      return;
    }
    setAvailabilityError(false);
    setSaving(true);
    setError(null);
    setSuccess(false);
    try {
      const { ...profileData } = profile;
      await alumniAPI.partialUpdate(alumniId, {
        ...profileData,
        skills,
      });
      const refreshed = await alumniAPI.getById(alumniId);
      setProfile({
        first_name: refreshed.data.first_name || '',
        last_name: refreshed.data.last_name || '',
        email: refreshed.data.email || '',
        phone: refreshed.data.phone || '',
        address: refreshed.data.address || '',
        city: refreshed.data.city || '',
        country: refreshed.data.country || '',
        linkedin: refreshed.data.linkedin || '',
        availability_status: refreshed.data.availability_status || '',
        sector: refreshed.data.sector || '',
        id_promotion: refreshed.data.id_promotion || null,
        date_naissance: refreshed.data.date_naissance || '',
        email_academique: refreshed.data.email_academique || '',
        parcours_anterieur: refreshed.data.parcours_anterieur || '',
      });
      setSkills(refreshed.data.skills || []);
      if (refreshed.data.email) {
        localStorage.setItem('alumni_email', refreshed.data.email);
      }
      if (refreshed.data.first_name && refreshed.data.last_name) {
        localStorage.setItem('alumni_name', `${refreshed.data.first_name} ${refreshed.data.last_name}`);
      }
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(
        Array.isArray(detail) ? detail.map((d) => d.msg).join(', ') :
        detail || 'Erreur lors de la sauvegarde du profil.'
      );
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <LoadingSpinner text="Chargement de votre profil..." />;

  const inputClass = 'w-full max-w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100 sm:px-4';
  const labelClass = 'mb-1 block text-sm font-medium text-gray-700 dark:text-slate-300';

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-slate-100">Mon Profil</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">
          Mettez à jour vos informations personnelles et votre disponibilité
        </p>
      </div>

      {error && <ErrorMessage message={error} onRetry={() => setError(null)} />}

      {success && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-4 dark:border-green-900 dark:bg-green-950">
          <div className="flex items-center gap-2">
            <svg className="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
            </svg>
            <p className="text-sm font-medium text-green-800 dark:text-green-200">Profil sauvegardé avec succès !</p>
          </div>
        </div>
      )}

      <form onSubmit={handleSaveProfile} className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">Informations personnelles</h2>
          <button
            type="submit"
            disabled={saving}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 min-h-[44px]"
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
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 [&>*]:min-w-0">
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
          <div className="md:col-span-2">
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
          <div className="md:col-span-2">
            <label className={labelClass}>LinkedIn</label>
            <input type="url" name="linkedin" value={profile.linkedin} onChange={handleProfileChange} placeholder="https://linkedin.com/in/..." className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>Date de naissance</label>
            <input type="date" name="date_naissance" value={profile.date_naissance} onChange={handleProfileChange} className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>Email académique</label>
            <input type="email" name="email_academique" value={profile.email_academique} onChange={handleProfileChange} placeholder="prenom.nom@ionis-stm.com" className={inputClass} />
          </div>
          <div className="md:col-span-2">
            <label className={labelClass}>Parcours antérieur</label>
            <textarea
              name="parcours_anterieur"
              value={profile.parcours_anterieur}
              onChange={handleProfileChange}
              rows={2}
              placeholder="Formation initiale, école précédente..."
              className={inputClass}
            />
          </div>
          {profile.availability_status === 'en_poste' && (
            <div className="md:col-span-2">
              <label className={labelClass}>Secteur d'activité</label>
              {profile.sector ? (
                <div className="rounded-lg border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm text-gray-700 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-300">
                  {profile.sector}
                </div>
              ) : (
                <div className="rounded-lg border border-dashed border-gray-300 bg-gray-50 px-4 py-3 dark:border-slate-600 dark:bg-slate-800/50">
                  <p className="text-sm text-gray-500 dark:text-slate-400">
                    Non renseigné — ajoutez un poste actuel dans votre{' '}
                    <span className="font-medium text-gray-700 dark:text-slate-300">parcours professionnel</span>{' '}
                    pour que le secteur soit déduit automatiquement.
                  </p>
                </div>
              )}
              <p className="mt-1 text-xs text-gray-400 dark:text-slate-500">
                Le secteur est automatiquement défini par votre expérience professionnelle actuelle.
              </p>
            </div>
          )}
        </div>
      </form>

      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-slate-100">
          Statut de disponibilité <span className="text-red-500">*</span>
        </h2>
        <div className="space-y-3">
          {AVAILABILITY_OPTIONS.map((option) => (
            <label key={option.value} className="flex items-center gap-3 rounded-lg border border-gray-200 px-4 py-3 cursor-pointer hover:bg-gray-50 transition dark:border-slate-600 dark:hover:bg-slate-700/50">
              <input
                type="radio"
                name="availability_status"
                value={option.value}
                checked={profile.availability_status === option.value}
                onChange={(e) => {
                  handleProfileChange(e);
                  setAvailabilityError(false);
                }}
                className="h-4 w-4 border-gray-300 text-emerald-600 focus:ring-emerald-500"
              />
              <span className="text-sm font-medium text-gray-700 dark:text-slate-300">{option.label}</span>
            </label>
          ))}
        </div>
        {availabilityError && !profile.availability_status && (
          <p className="mt-3 text-sm text-red-600 dark:text-red-400">
            Ce champ est obligatoire. Veuillez choisir une option.
          </p>
        )}
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-slate-100">Tags de compétences</h2>
        <p className="mb-3 text-sm text-gray-500 dark:text-slate-400">
          Ajoutez des mots-clés pour décrire vos compétences (ex: Python, Marketing, Management)
        </p>
        <div className="flex gap-2">
          <input
            type="text"
            value={skillInput}
            onChange={(e) => setSkillInput(e.target.value)}
            onKeyDown={handleSkillKeyDown}
            placeholder="Tapez une compétence et appuyez sur Entrée"
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
          />
          <button
            type="button"
            onClick={addSkill}
            disabled={!skillInput.trim()}
            className="inline-flex items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 min-h-[44px]"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            Ajouter
          </button>
        </div>
        {skills.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {skills.map((skill) => (
              <span
                key={skill}
                className="inline-flex items-center gap-1.5 rounded-full bg-blue-100 dark:bg-blue-900 px-3 py-1 text-sm font-medium text-blue-800 dark:text-blue-200"
              >
                {skill}
                <button
                  type="button"
                  onClick={() => removeSkill(skill)}
                  className="inline-flex h-8 w-8 items-center justify-center rounded-full text-blue-600 dark:text-blue-400 hover:bg-blue-200 dark:hover:bg-blue-800 hover:text-blue-900 dark:hover:text-blue-100 min-h-[44px] min-w-[44px]"
                >
                  <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
                  </svg>
                </button>
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
