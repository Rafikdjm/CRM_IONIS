import { useState, useEffect } from 'react';
import { alumniAPI, promotionsAPI, apiErrorMessage } from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';

const AVAILABILITY_STATUSES = [
  { value: 'en_poste', label: 'En poste' },
  { value: 'a_lecoute', label: "À l'écoute d'opportunités" },
  { value: 'en_recherche', label: 'En recherche active' },
];

export default function AlumniEditModal({ alumniId, onClose, onSaved }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [promotions, setPromotions] = useState([]);
  const [form, setForm] = useState(null);

  useEffect(() => {
    if (!alumniId) return;
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const [profileRes, promoRes] = await Promise.all([
          alumniAPI.getById(alumniId),
          promotionsAPI.getAll().catch(() => ({ data: [] })),
        ]);
        if (cancelled) return;
        const profile = profileRes.data;
        setPromotions(promoRes.data || []);
        setForm({
          last_name: profile.last_name || '',
          first_name: profile.first_name || '',
          email: profile.email || '',
          phone: profile.phone || '',
          date_naissance: profile.date_naissance || '',
          date_inscription: profile.date_inscription || '',
          parcours_anterieur: profile.parcours_anterieur || '',
          id_promotion: profile.id_promotion != null ? String(profile.id_promotion) : '',
          email_academique: profile.email_academique || '',
          address: profile.address || '',
          city: profile.city || '',
          country: profile.country || '',
          linkedin: profile.linkedin || '',
          sector: profile.sector || '',
          availability_status: profile.availability_status || 'en_poste',
          skills: Array.isArray(profile.skills) ? profile.skills.join(', ') : '',
        });
      } catch {
        if (!cancelled) setError('Erreur lors du chargement de la fiche.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => { cancelled = true; };
  }, [alumniId]);

  useEffect(() => {
    const handleKey = (e) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [onClose]);

  const setField = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    if (!form) return;
    const last_name = form.last_name.trim();
    const first_name = form.first_name.trim();
    const email = form.email.trim();
    if (!last_name || !first_name || !email) {
      setError('Les champs nom, prénom et email sont obligatoires.');
      return;
    }
    if (!form.id_promotion) {
      setError('La promotion est obligatoire.');
      return;
    }

    const skills = form.skills
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);

    setSaving(true);
    setError(null);
    try {
      await alumniAPI.update(alumniId, {
        ...form,
        last_name,
        first_name,
        email: email.toLowerCase(),
        skills,
        id_promotion: Number(form.id_promotion),
      });
      onSaved?.();
      onClose();
    } catch (err) {
      setError(apiErrorMessage(err, 'Erreur lors de la sauvegarde.'));
    } finally {
      setSaving(false);
    }
  };

  if (!alumniId) return null;

  const inputClass = 'w-full max-w-full rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none';
  const labelClass = 'block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" role="dialog" aria-modal="true">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />

      <div className="relative z-10 flex max-h-[90vh] w-full max-w-2xl flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-2xl dark:border-slate-700 dark:bg-slate-800">
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4 dark:border-slate-700">
          <h2 className="text-lg font-bold text-gray-900 dark:text-slate-100">Modifier l&apos;étudiant</h2>
          <button
            onClick={onClose}
            className="flex h-11 w-11 items-center justify-center rounded-lg text-gray-400 transition hover:bg-gray-200 hover:text-gray-600 dark:hover:bg-slate-700 dark:hover:text-slate-300"
            aria-label="Fermer"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-5">
          {loading ? (
            <div className="py-12"><LoadingSpinner text="Chargement de la fiche..." /></div>
          ) : error && !form ? (
            <div className="py-12 text-center text-sm text-red-500 dark:text-red-400">{error}</div>
          ) : form ? (
            <>
              {error && (
                <div className="mb-4 rounded-lg bg-red-50 dark:bg-red-950/60 p-3 text-sm text-red-700 dark:text-red-300">
                  {error}
                </div>
              )}
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 [&>*]:min-w-0">
                <div>
                  <label className={labelClass}>Nom *</label>
                  <input type="text" value={form.last_name} onChange={(e) => setField('last_name', e.target.value)} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>Prénom *</label>
                  <input type="text" value={form.first_name} onChange={(e) => setField('first_name', e.target.value)} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>Email *</label>
                  <input type="email" value={form.email} onChange={(e) => setField('email', e.target.value)} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>Email académique</label>
                  <input type="email" value={form.email_academique} onChange={(e) => setField('email_academique', e.target.value)} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>Téléphone</label>
                  <input type="text" value={form.phone} onChange={(e) => setField('phone', e.target.value)} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>Date de naissance</label>
                  <input type="date" value={form.date_naissance} onChange={(e) => setField('date_naissance', e.target.value)} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>Date d'inscription</label>
                  <input type="date" value={form.date_inscription} onChange={(e) => setField('date_inscription', e.target.value)} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>Promotion *</label>
                  <select value={form.id_promotion} onChange={(e) => setField('id_promotion', e.target.value)} className={inputClass}>
                    <option value="">Sélectionner...</option>
                    {promotions.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name} ({p.year})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className={labelClass}>Statut de disponibilité *</label>
                  <select value={form.availability_status} onChange={(e) => setField('availability_status', e.target.value)} className={inputClass}>
                    {AVAILABILITY_STATUSES.map((s) => (
                      <option key={s.value} value={s.value}>{s.label}</option>
                    ))}
                  </select>
                </div>
                <div className="md:col-span-2">
                  <label className={labelClass}>Secteur d'activité</label>
                  <div className="rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-700 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-300">
                    {form.sector || <span className="text-gray-400 dark:text-slate-500 italic">Non renseigné</span>}
                  </div>
                  <p className="mt-1 text-xs text-gray-400 dark:text-slate-500">
                    Déduit automatiquement de l'expérience professionnelle actuelle.
                  </p>
                </div>
                <div>
                  <label className={labelClass}>Compétences (séparées par des virgules)</label>
                  <input type="text" value={form.skills} onChange={(e) => setField('skills', e.target.value)} className={inputClass} placeholder="Ex : Python, SQL, Data Analysis" />
                </div>
                <div>
                  <label className={labelClass}>Ville</label>
                  <input type="text" value={form.city} onChange={(e) => setField('city', e.target.value)} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>Pays</label>
                  <input type="text" value={form.country} onChange={(e) => setField('country', e.target.value)} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>LinkedIn</label>
                  <input type="text" value={form.linkedin} onChange={(e) => setField('linkedin', e.target.value)} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>Adresse</label>
                  <input type="text" value={form.address} onChange={(e) => setField('address', e.target.value)} className={inputClass} />
                </div>
                <div className="md:col-span-2">
                  <label className={labelClass}>Parcours antérieur</label>
                  <input type="text" value={form.parcours_anterieur} onChange={(e) => setField('parcours_anterieur', e.target.value)} className={inputClass} />
                </div>
              </div>
            </>
          ) : null}
        </div>

        <div className="flex justify-end gap-2 border-t border-gray-200 px-6 py-3 dark:border-slate-700">
          <button
            onClick={onClose}
            className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 min-h-[44px]"
          >
            Annuler
          </button>
          <button
            onClick={handleSave}
            disabled={saving || loading || !form}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50 min-h-[44px]"
          >
            {saving ? (
              <>
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                Sauvegarde...
              </>
            ) : (
              'Enregistrer'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
