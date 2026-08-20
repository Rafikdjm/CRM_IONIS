import { useState, useEffect } from 'react';
import { questionnaireAPI } from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';
import ErrorMessage from '../shared/ErrorMessage';

const EMPTY_QUESTION = { id_question: null, texte: '', type: 'text', options: [], ordre: 0, tag: '', conditionnee_statut_emploi: false };

function OptionsEditor({ options, onChange }) {
  const [newOption, setNewOption] = useState('');

  const addOption = () => {
    const trimmed = newOption.trim();
    if (!trimmed) return;
    onChange([...(options || []), trimmed]);
    setNewOption('');
  };

  const removeOption = (idx) => {
    onChange((options || []).filter((_, i) => i !== idx));
  };

  const updateOption = (idx, value) => {
    const updated = [...(options || [])];
    updated[idx] = value;
    onChange(updated);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addOption();
    }
  };

  return (
    <div className="space-y-2">
      {(options || []).map((opt, idx) => (
        <div key={idx} className="flex items-center gap-2">
          <input
            type="text"
            value={opt}
            onChange={(e) => updateOption(idx, e.target.value)}
            className="flex-1 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100 px-3 py-1.5 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
          />
          <button
            type="button"
            onClick={() => removeOption(idx)}
            className="inline-flex items-center justify-center rounded-lg p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-950 transition-colors min-h-[44px] min-w-[44px]"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      ))}
      <div className="flex items-center gap-2">
        <input
          type="text"
          value={newOption}
          onChange={(e) => setNewOption(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ajouter une option..."
          className="flex-1 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100 px-3 py-1.5 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
        />
        <button
          type="button"
          onClick={addOption}
          className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-2.5 py-1.5 text-sm font-medium text-white hover:bg-blue-700 transition-colors min-h-[44px] min-w-[44px]"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
        </button>
      </div>
      {(!options || options.length === 0) && (
        <p className="text-xs text-gray-400 dark:text-slate-500">Aucune option ajoutee. Cliquez "+" ou tapez et appuyez Entree.</p>
      )}
    </div>
  );
}

export default function AdminQuestionnaires() {
  const [questionnaires, setQuestionnaires] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreate, setShowCreate] = useState(false);
  const [creating, setCreating] = useState(false);
  const [viewingResponses, setViewingResponses] = useState(null);
  const [responsesData, setResponsesData] = useState(null);
  const [loadingResponses, setLoadingResponses] = useState(false);
  const [editingId, setEditingId] = useState(null);

  const [form, setForm] = useState({ titre: '', description: '', questions: [{ ...EMPTY_QUESTION }] });

  const fetchQuestionnaires = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await questionnaireAPI.listAll();
      setQuestionnaires(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors du chargement.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchQuestionnaires(); }, []);

  const addQuestion = () => {
    setForm((prev) => ({
      ...prev,
      questions: [...prev.questions, { ...EMPTY_QUESTION, ordre: prev.questions.length }],
    }));
  };

  const updateQuestion = (index, field, value) => {
    setForm((prev) => ({
      ...prev,
      questions: prev.questions.map((q, i) => (i === index ? { ...q, [field]: value } : q)),
    }));
  };

  const removeQuestion = (index) => {
    setForm((prev) => ({
      ...prev,
      questions: prev.questions.filter((_, i) => i !== index).map((q, i) => ({ ...q, ordre: i })),
    }));
  };

  const resetForm = () => {
    setForm({ titre: '', description: '', questions: [{ ...EMPTY_QUESTION }] });
    setEditingId(null);
    setShowCreate(false);
  };

  const startEdit = async (q) => {
    setError(null);
    try {
      const res = await questionnaireAPI.getDetail(q.id_questionnaire);
      const detail = res.data;
      setForm({
        titre: detail.titre,
        description: detail.description || '',
        questions: (detail.questions || []).map((question, i) => ({
          id_question: question.id_question,
          texte: question.texte,
          type: question.type,
          options: question.options || [],
          ordre: question.ordre ?? i,
          tag: question.tag || '',
        })),
      });
      setEditingId(q.id_questionnaire);
      setShowCreate(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors du chargement du questionnaire.');
    }
  };

  const handleCreate = async () => {
    if (!form.titre.trim()) {
      setError('Le titre est obligatoire.');
      return;
    }
    if (form.questions.length === 0) {
      setError('Ajoutez au moins une question.');
      return;
    }
    const empty = form.questions.find((q) => !q.texte.trim());
    if (empty) {
      setError('Toutes les questions doivent avoir un texte.');
      return;
    }
    setCreating(true);
    setError(null);
    try {
      if (editingId) {
        await questionnaireAPI.modifier(editingId, form);
      } else {
        await questionnaireAPI.creer(form);
      }
      resetForm();
      await fetchQuestionnaires();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la sauvegarde.');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Supprimer ce questionnaire et toutes ses reponses ?')) return;
    try {
      await questionnaireAPI.supprimer(id);
      await fetchQuestionnaires();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la suppression.');
    }
  };

  const handleDesactiver = async (id) => {
    try {
      await questionnaireAPI.desactiver(id);
      await fetchQuestionnaires();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la desactivation.');
    }
  };

  const handleReactiver = async (id) => {
    try {
      await questionnaireAPI.reactiver(id);
      await fetchQuestionnaires();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la reactivation.');
    }
  };

  const viewResponses = async (q) => {
    setViewingResponses(q);
    setLoadingResponses(true);
    setResponsesData(null);
    try {
      const res = await questionnaireAPI.getReponses(q.id_questionnaire);
      setResponsesData(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors du chargement des reponses.');
    } finally {
      setLoadingResponses(false);
    }
  };

  if (loading) return <LoadingSpinner text="Chargement des questionnaires..." />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-slate-100">Questionnaires annuels</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">Creez et gérez les enquetes envoyées aux alumni</p>
        </div>
        {!showCreate && (
          <button
            onClick={() => setShowCreate(true)}
            className="inline-flex shrink-0 items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-blue-700 min-h-[44px]"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            Nouveau questionnaire
          </button>
        )}
      </div>

      {error && <ErrorMessage message={error} onRetry={() => setError(null)} />}

      {/* FORMULAIRE DE CREATION / MODIFICATION */}
      {showCreate && (
        <div className="rounded-xl border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-gray-900 dark:text-slate-100">
              {editingId ? 'Modifier le questionnaire' : 'Creer un questionnaire'}
            </h2>
            <button onClick={resetForm} className="inline-flex items-center rounded-lg px-3 py-1.5 text-sm text-gray-500 dark:text-slate-400 hover:bg-gray-100 hover:text-gray-700 dark:hover:bg-slate-700 dark:hover:text-slate-200 min-h-[44px]">
              Annuler
            </button>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">Titre *</label>
              <input
                type="text"
                value={form.titre}
                onChange={(e) => setForm((p) => ({ ...p, titre: e.target.value }))}
                placeholder="Ex: Enquete annuelle 2026"
                className="w-full rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">Description</label>
              <textarea
                rows={2}
                value={form.description}
                onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
                placeholder="Description optionnelle..."
                className="w-full rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
              />
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-gray-900 dark:text-slate-100">Questions ({form.questions.length})</h3>
                <button onClick={addQuestion} className="inline-flex items-center gap-1 rounded-lg px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 hover:text-blue-700 font-medium dark:hover:bg-blue-950 min-h-[44px]">
                  + Ajouter une question
                </button>
              </div>

              {form.questions.map((q, idx) => (
                <div key={idx} className="rounded-lg border border-gray-100 dark:border-slate-700/50 bg-gray-50 dark:bg-slate-700/50 p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700">
                      {idx + 1}
                    </span>
                    {form.questions.length > 1 && (
                      <button onClick={() => removeQuestion(idx)} className="inline-flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs font-medium text-red-500 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950 min-h-[44px]">
                        Supprimer
                      </button>
                    )}
                  </div>

                  <input
                    type="text"
                    value={q.texte}
                    onChange={(e) => updateQuestion(idx, 'texte', e.target.value)}
                    placeholder="Texte de la question..."
                    className="w-full rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
                  />

                  <div className="flex gap-3">
                    <select
                      value={q.type}
                      onChange={(e) => updateQuestion(idx, 'type', e.target.value)}
                      className="rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
                    >
                      <option value="text">Texte libre</option>
                      <option value="choice">Choix multiple</option>
                      <option value="boolean">Oui / Non</option>
                      <option value="rating">Note 1-5</option>
                    </select>
                  </div>

                  {q.type === 'choice' && (
                    <div>
                      <label className="block text-xs font-medium text-gray-500 dark:text-slate-400 mb-1">Options</label>
                      <OptionsEditor
                        options={q.options}
                        onChange={(newOpts) => updateQuestion(idx, 'options', newOpts)}
                      />
                    </div>
                  )}

                  <div>
                    <label className="block text-xs font-medium text-gray-500 dark:text-slate-400 mb-1">Tag KPI (optionnel)</label>
                    <div className="flex items-center gap-2">
                      <input
                        type="text"
                        value={q.tag || ''}
                        onChange={(e) => updateQuestion(idx, 'tag', e.target.value)}
                        placeholder="Ex: adequation_formation"
                        className="flex-1 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100 px-3 py-1.5 text-xs focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
                      />
                      {q.tag && (
                        <span className="inline-flex items-center rounded-full bg-amber-100 dark:bg-amber-950 px-2 py-0.5 text-[11px] font-medium text-amber-700 dark:text-amber-300 whitespace-nowrap">
                          KPI: {q.tag}
                        </span>
                      )}
                    </div>
                  </div>

                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={q.conditionnee_statut_emploi || false}
                      onChange={(e) => updateQuestion(idx, 'conditionnee_statut_emploi', e.target.checked)}
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 dark:border-slate-600"
                    />
                    <span className="text-xs text-gray-600 dark:text-slate-400">
                      Conditionner au statut emploi — masquer si l&apos;alumni est en recherche active
                    </span>
                  </label>
                </div>
              ))}
            </div>

            <div className="flex justify-end">
              <button
                onClick={handleCreate}
                disabled={creating}
                className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {creating ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                    Sauvegarde...
                  </>
                ) : (
                  editingId ? 'Enregistrer les modifications' : 'Creer le questionnaire'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* LISTE DES QUESTIONNAIRES */}
      {questionnaires.length === 0 ? (
        <div className="rounded-xl border border-dashed border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-800 p-12 text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400 dark:text-slate-500" fill="none" viewBox="0 0 24 24" strokeWidth="1" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m3.75 9v6m3-3H9m1.5-12H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
          </svg>
          <h3 className="mt-4 text-sm font-semibold text-gray-900 dark:text-slate-100">Aucun questionnaire</h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">Creez votre premier questionnaire pour interroger vos alumni.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {questionnaires.map((q) => (
            <div key={q.id_questionnaire} className="rounded-xl border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-semibold text-gray-900 dark:text-slate-100">{q.titre}</h3>
                    <span
                      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                        q.actif ? 'bg-green-100 dark:bg-green-950 text-green-700 dark:text-green-300' : 'bg-gray-100 dark:bg-slate-700 text-gray-500 dark:text-slate-400'
                      }`}
                    >
                      {q.actif ? 'Actif' : 'Inactif'}
                    </span>
                  </div>
                  {q.description && <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">{q.description}</p>}
                  <p className="mt-1 text-xs text-gray-400 dark:text-slate-500">
                    Cree le {new Date(q.date_creation).toLocaleDateString('fr-FR')}
                  </p>
                  {q.nb_questions > 0 && (
                    <p className="mt-1 text-xs text-gray-400 dark:text-slate-500">
                      {q.nb_questions} question(s)
                    </p>
                  )}
                  {q.tags && q.tags.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {q.tags.map((t) => (
                        <span
                          key={t}
                          className="inline-flex items-center rounded-full bg-amber-100 dark:bg-amber-950 px-2 py-0.5 text-[11px] font-medium text-amber-700 dark:text-amber-300"
                        >
                          KPI: {t}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => viewResponses(q)}
                    className="inline-flex items-center gap-1 rounded-lg border border-gray-200 dark:border-slate-700 px-3 py-2 text-xs font-medium text-gray-600 dark:text-slate-300 hover:bg-gray-50 dark:hover:bg-slate-700/50 min-h-[44px]"
                  >
                    <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                    </svg>
                    Voir reponses
                  </button>
                  <button
                    onClick={() => startEdit(q)}
                    className="inline-flex items-center gap-1 rounded-lg border border-blue-200 bg-blue-50 dark:bg-blue-950 px-3 py-2 text-xs font-medium text-blue-700 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900 min-h-[44px]"
                  >
                    <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
                    </svg>
                    Modifier
                  </button>
                  {q.actif ? (
                    <button
                      onClick={() => handleDesactiver(q.id_questionnaire)}
                      className="inline-flex items-center gap-1 rounded-lg border border-amber-200 bg-amber-50 dark:bg-amber-950 px-3 py-2 text-xs font-medium text-amber-700 dark:text-amber-300 hover:bg-amber-100 dark:hover:bg-amber-950 min-h-[44px]"
                    >
                      Desactiver
                    </button>
                  ) : (
                    <button
                      onClick={() => handleReactiver(q.id_questionnaire)}
                      className="inline-flex items-center gap-1 rounded-lg border border-green-200 bg-green-50 dark:bg-green-950 px-3 py-2 text-xs font-medium text-green-700 dark:text-green-300 hover:bg-green-100 dark:hover:bg-green-950 min-h-[44px]"
                    >
                      Reactiver
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(q.id_questionnaire)}
                    className="inline-flex items-center gap-1 rounded-lg border border-red-200 bg-red-50 dark:bg-red-950 px-3 py-2 text-xs font-medium text-red-600 hover:bg-red-100 dark:hover:bg-red-950 min-h-[44px]"
                  >
                    Supprimer
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* MODAL DES REPONSES */}
      {viewingResponses && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={() => setViewingResponses(null)}>
          <div className="w-full max-w-3xl max-h-[80vh] overflow-auto rounded-2xl bg-white dark:bg-slate-800 p-6 shadow-xl" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-bold text-gray-900 dark:text-slate-100">Reponses - {viewingResponses.titre}</h2>
                {responsesData && (
                  <p className="text-sm text-gray-500 dark:text-slate-400">{responsesData.total} reponse(s) recue(s)</p>
                )}
              </div>
              <button onClick={() => setViewingResponses(null)} className="rounded-lg p-2 text-gray-400 dark:text-slate-500 hover:bg-gray-100 dark:hover:bg-slate-700">
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {loadingResponses ? (
              <LoadingSpinner text="Chargement des reponses..." />
            ) : responsesData?.reponses?.length === 0 ? (
              <p className="text-center text-sm text-gray-500 dark:text-slate-400 py-8">Aucune reponse pour le moment.</p>
            ) : (
              <div className="space-y-3">
                {responsesData?.reponses?.map((r) => (
                  <div key={r.id_reponse} className="rounded-lg border border-gray-200 dark:border-slate-700 p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <span className="font-semibold text-sm text-gray-900 dark:text-slate-100">{r.prenom} {r.nom}</span>
                        <span className="ml-2 text-xs text-gray-400 dark:text-slate-500">{r.email}</span>
                      </div>
                      <span className="text-xs text-gray-400 dark:text-slate-500">
                        {new Date(r.date_reponse).toLocaleDateString('fr-FR')}
                      </span>
                    </div>
                    <div className="space-y-2">
                      {Object.entries(r.reponses || {}).map(([qId, val]) => {
                        const questionDef = responsesData?.questions?.[qId];
                        return (
                          <div key={qId} className="text-sm">
                            <p className="font-medium text-gray-700 dark:text-slate-300">
                              {questionDef ? questionDef.texte : `Question #${qId}`}
                            </p>
                            <p className="mt-0.5 text-gray-900 dark:text-slate-100 pl-2">{String(val)}</p>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
