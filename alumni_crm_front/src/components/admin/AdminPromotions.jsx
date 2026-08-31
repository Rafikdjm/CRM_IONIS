import { useState, useEffect } from 'react';
import { promotionsAPI } from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';
import ErrorMessage from '../shared/ErrorMessage';

const EMPTY_FORM = { nom_promotion: '', annee_diplome: '', filiere: '' };

export default function AdminPromotions() {
  const [promotions, setPromotions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [formOpen, setFormOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState({ ...EMPTY_FORM });
  const [saving, setSaving] = useState(false);

  const [cascade, setCascade] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const fetchPromotions = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await promotionsAPI.getAll();
      setPromotions(res.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors du chargement des promotions.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchPromotions(); }, []);

  const openCreate = () => {
    setEditingId(null);
    setForm({ ...EMPTY_FORM });
    setFormOpen(true);
  };

  const openEdit = (p) => {
    setEditingId(p.id);
    setForm({
      nom_promotion: p.name || '',
      annee_diplome: p.year || '',
      filiere: p.filiere || '',
    });
    setFormOpen(true);
  };

  const closeForm = () => {
    setFormOpen(false);
    setEditingId(null);
    setForm({ ...EMPTY_FORM });
  };

  const handleSave = async () => {
    const nom = form.nom_promotion.trim();
    const filiere = form.filiere.trim();
    const annee = Number(form.annee_diplome);

    if (!nom || !filiere || form.annee_diplome === '') {
      setError('Tous les champs sont obligatoires.');
      return;
    }
    if (!Number.isInteger(annee) || annee < 1950 || annee > 2100) {
      setError("L'année de diplôme doit être un entier compris entre 1950 et 2100.");
      return;
    }

    setSaving(true);
    setError(null);
    try {
      const payload = { nom_promotion: nom, annee_diplome: annee, filiere };
      if (editingId) {
        await promotionsAPI.update(editingId, payload);
      } else {
        await promotionsAPI.create(payload);
      }
      closeForm();
      await fetchPromotions();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la sauvegarde.');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (p) => {
    if (!window.confirm(`Supprimer la promotion "${p.name}" ?`)) return;
    setError(null);
    try {
      await promotionsAPI.remove(p.id);
      await fetchPromotions();
    } catch (err) {
      if (err.response?.status === 409) {
        const detail = String(err.response?.data?.detail || '');
        const countMatch = detail.match(/: (\d+) \u00e9tudiant/);
        const nbEtudiants = countMatch ? parseInt(countMatch[1], 10) : (p.nb_etudiants || 0);
        setCascade({ id: p.id, name: p.name, nb_etudiants: nbEtudiants });
      } else {
        setError(err.response?.data?.detail || 'Erreur lors de la suppression.');
      }
    }
  };

  const confirmCascadeDelete = async () => {
    if (!cascade) return;
    setDeleting(true);
    setError(null);
    try {
      await promotionsAPI.remove(cascade.id, true);
      setCascade(null);
      await fetchPromotions();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la suppression.');
      setCascade(null);
    } finally {
      setDeleting(false);
    }
  };

  if (loading) return <LoadingSpinner text="Chargement des promotions..." />;

  const inputClass = 'w-full rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none';
  const labelClass = 'block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1';

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="mb-3 inline-flex h-1 w-12 rounded-full bg-gradient-to-r from-blue-600 to-indigo-500" />
          <h1 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-slate-100 sm:text-3xl">Promotions</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">
            Gérez promotions, filières et années de diplôme
          </p>
        </div>
        <button
          onClick={openCreate}
          className="inline-flex shrink-0 items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-blue-700 min-h-[44px]"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          Ajouter une promotion
        </button>
      </div>

      {error && <ErrorMessage message={error} onRetry={() => setError(null)} />}

      {/* MODAL CREATION / MODIFICATION */}
      {formOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={closeForm}>
          <div
            className="w-full max-w-md rounded-2xl bg-white dark:bg-slate-800 p-6 shadow-xl"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-gray-900 dark:text-slate-100">
                {editingId ? 'Modifier la promotion' : 'Ajouter une promotion'}
              </h2>
              <button onClick={closeForm} className="rounded-lg p-2 text-gray-400 dark:text-slate-500 hover:bg-gray-100 dark:hover:bg-slate-700 min-h-[44px] min-w-[44px]">
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className={labelClass}>Nom de la promotion *</label>
                <input
                  type="text"
                  value={form.nom_promotion}
                  onChange={(e) => setForm((p) => ({ ...p, nom_promotion: e.target.value }))}
                  placeholder="Ex : MSc Data Science"
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Année de diplôme *</label>
                <input
                  type="number"
                  min="1950"
                  max="2100"
                  value={form.annee_diplome}
                  onChange={(e) => setForm((p) => ({ ...p, annee_diplome: e.target.value }))}
                  placeholder="Ex : 2026"
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Filière *</label>
                <input
                  type="text"
                  value={form.filiere}
                  onChange={(e) => setForm((p) => ({ ...p, filiere: e.target.value }))}
                  placeholder="Ex : Informatique"
                  className={inputClass}
                />
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-2">
              <button
                onClick={closeForm}
                className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 min-h-[44px]"
              >
                Annuler
              </button>
              <button
                onClick={handleSave}
                disabled={saving}
                className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50 min-h-[44px]"
              >
                {saving ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                    Sauvegarde...
                  </>
                ) : (
                  editingId ? 'Enregistrer les modifications' : 'Créer la promotion'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL SUPPRESSION EN CASCADE */}
      {cascade && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={() => setCascade(null)}>
          <div
            className="w-full max-w-md rounded-2xl bg-white dark:bg-slate-800 p-6 shadow-xl"
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
                <h2 className="text-lg font-bold text-gray-900 dark:text-slate-100">Suppression en cascade</h2>
                <p className="mt-2 text-sm text-gray-600 dark:text-slate-300">
                  La promotion <span className="font-semibold">{cascade.name}</span> compte{' '}
                  <span className="font-semibold">{cascade.nb_etudiants}</span> étudiant(s) rattaché(s).
                </p>
                <div className="mt-3 rounded-lg bg-red-50 dark:bg-red-950/60 p-3 text-sm text-red-700 dark:text-red-300">
                  La promotion <span className="font-semibold">{cascade.name}</span> compte{' '}
                  <span className="font-semibold">{cascade.nb_etudiants}</span> étudiant(s) rattaché(s).
                  La supprimer supprimera <span className="font-semibold">définitivement</span>{' '}
                  {cascade.nb_etudiants === 1 ? 'cet étudiant' : 'ces étudiants'} et toutes leurs données liées.
                  Cette action est <span className="font-semibold">irréversible</span>.
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-2">
              <button
                onClick={() => setCascade(null)}
                className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 min-h-[44px]"
              >
                Annuler
              </button>
              <button
                onClick={confirmCascadeDelete}
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

      {/* LISTE DES PROMOTIONS */}
      {promotions.length === 0 ? (
        <div className="rounded-xl border border-dashed border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-800 p-12 text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400 dark:text-slate-500" fill="none" viewBox="0 0 24 24" strokeWidth="1" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.62 48.62 0 0 1 12 20.904a48.62 48.62 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347m-15.482 0a50.636 50.636 0 0 0-2.658-.813A59.906 59.906 0 0 1 12 3.493a59.903 59.903 0 0 1 10.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.717 50.717 0 0 1 12 13.489a50.702 50.702 0 0 1 7.74-3.342" />
          </svg>
          <h3 className="mt-4 text-sm font-semibold text-gray-900 dark:text-slate-100">Aucune promotion</h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">Créez votre première promotion pour rattacher vos alumni.</p>
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-slate-700 dark:bg-slate-800 shadow-sm">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-slate-700">
              <thead className="bg-gray-50 dark:bg-slate-700/50">
                <tr>
                  {[
                    { key: 'name', label: 'Promotion' },
                    { key: 'year', label: 'Année de diplôme' },
                    { key: 'filiere', label: 'Filière' },
                    { key: 'nb_etudiants', label: 'Étudiants' },
                    { key: 'actions', label: 'Actions' },
                  ].map((col) => (
                    <th
                      key={col.key}
                      className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-slate-400"
                    >
                      {col.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white dark:divide-slate-700 dark:bg-slate-800">
                {promotions.map((p) => (
                  <tr key={p.id} className="transition hover:bg-gray-50 dark:hover:bg-slate-700/50">
                    <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-gray-900 dark:text-slate-100">
                      {p.name}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-700 dark:text-slate-300">
                      {p.year}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3">
                      {p.filiere ? (
                        <span className="inline-flex items-center rounded-full bg-blue-50 dark:bg-blue-900 px-2 py-1 text-xs font-medium text-blue-700 dark:text-blue-300">
                          {p.filiere}
                        </span>
                      ) : (
                        <span className="text-gray-400 dark:text-slate-500">-</span>
                      )}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3">
                      <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                        p.nb_etudiants > 0
                          ? 'bg-emerald-50 dark:bg-emerald-900 text-emerald-700 dark:text-emerald-300'
                          : 'bg-gray-100 dark:bg-slate-700 text-gray-500 dark:text-slate-400'
                      }`}>
                        {p.nb_etudiants}
                      </span>
                    </td>
                    <td className="whitespace-nowrap px-4 py-3">
                      <div className="flex gap-2">
                        <button
                          onClick={() => openEdit(p)}
                          className="inline-flex items-center gap-1 rounded-lg border border-blue-200 bg-blue-50 dark:bg-blue-950 px-3 py-2 text-xs font-medium text-blue-700 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900 min-h-[44px]"
                        >
                          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
                          </svg>
                          Modifier
                        </button>
                        <button
                          onClick={() => handleDelete(p)}
                          className="inline-flex items-center gap-1 rounded-lg border border-red-200 bg-red-50 dark:bg-red-950 px-3 py-2 text-xs font-medium text-red-600 hover:bg-red-100 dark:hover:bg-red-950 min-h-[44px]"
                        >
                          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                          </svg>
                          Supprimer
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
