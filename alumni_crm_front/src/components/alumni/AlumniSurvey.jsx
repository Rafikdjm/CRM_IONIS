import { useState, useEffect } from 'react';
import { questionnaireAPI, alumniAPI } from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';
import ErrorMessage from '../shared/ErrorMessage';

const QUESTION_TYPES = {
  text: 'Réponse libre',
  choice: 'Choix parmi une liste',
  boolean: 'Oui / Non',
  rating: 'Note (1-5)',
};

const getAlumniStatus = (profile) => {
  if (!profile) return '';
  return (profile.availability_status || '').trim().toLowerCase();
};

const isEnRechercheActive = (profile) => getAlumniStatus(profile) === 'en_recherche';

export default function AlumniSurvey() {
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [refused, setRefused] = useState(false);
  const [questionnaire, setQuestionnaire] = useState(null);
  const [answers, setAnswers] = useState({});
  const [previousAnswers, setPreviousAnswers] = useState([]);
  const [profile, setProfile] = useState(null);
  const [confirmDelete, setConfirmDelete] = useState(false);

  const alumniId = localStorage.getItem('alumni_id');

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      setError(null);
      try {
        const [qRes, prevRes, profileRes] = await Promise.all([
          questionnaireAPI.getActif(alumniId),
          alumniId ? questionnaireAPI.getMesReponses(alumniId).catch(() => ({ data: [] })) : Promise.resolve({ data: [] }),
          alumniId ? alumniAPI.getById(alumniId).catch(() => ({ data: null })) : Promise.resolve({ data: null }),
        ]);
        setQuestionnaire(qRes.data);
        setPreviousAnswers(prevRes.data);
        setProfile(profileRes.data);

        if (qRes.data?.questions && prevRes.data?.length > 0) {
          const lastReponse = prevRes.data[0];
          const prefill = {};
          if (lastReponse.reponses) {
            qRes.data.questions.forEach((q) => {
              if (lastReponse.reponses[String(q.id_question)] !== undefined) {
                prefill[q.id_question] = lastReponse.reponses[String(q.id_question)];
              }
            });
          }
          setAnswers(prefill);
        }
      } catch (err) {
        const detail = err.response?.data?.detail;
        if (err.response?.status === 403) setRefused(true);
        setError(detail || 'Aucun questionnaire actif pour le moment.');
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [alumniId]);

  const isHiddenByStatus = (q) => {
    if (!q.conditionnee_statut_emploi) return false;
    return isEnRechercheActive(profile);
  };

  const visibleQuestions = (questionnaire?.questions || []).filter((q) => !isHiddenByStatus(q));
  const hiddenQuestions = (questionnaire?.questions || []).filter((q) => isHiddenByStatus(q));

  const handleChange = (questionId, value) => {
    setAnswers((prev) => ({ ...prev, [questionId]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!questionnaire || !alumniId) {
      setError('Impossible d\'envoyer la réponse. Vérifiez votre connexion.');
      return;
    }

    const unanswered = visibleQuestions.filter(
      (q) => !answers[q.id_question] || String(answers[q.id_question]).trim() === '',
    );
    if (unanswered.length > 0) {
      setError(`Veuillez répondre à toutes les questions (${unanswered.length} restante(s)).`);
      return;
    }

    const finalAnswers = { ...answers };
    hiddenQuestions.forEach((q) => {
      finalAnswers[q.id_question] = 'Non applicable';
    });

    setSubmitting(true);
    setError(null);
    setSuccess(false);
    try {
      await questionnaireAPI.repondre(questionnaire.id_questionnaire, alumniId, finalAnswers);
      setSuccess(true);
      const prevRes = await questionnaireAPI.getMesReponses(alumniId);
      setPreviousAnswers(prevRes.data);
      setTimeout(() => setSuccess(false), 5000);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(detail || 'Erreur lors de l\'envoi. Réessayez.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!questionnaire || !alumniId) return;
    setConfirmDelete(true);
  };

  const confirmDeleteAction = async () => {
    if (!questionnaire || !alumniId) return;
    setConfirmDelete(false);
    setDeleting(true);
    setError(null);
    setSuccess(false);
    try {
      await questionnaireAPI.supprimerReponse(questionnaire.id_questionnaire, alumniId);
      setPreviousAnswers([]);
      setAnswers({});
      setSuccess(true);
      setTimeout(() => setSuccess(false), 5000);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(detail || 'Erreur lors de la suppression. Réessayez.');
    } finally {
      setDeleting(false);
    }
  };

  if (loading) return <LoadingSpinner text="Chargement du questionnaire..." />;

  if (error && !questionnaire) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-slate-100">Enquête annuelle</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">Participez à l'enquête de suivi des parcours alumni</p>
        </div>
        {refused ? (
          <div className="rounded-xl border border-amber-200 bg-amber-50 p-6 dark:border-amber-800 dark:bg-amber-950">
            <h2 className="text-base font-semibold text-amber-900 dark:text-amber-200">Consentement aux enquêtes refusé</h2>
            <p className="mt-1 text-sm text-amber-800 dark:text-amber-300">
              Vous avez indiqué ne pas souhaiter participer aux enquêtes alumni.
              Le questionnaire n'est donc pas accessible.
            </p>
          </div>
        ) : (
          <ErrorMessage message={error} />
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-slate-100">Enquête annuelle</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">Participez à l'enquête de suivi des parcours alumni</p>
      </div>

      {questionnaire && (
        <div className="rounded-xl border border-blue-200 bg-blue-50 p-4 dark:bg-blue-950 dark:border-blue-800">
          <h2 className="text-lg font-bold text-gray-900 dark:text-slate-100">{questionnaire.titre}</h2>
          {questionnaire.description && (
            <p className="mt-1 text-sm text-gray-600 dark:text-slate-300">{questionnaire.description}</p>
          )}
          <p className="mt-2 text-xs text-gray-500 dark:text-slate-400">
            {questionnaire.questions.length} question(s) &middot; Créé le {new Date(questionnaire.date_creation).toLocaleDateString('fr-FR')}
          </p>
        </div>
      )}

      {error && <ErrorMessage message={error} onRetry={() => setError(null)} />}

      {success && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-4 dark:bg-green-950 dark:border-green-800">
          <div className="flex items-center gap-2">
            <svg className="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
            </svg>
            <p className="text-sm font-medium text-green-800 dark:text-green-200">
              {previousAnswers.length > 0
                ? 'Réponse enregistrée avec succès ! Vous pouvez modifier vos réponses à tout moment.'
                : 'Votre réponse a été supprimée avec succès.'}
            </p>
          </div>
        </div>
      )}

      {confirmDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={() => setConfirmDelete(false)}>
          <div className="w-full max-w-sm rounded-2xl bg-white dark:bg-slate-800 p-6 shadow-xl" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-red-100 dark:bg-red-900">
                <svg className="h-5 w-5 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                </svg>
              </div>
              <div>
                <h3 className="text-base font-semibold text-gray-900 dark:text-slate-100">Supprimer ma réponse</h3>
                <p className="text-sm text-gray-500 dark:text-slate-400">Cette action est irréversible.</p>
              </div>
            </div>
            <p className="text-sm text-gray-600 dark:text-slate-300 mb-5">
              Voulez-vous vraiment supprimer votre réponse au questionnaire &laquo;&nbsp;{questionnaire?.titre}&nbsp;&raquo;&nbsp;?
            </p>
            <div className="flex flex-col gap-3 sm:flex-row sm:justify-end">
              <button
                type="button"
                onClick={() => setConfirmDelete(false)}
                className="inline-flex items-center justify-center rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600 min-h-[44px]"
              >
                Annuler
              </button>
              <button
                type="button"
                onClick={confirmDeleteAction}
                className="inline-flex items-center justify-center rounded-lg bg-red-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-red-700 min-h-[44px]"
              >
                Supprimer
              </button>
            </div>
          </div>
        </div>
      )}

      {questionnaire && (
        <form onSubmit={handleSubmit} className="space-y-5">
          {questionnaire.questions.map((q, idx) => {
            if (isHiddenByStatus(q)) {
              return (
                <div key={q.id_question} className="rounded-xl border border-dashed border-gray-300 dark:border-slate-600 bg-gray-50 dark:bg-slate-800/50 p-5">
                  <div className="flex items-start gap-3">
                    <span className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-gray-200 dark:bg-slate-700 text-sm font-bold text-gray-500 dark:text-slate-400">
                      {idx + 1}
                    </span>
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-gray-900 dark:text-slate-100">{q.texte}</p>
                      <p className="mt-0.5 text-xs text-gray-400 dark:text-slate-500">{QUESTION_TYPES[q.type] || q.type}</p>
                      <div className="mt-3 rounded-lg bg-gray-100 dark:bg-slate-700 p-3">
                        <p className="text-xs text-gray-500 dark:text-slate-400 italic">
                          Cette question ne s&apos;applique pas à votre situation actuelle. Elle sera enregistrée comme &laquo;&nbsp;Non applicable&nbsp;&raquo;.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              );
            }

            return (
              <div key={q.id_question} className="rounded-xl border border-gray-200 bg-white p-3 shadow-sm dark:border-slate-700 dark:bg-slate-800 sm:p-5">
                <div className="flex items-start gap-3">
                  <span className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-emerald-100 dark:bg-emerald-900 text-sm font-bold text-emerald-700 dark:text-emerald-300">
                    {idx + 1}
                  </span>
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-gray-900 dark:text-slate-100">{q.texte}</p>
                    <p className="mt-0.5 text-xs text-gray-400 dark:text-slate-500">{QUESTION_TYPES[q.type] || q.type}</p>

                    <div className="mt-3">
                      {q.type === 'text' && (
                        <textarea
                          rows={3}
                          value={answers[q.id_question] || ''}
                          onChange={(e) => handleChange(q.id_question, e.target.value)}
                          placeholder="Votre réponse..."
                          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-none dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100 dark:placeholder-slate-500"
                        />
                      )}

                      {q.type === 'choice' && (
                        <div className="space-y-2">
                          {(q.options || []).map((opt) => (
                            <label key={opt} className="flex items-center gap-2 cursor-pointer">
                              <input
                                type="radio"
                                name={`q_${q.id_question}`}
                                checked={answers[q.id_question] === opt}
                                onChange={() => handleChange(q.id_question, opt)}
                                className="h-4 w-4 border-gray-300 text-emerald-600 focus:ring-emerald-500 dark:border-slate-600"
                              />
                              <span className="text-sm text-gray-700 dark:text-slate-300">{opt}</span>
                            </label>
                          ))}
                        </div>
                      )}

                      {q.type === 'boolean' && (
                        <div className="flex flex-col gap-3 sm:flex-row">
                          {['Oui', 'Non'].map((val) => (
                            <button
                              key={val}
                              type="button"
                              onClick={() => handleChange(q.id_question, val)}
                              className={`flex min-h-[44px] flex-1 items-center justify-center rounded-lg border px-4 py-2 text-sm font-medium transition ${
                                answers[q.id_question] === val
                                  ? 'border-emerald-500 bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'
                                  : 'border-gray-200 bg-gray-50 text-gray-600 hover:bg-gray-100 dark:border-slate-700 dark:bg-slate-700/50 dark:text-slate-300 dark:hover:bg-slate-700'
                              }`}
                            >
                              {val}
                            </button>
                          ))}
                        </div>
                      )}

                      {q.type === 'rating' && (
                        <div className="flex flex-wrap gap-2">
                          {[1, 2, 3, 4, 5].map((n) => (
                            <button
                              key={n}
                              type="button"
                              onClick={() => handleChange(q.id_question, String(n))}
                              className={`flex h-11 w-11 items-center justify-center rounded-lg text-sm font-bold transition sm:h-10 sm:w-10 ${
                                answers[q.id_question] === String(n)
                                  ? 'bg-emerald-600 text-white'
                                  : 'border border-gray-200 bg-gray-50 text-gray-600 hover:bg-gray-100 dark:border-slate-700 dark:bg-slate-700/50 dark:text-slate-300 dark:hover:bg-slate-700'
                              }`}
                            >
                              {n}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}

          <div className="flex flex-col items-stretch gap-3 sm:flex-row sm:items-center sm:justify-between">
            {previousAnswers.length > 0 && (
              <p className="text-xs text-gray-400 dark:text-slate-500 sm:text-right">
                Dernière réponse : {new Date(previousAnswers[0].date_reponse).toLocaleDateString('fr-FR')}
              </p>
            )}
            <div className="flex flex-col gap-3 sm:ml-auto sm:flex-row sm:items-center">
              {previousAnswers.length > 0 && (
                <button
                  type="button"
                  onClick={handleDelete}
                  disabled={deleting}
                  className="inline-flex items-center justify-center gap-2 rounded-lg border border-red-300 bg-white px-5 py-2.5 text-sm font-medium text-red-600 shadow-sm hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-red-700 dark:bg-slate-800 dark:text-red-400 dark:hover:bg-red-950 min-h-[44px]"
                >
                  {deleting ? (
                    <>
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-red-300 border-t-red-600" />
                      Suppression...
                    </>
                  ) : (
                    <>
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                      </svg>
                      Supprimer ma réponse
                    </>
                  )}
                </button>
              )}
              <button
                type="submit"
                disabled={submitting}
                className="inline-flex items-center justify-center gap-2 rounded-lg bg-emerald-600 px-6 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50 min-h-[44px]"
              >
              {submitting ? (
                <>
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                  Envoi en cours...
                </>
              ) : (
                <>
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
                  </svg>
                  {previousAnswers.length > 0 ? 'Mettre à jour mes réponses' : 'Envoyer mes réponses'}
                </>
              )}
            </button>
            </div>
          </div>
        </form>
      )}
    </div>
  );
}