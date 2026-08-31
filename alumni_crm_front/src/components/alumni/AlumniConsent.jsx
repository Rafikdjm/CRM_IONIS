import { useState, useEffect } from 'react';
import { consentAPI, rgpdAPI } from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';
import ErrorMessage from '../shared/ErrorMessage';
import downloadBlob from '../../utils/downloadBlob';

export default function AlumniConsent() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [consent, setConsent] = useState({
    contact_allowed: false,
    data_sharing: false,
    survey_participation: false,
    newsletter: false,
    last_updated: null,
  });

  useEffect(() => {
    const fetchConsent = async () => {
      setLoading(true);
      try {
        const alumniId = localStorage.getItem('alumni_id');
        if (alumniId) {
          const res = await consentAPI.get(alumniId);
          if (res.data) {
            setConsent(res.data);
          }
        }
      } catch {
        // Endpoint peut ne pas exister encore — on garde les valeurs par défaut
      } finally {
        setLoading(false);
      }
    };
    fetchConsent();
  }, []);

  const handleToggle = (field) => {
    setConsent((prev) => ({ ...prev, [field]: !prev[field] }));
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccess(false);
    try {
      const alumniId = localStorage.getItem('alumni_id');
      if (!alumniId) {
        setError('Aucun profil identifié. Veuillez vous connecter d\'abord.');
        return;
      }
      await consentAPI.update(alumniId, consent);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(detail || 'Erreur lors de la sauvegarde. Vérifiez que le backend est accessible.');
    } finally {
      setSaving(false);
    }
  };

  const [myDemandes, setMyDemandes] = useState([]);
  const [loadingDemandes, setLoadingDemandes] = useState(false);
  const [demandeError, setDemandeError] = useState(null);
  const [demandeSuccess, setDemandeSuccess] = useState(null);
  const [exporting, setExporting] = useState(false);
  const [formatExport, setFormatExport] = useState('json');
  const [submittingDemande, setSubmittingDemande] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const loadDemandes = async () => {
    setLoadingDemandes(true);
    setDemandeError(null);
    try {
      setMyDemandes(await rgpdAPI.listMine());
    } catch (err) {
      const d = err.response?.data?.detail;
      setDemandeError(typeof d === 'string' ? d : 'Impossible de charger vos demandes RGPD.');
    } finally {
      setLoadingDemandes(false);
    }
  };

  useEffect(() => {
    loadDemandes();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading) return <LoadingSpinner text="Chargement de vos préférences..." />;

  const handleExport = async () => {
    setExporting(true);
    setDemandeError(null);
    setDemandeSuccess(null);
    try {
      const { blob, filename } = await rgpdAPI.exportData(formatExport);
      downloadBlob(blob, filename);
      setDemandeSuccess('Export généré. Une trace a été enregistrée dans vos demandes.');
      await loadDemandes();
    } catch (err) {
      const d = err.response?.data?.detail;
      setDemandeError(typeof d === 'string' ? d : 'Erreur lors de l\'export de vos données.');
    } finally {
      setExporting(false);
    }
  };

  const handleRequestSuppression = async () => {
    setSubmittingDemande(true);
    setDemandeError(null);
    setDemandeSuccess(null);
    try {
      await rgpdAPI.create('suppression');
      setShowDeleteConfirm(false);
      setDemandeSuccess('Demande de suppression envoyée. Un administrateur va la traiter.');
      await loadDemandes();
    } catch (err) {
      const d = err.response?.data?.detail;
      setDemandeError(typeof d === 'string' ? d : 'Erreur lors de l\'envoi de la demande de suppression.');
    } finally {
      setSubmittingDemande(false);
    }
  };

  const handleCancelDemande = async (id) => {
    try {
      await rgpdAPI.cancel(id);
      setDemandeSuccess('Demande annulée.');
      await loadDemandes();
    } catch (err) {
      const d = err.response?.data?.detail;
      setDemandeError(typeof d === 'string' ? d : 'Impossible d\'annuler la demande.');
    }
  };

  const hasPendingSuppression = myDemandes.some(
    (d) => d.type_demande === 'suppression' && (d.statut === 'envoyee' || d.statut === 'en_traitement'),
  );

  const consentItems = [
    {
      key: 'contact_allowed',
      title: 'Autoriser la prise de contact',
      description: 'Être contacté pour des opportunités, des événements ou des enquêtes.',
      critical: true,
    },
    {
      key: 'data_sharing',
      title: 'Partage des données avec les partenaires',
      description: 'Partage anonymisé de vos statistiques (secteur, poste) pour les études et recrutements.',
      critical: false,
    },
    {
      key: 'survey_participation',
      title: 'Participation aux enquêtes',
      description: 'Recevoir et répondre aux enquêtes alumni.',
      critical: false,
    },
    {
      key: 'newsletter',
      title: 'Bulletin d\'information',
      description: 'Recevoir la newsletter : actualités, événements et offres d\'emploi.',
      critical: false,
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-slate-100">RGPD & Consentement</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">
          Gérez vos consentements et vos demandes relatives à vos données personnelles
        </p>
      </div>

      <div className="rounded-xl border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-950">
        <div className="flex items-start gap-3">
          <svg className="mt-0.5 h-5 w-5 flex-shrink-0 text-blue-600" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
          </svg>
          <div className="text-sm text-blue-800 dark:text-blue-200">
            <p className="font-medium">Protection de vos données</p>
            <p className="mt-1">
              Vos données sont protégées par le RGPD : vous pouvez à tout moment les consulter, modifier ou demander leur suppression.
            </p>
          </div>
        </div>
      </div>

      {error && <ErrorMessage message={error} onRetry={() => setError(null)} />}

      {success && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-4 dark:border-green-900 dark:bg-green-950">
          <div className="flex items-center gap-2">
            <svg className="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
            </svg>
            <p className="text-sm font-medium text-green-800 dark:text-green-200">Préférences sauvegardées !</p>
          </div>
        </div>
      )}

      <div className="space-y-4">
        {consentItems.map((item) => (
          <div
            key={item.key}
            className={`rounded-xl border bg-white p-5 shadow-sm transition dark:bg-slate-800 ${
              consent[item.key] ? 'border-green-200 dark:border-green-800' : 'border-gray-200 dark:border-slate-700'
            }`}
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-semibold text-gray-900 dark:text-slate-100">{item.title}</h3>
                  {item.critical && (
                    <span className="inline-flex items-center rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">
                      Recommandé
                    </span>
                  )}
                </div>
                <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">{item.description}</p>
              </div>
              <button
                onClick={() => handleToggle(item.key)}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-slate-800 ${
                  consent[item.key] ? 'bg-blue-600' : 'bg-gray-200 dark:bg-slate-600'
                }`}
                role="switch"
                aria-checked={consent[item.key]}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                    consent[item.key] ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-slate-600 dark:bg-slate-800/50">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-slate-100">Vos droits RGPD</h3>
        <ul className="mt-2 space-y-1 text-sm text-gray-600 dark:text-slate-400">
          <li className="flex items-center gap-2">
            <svg className="h-4 w-4 text-gray-400 dark:text-slate-500" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
            </svg>
            Droit d'accès à vos données personnelles
          </li>
          <li className="flex items-center gap-2">
            <svg className="h-4 w-4 text-gray-400 dark:text-slate-500" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
            </svg>
            Droit de rectification et de mise à jour
          </li>
          <li className="flex items-center gap-2">
            <svg className="h-4 w-4 text-gray-400 dark:text-slate-500" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
            </svg>
            Droit à l'effacement (« droit à l'oubli »)
          </li>
          <li className="flex items-center gap-2">
            <svg className="h-4 w-4 text-gray-400 dark:text-slate-500" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
            </svg>
            Droit de retrait du consentement à tout moment
          </li>
        </ul>
        <div className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-200">
          <p className="font-medium">Durée de conservation</p>
          <p className="mt-1">
            Vos données sont conservées tant que votre compte est actif. Après anonymisation, elles sont purgées dans un délai de 6 mois.
          </p>
          <p className="mt-2 font-medium">Questions ?</p>
          <p className="mt-1">
            Contactez le DPO :
            <a href="mailto:contact@ionis-stm.com" className="ml-1 font-medium underline">contact@ionis-stm.com</a>
          </p>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">Vos demandes RGPD</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">
          Exportez vos données ou demandez la suppression de votre compte.
        </p>

        {demandeError && <ErrorMessage message={demandeError} onRetry={() => setDemandeError(null)} />}

        {demandeSuccess && (
          <div className="mt-3 rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-800 dark:border-green-900 dark:bg-green-950 dark:text-green-200">
            {demandeSuccess}
          </div>
        )}

        <div className="mt-4 flex flex-wrap items-center gap-3">
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-slate-300">
            Format
            <select
              value={formatExport}
              onChange={(e) => setFormatExport(e.target.value)}
              disabled={exporting}
              aria-label="Format de l'export de mes données"
              className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
            >
              <option value="json">JSON</option>
              <option value="xlsx">Excel (.xlsx)</option>
              <option value="csv">CSV</option>
            </select>
          </label>
          <button
            onClick={handleExport}
            disabled={exporting}
            className="inline-flex min-h-[44px] items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {exporting ? 'Export en cours...' : '⬇ Exporter mes données'}
          </button>
          <button
            onClick={() => setShowDeleteConfirm(true)}
            disabled={hasPendingSuppression}
            className="inline-flex min-h-[44px] items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {hasPendingSuppression ? 'Suppression déjà envoyée / en cours' : '🗑 Demander la suppression de mon compte'}
          </button>
        </div>

        {showDeleteConfirm && (
          <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-800 dark:bg-red-950">
            <p className="text-sm text-red-800 dark:text-red-200">
              Supprimer définitivement votre compte ? Action irréversible après validation par un administrateur.
            </p>
            <div className="mt-3 flex gap-3">
              <button
                onClick={handleRequestSuppression}
                disabled={submittingDemande}
                className="inline-flex min-h-[44px] items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-red-700 disabled:opacity-50"
              >
                {submittingDemande ? 'Envoi...' : 'Confirmer la demande'}
              </button>
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="min-h-[44px] rounded-lg bg-gray-200 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-300 dark:bg-slate-700 dark:text-slate-200"
              >
                Annuler
              </button>
            </div>
          </div>
        )}

        {loadingDemandes && <p className="mt-4 text-sm text-gray-500 dark:text-slate-400">Chargement de vos demandes...</p>}

        {!loadingDemandes && myDemandes.length > 0 && (
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm dark:divide-slate-700">
              <thead className="bg-gray-50 dark:bg-slate-700/50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-slate-400">Type</th>
                  <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-slate-400">Date</th>
                  <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-slate-400">Statut</th>
                  <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-slate-400">Traitée par</th>
                  <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-slate-400">Actions</th>
                </tr>
              </thead>
              <tbody>
                {myDemandes.map((d) => (
                  <tr key={d.id_demande} className="border-t border-gray-100 dark:border-slate-700">
                    <td className="px-4 py-2 capitalize">{d.type_demande}</td>
                    <td className="px-4 py-2 whitespace-nowrap">
                      {new Date(d.date_demande).toLocaleDateString('fr-FR')}
                    </td>
                    <td className="px-4 py-2">
                      {d.statut === 'envoyee' ? (
                        <span className="inline-flex rounded-full bg-yellow-100 px-2 py-1 text-xs font-medium text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">Envoyée</span>
                      ) : d.statut === 'en_traitement' ? (
                        <span className="inline-flex rounded-full bg-blue-100 px-2 py-1 text-xs font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200">En cours de traitement</span>
                      ) : d.statut === 'traitee' ? (
                        <span className="inline-flex rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-800 dark:bg-green-900 dark:text-green-200">Traitée</span>
                      ) : (
                        <span className="inline-flex rounded-full bg-red-100 px-2 py-1 text-xs font-medium text-red-800 dark:bg-red-900 dark:text-red-200">Rejetée</span>
                      )}
                    </td>
                    <td className="px-4 py-2">
                      {d.statut === 'en_traitement' ? (
                        <span className="text-xs text-gray-500 dark:text-slate-400">
                          {d.prise_en_charge_par ? `${d.prise_en_charge_par} (en charge)` : '—'}
                        </span>
                      ) : d.type_demande === 'export' && d.statut === 'traitee' && !d.traitee_par ? (
                        <span className="text-xs text-gray-400 dark:text-slate-500">Automatique</span>
                      ) : (
                        d.traitee_par || '—'
                      )}
                    </td>
                    <td className="px-4 py-2">
                      {d.statut === 'envoyee' || d.statut === 'en_traitement' ? (
                        <button
                          onClick={() => handleCancelDemande(d.id_demande)}
                          className="text-sm text-red-600 hover:text-red-800 dark:text-red-400"
                        >
                          Annuler
                        </button>
                      ) : (
                        <span className="text-sm text-gray-400 dark:text-slate-500">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {!loadingDemandes && myDemandes.length === 0 && (
          <p className="mt-4 text-sm text-gray-400 dark:text-slate-500">Aucune demande pour le moment.</p>
        )}
      </div>

      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={saving}
          className="inline-flex min-h-[44px] items-center gap-2 rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {saving ? (
            <>
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
              Sauvegarde...
            </>
          ) : (
            <>
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
              </svg>
              Sauvegarder mes préférences
            </>
          )}
        </button>
      </div>

      {consent.last_updated && (
        <p className="text-right text-xs text-gray-400 dark:text-slate-500">
          Dernière mise à jour : {new Date(consent.last_updated).toLocaleDateString('fr-FR')}
        </p>
      )}
    </div>
  );
}
