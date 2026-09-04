import { useState, useEffect, useMemo, useCallback } from 'react';
import { adminRgpdAPI, adminIdentityAPI } from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';
import ErrorMessage from '../shared/ErrorMessage';
import { downloadFileByUrl } from '../../utils/downloadUrl';

const MAX_BULK_LIGNES = 5;

const avecS = (n) => (n > 1 ? 's' : '');

const FORMATS_EXPORT = [
  { value: 'json', label: 'JSON' },
  { value: 'xlsx', label: 'Excel (.xlsx)' },
  { value: 'csv', label: 'CSV' },
];

const labelFormat = (format) =>
  FORMATS_EXPORT.find((f) => f.value === format)?.label || format;

function nomAlumni(demande) {
  const qui = demande?.nom_complet || 'alumni';
  return demande?.email ? `${qui} (${demande.email})` : qui;
}

function buildBulkSummary(action, result, demandesById) {
  if (!result) return null;
  const lignes = [];
  const erreurs = [];

  if (action === 'bulk-traitee' || action === 'bulk-rejetee') {
    const resultats = result.resultats || [];
    for (const r of resultats) {
      const demande = demandesById.get(r.id_demande);
      if (r.ok) {
        lignes.push(
          action === 'bulk-traitee'
            ? `${demande?.type_demande === 'suppression' ? 'Suppression effectuée pour' : 'Export effectué pour'} ${nomAlumni(demande)}`
            : `Demande rejetée pour ${nomAlumni(demande)}`,
        );
      } else {
        erreurs.push(`Demande #${r.id_demande} : ${r.erreur || 'erreur inconnue'}`);
      }
    }
    const n = resultats.filter((r) => r.ok).length;
    return {
      titre:
        action === 'bulk-traitee'
          ? `✓ ${n} demande${avecS(n)} traitée${avecS(n)} avec succès`
          : `✓ ${n} demande${avecS(n)} rejetée${avecS(n)}`,
      lignes: n > MAX_BULK_LIGNES ? [] : lignes,
      erreurs,
    };
  }

  if (action === 'bulk-export') {
    const nExports = Object.keys(result.exports || {}).length;
    for (const id of Object.keys(result.exports || {})) {
      lignes.push(`Export effectué pour ${nomAlumni(demandesById.get(Number(id)))}`);
    }
    for (const [id, message] of Object.entries(result.erreurs || {})) {
      erreurs.push(`Demande #${id} : ${message}`);
    }
    return {
      titre: nExports > 0 ? `✓ Export effectué pour ${nExports} demande${avecS(nExports)}` : '✓ Export groupé terminé',
      lignes,
      erreurs,
    };
  }

  if (action === 'bulk-delete') {
    return {
      titre: `✓ ${result.supprimees ?? 0} demande${avecS(result.supprimees ?? 0)} supprimée${avecS(result.supprimees ?? 0)} définitivement`,
      lignes: [],
      erreurs: [],
    };
  }

  if (action === 'purge') {
    return {
      titre: `✓ Purge terminée : ${result.supprimees ?? 0} demande${avecS(result.supprimees ?? 0)} clôturée${avecS(result.supprimees ?? 0)} supprimée${avecS(result.supprimees ?? 0)}`,
      lignes: [],
      erreurs: [],
    };
  }

  return null;
}

export default function AdminRgpdDemandes() {
  const [demandes, setDemandes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterStatut, setFilterStatut] = useState('');
  const [filterType, setFilterType] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [traitementModal, setTraitementModal] = useState(null);
  const [modalAction, setModalAction] = useState(''); // 'traiter' | 'rejeter' | 'prendre'
  const [adminName, setAdminName] = useState(adminIdentityAPI.getName());
  const [motifRefus, setMotifRefus] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [exportingId, setExportingId] = useState(null);
  const [exportFormat, setExportFormat] = useState('json');

  // Sélection pour actions groupées
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [confirmModal, setConfirmModal] = useState(null); // { type, title, message }
  const [bulkSubmitting, setBulkSubmitting] = useState(false);
  const [bulkResult, setBulkResult] = useState(null);

  // Purge définitive différée des comptes anonymisés
  const [purgePreview, setPurgePreview] = useState(null);
  const [purgeLoading, setPurgeLoading] = useState(false);
  const [purgeConfirm, setPurgeConfirm] = useState(false);
  const [purgeResult, setPurgeResult] = useState(null);

  const loadDemandes = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {};
      if (filterStatut) params.statut = filterStatut;
      if (filterType) params.type_demande = filterType;
      setDemandes(await adminRgpdAPI.list(params));
      setSelectedIds(new Set()); // réinitialise la sélection au rechargement
    } catch (err) {
      const d = err.response?.data?.detail;
      setError(typeof d === 'string' ? d : 'Erreur de chargement des demandes RGPD.');
    } finally {
      setLoading(false);
    }
  }, [filterStatut, filterType]);

  useEffect(() => {
    loadDemandes();
  }, [loadDemandes]);

  const filtered = useMemo(() => {
    let result = demandes;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (d) =>
          (d.nom_complet || '').toLowerCase().includes(q) ||
          (d.email || '').toLowerCase().includes(q),
      );
    }
    return result;
  }, [demandes, searchQuery]);

  const demandesById = useMemo(
    () => new Map(demandes.map((d) => [d.id_demande, d])),
    [demandes],
  );

  const pendingCount = demandes.filter(
    (d) => d.statut === 'envoyee' || d.statut === 'en_traitement',
  ).length;
  const clotureesCount = demandes.filter(
    (d) => d.statut === 'traitee' || d.statut === 'rejetee',
  ).length;

  const allFilteredSelected =
    filtered.length > 0 && filtered.every((d) => selectedIds.has(d.id_demande));

  const toggleSelectAll = () => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (allFilteredSelected) {
        filtered.forEach((d) => next.delete(d.id_demande));
      } else {
        filtered.forEach((d) => next.add(d.id_demande));
      }
      return next;
    });
  };

  const toggleSelect = (id) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const openModal = (demande, action) => {
    setTraitementModal(demande);
    setModalAction(action);
    setMotifRefus('');
    setError(null);
  };

  const handleTraiter = async (decision) => {
    if (!adminName.trim()) {
      setError('Veuillez saisir votre nom pour la traçabilité (acteur).');
      return;
    }
    if (decision === 'rejetee' && !motifRefus.trim()) {
      setError('Veuillez saisir un motif de refus.');
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await adminRgpdAPI.traiter(traitementModal.id_demande, {
        decision,
        traitee_par: adminName.trim(),
        motif_refus: decision === 'rejetee' ? motifRefus.trim() : null,
      });
      adminIdentityAPI.setName(adminName.trim());
      setTraitementModal(null);
      await loadDemandes();
    } catch (err) {
      const d = err.response?.data?.detail;
      setError(typeof d === 'string' ? d : 'Erreur lors du traitement de la demande.');
    } finally {
      setSubmitting(false);
    }
  };

  const handlePrendreEnCharge = async () => {
    if (!adminName.trim()) {
      setError('Veuillez saisir votre nom pour la traçabilité (acteur).');
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await adminRgpdAPI.prendreEnCharge(traitementModal.id_demande, adminName.trim());
      adminIdentityAPI.setName(adminName.trim());
      setTraitementModal(null);
      await loadDemandes();
    } catch (err) {
      const d = err.response?.data?.detail;
      setError(typeof d === 'string' ? d : 'Erreur lors de la prise en charge de la demande.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleExport = async (idDemande) => {
    setExportingId(idDemande);
    setError(null);
    downloadFileByUrl(`/admin/demandes-rgpd/${idDemande}/export`, { format: exportFormat });
    setExportingId(null);
  };

  const openBulkAction = (action) => {
    setBulkResult(null);
    setError(null);
    if (action === 'delete') {
      setConfirmModal({
        type: 'bulk-delete',
        title: 'Suppression définitive',
        message: `Supprimer définitivement ${selectedIds.size} demande(s) RGPD ? Seule la table des demandes est touchée, pas les profils alumni.`,
      });
    } else if (action === 'rejetee') {
      setConfirmModal({
        type: 'bulk-rejetee',
        title: 'Rejet groupé',
        message: `Rejeter ${selectedIds.size} demande(s) ? Un motif de refus est nécessaire.`,
      });
      setMotifRefus('');
    } else if (action === 'traitee') {
      setConfirmModal({
        type: 'bulk-traitee',
        title: 'Traitement groupé',
        message: `Marquer ${selectedIds.size} demande(s) comme traitée(s) ? Les demandes de suppression déclenchent l'anonymisation des comptes (irréversible).`,
      });
    } else if (action === 'export') {
      setConfirmModal({
        type: 'bulk-export',
        title: 'Export groupé',
        message: `Exporter les données des ${selectedIds.size} demande(s) sélectionnée(s) dans un seul fichier au format ${labelFormat(exportFormat)} ?`,
      });
    }
  };

  const handleBulkConfirm = async () => {
    if (!adminName.trim()) {
      setError('Veuillez saisir votre nom pour la traçabilité (acteur).');
      return;
    }
    if (confirmModal.type === 'bulk-rejetee' && !motifRefus.trim()) {
      setError('Veuillez saisir un motif de refus pour le rejet groupé.');
      return;
    }

    setBulkSubmitting(true);
    setError(null);
    try {
      const ids = Array.from(selectedIds);
      let result;
      switch (confirmModal.type) {
        case 'bulk-traitee':
          result = await adminRgpdAPI.bulkTraiter(ids, 'traitee', adminName.trim());
          break;
        case 'bulk-rejetee':
          result = await adminRgpdAPI.bulkTraiter(ids, 'rejetee', adminName.trim(), motifRefus.trim());
          break;
        case 'bulk-export': {
          if (exportFormat === 'json') {
            const res = await adminRgpdAPI.bulkExport(ids, 'json');
            result = res.data;
          } else {
            downloadFileByUrl(
              '/admin/demandes-rgpd/bulk/export',
              { ids: ids.join(','), format: exportFormat },
            );
            result = null;
          }
          break;
        }
        case 'bulk-delete':
          result = await adminRgpdAPI.bulkDelete(ids);
          break;
        case 'purge':
          result = await adminRgpdAPI.purgeCloturees();
          break;
        default:
          return;
      }
      adminIdentityAPI.setName(adminName.trim());
      if (confirmModal.type === 'bulk-export' && !result) {
        // Formats fichier (xlsx/csv) : pas de résumé JSON renvoyé par l'API,
        // les éventuelles erreurs figurent dans la section « Erreurs » du fichier.
        setBulkResult({ titre: `✓ Fichier d'export groupé téléchargé (${labelFormat(exportFormat)})`, lignes: [], erreurs: [] });
      } else {
        setBulkResult(buildBulkSummary(confirmModal.type, result, demandesById));
      }
      setConfirmModal(null);
      await loadDemandes();
    } catch (err) {
      const d = err.response?.data?.detail;
      setError(typeof d === 'string' ? d : 'Erreur lors de l\'action groupée.');
      setConfirmModal(null);
    } finally {
      setBulkSubmitting(false);
    }
  };

  const openPurgeModal = () => {
    setConfirmModal({
      type: 'purge',
      title: 'Purger les demandes clôturées',
      message: `Supprimer définitivement les ${clotureesCount} demande(s) « Traitées » ou « Rejetées » ? Les autres demandes ne seront pas touchées.`,
    });
    setBulkResult(null);
    setError(null);
  };

  const openPurgeAnonymises = async () => {
    setPurgeLoading(true);
    setError(null);
    setPurgeResult(null);
    setPurgeConfirm(false);
    try {
      setPurgePreview(await adminRgpdAPI.previewPurgeAnonymises());
    } catch (err) {
      const d = err.response?.data?.detail;
      setError(typeof d === 'string' ? d : "Erreur de chargement de l'aperçu de purge.");
    } finally {
      setPurgeLoading(false);
    }
  };

  const launchPurge = async () => {
    setPurgeLoading(true);
    setError(null);
    try {
      const result = await adminRgpdAPI.purgeAnonymises();
      setPurgeResult(result);
      setPurgeConfirm(false);
      setPurgePreview(null);
      await loadDemandes();
    } catch (err) {
      const d = err.response?.data?.detail;
      setError(typeof d === 'string' ? d : 'Erreur lors de la purge des comptes anonymisés.');
      setPurgeConfirm(false);
    } finally {
      setPurgeLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <div className="mb-3 inline-flex h-1 w-12 rounded-full bg-gradient-to-r from-blue-600 to-indigo-500" />
        <h1 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-slate-100 sm:text-3xl">Demandes RGPD</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">
          Traitez les demandes d'export et de suppression
        </p>
      </div>

      {error && <ErrorMessage message={error} onRetry={() => setError(null)} />}
      {purgeResult && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-800 dark:border-green-900 dark:bg-green-950 dark:text-green-200">
          {purgeResult.message ||
            `✓ Purge terminée : ${purgeResult.purges ?? 0} compte(s) supprimé(s) définitivement.`}
        </div>
      )}
      {bulkResult && (
        <>
          <div className="rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-800 dark:border-green-900 dark:bg-green-950 dark:text-green-200">
            <p className="font-medium">{bulkResult.titre}</p>
            {bulkResult.lignes.length > 0 && (
              <ul className="mt-1 space-y-0.5">
                {bulkResult.lignes.map((ligne, i) => (
                  <li key={`${ligne}-${i}`} className="pl-4">
                    {ligne}
                  </li>
                ))}
              </ul>
            )}
            {bulkResult.erreurs.length > 0 && (
              <p className="mt-1 pl-4">
                {bulkResult.erreurs.length} demande{avecS(bulkResult.erreurs.length)} n'a pas pu être
                traitée{avecS(bulkResult.erreurs.length)} (voir détails ci-dessous).
              </p>
            )}
          </div>
          {bulkResult.erreurs.length > 0 && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-200">
              <p className="font-medium">
                {bulkResult.erreurs.length} erreur{avecS(bulkResult.erreurs.length)} rencontrée{avecS(bulkResult.erreurs.length)} :
              </p>
              <ul className="mt-1 space-y-0.5">
                {bulkResult.erreurs.map((err, i) => (
                  <li key={`${err}-${i}`} className="pl-4">
                    {err}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}

      <div className="flex flex-wrap items-center gap-3">
        <select
          value={filterStatut}
          onChange={(e) => setFilterStatut(e.target.value)}
          className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
        >
          <option value="">Tous les statuts</option>
          <option value="envoyee">Envoyées</option>
          <option value="en_traitement">En cours de traitement</option>
          <option value="traitee">Traitées</option>
          <option value="rejetee">Rejetées</option>
        </select>

        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
        >
          <option value="">Tous les types</option>
          <option value="export">Export</option>
          <option value="suppression">Suppression</option>
        </select>

        <label className="flex items-center gap-2 text-sm text-gray-500 dark:text-slate-400">
          Format d'export
          <select
            value={exportFormat}
            onChange={(e) => setExportFormat(e.target.value)}
            aria-label="Format d'export"
            className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
          >
            {FORMATS_EXPORT.map((f) => (
              <option key={f.value} value={f.value}>
                {f.label}
              </option>
            ))}
          </select>
        </label>

        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Rechercher un alumni..."
          className="min-w-[200px] flex-1 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
        />

        <button
          onClick={openPurgeModal}
          disabled={clotureesCount === 0}
          className="min-h-[44px] rounded-lg border border-orange-300 bg-orange-50 px-3 py-2 text-sm font-medium text-orange-700 hover:bg-orange-100 disabled:cursor-not-allowed disabled:opacity-50 dark:border-orange-800 dark:bg-orange-950 dark:text-orange-300 dark:hover:bg-orange-900"
        >
          Purger les demandes traitées/rejetées ({clotureesCount})
        </button>

        <button
          onClick={openPurgeAnonymises}
          disabled={purgeLoading}
          className="min-h-[44px] rounded-lg border border-red-300 bg-red-50 px-3 py-2 text-sm font-medium text-red-700 hover:bg-red-100 disabled:cursor-not-allowed disabled:opacity-50 dark:border-red-800 dark:bg-red-950 dark:text-red-300 dark:hover:bg-red-900"
        >
          {purgeLoading ? 'Chargement...' : 'Comptes anonymisés à purger'}
        </button>
      </div>

      <p className="text-sm text-gray-500 dark:text-slate-400">{pendingCount} demande(s) à traiter</p>

      {selectedIds.size > 0 && (
        <div className="flex flex-wrap items-center gap-2 rounded-lg border border-blue-200 bg-blue-50 p-3 dark:border-blue-800 dark:bg-blue-950">
          <span className="text-sm font-medium text-blue-900 dark:text-blue-100">
            {selectedIds.size} demande(s) sélectionnée(s)
          </span>
          <button
            onClick={() => openBulkAction('traitee')}
            className="min-h-[44px] rounded-lg bg-green-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-green-700"
          >
            Marquer comme traitée
          </button>
          <button
            onClick={() => openBulkAction('rejetee')}
            className="min-h-[44px] rounded-lg bg-red-500 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-600"
          >
            Rejeter
          </button>
          <button
            onClick={() => openBulkAction('export')}
            className="min-h-[44px] rounded-lg bg-gray-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-gray-700"
          >
            Exporter ({labelFormat(exportFormat)})
          </button>
          <button
            onClick={() => openBulkAction('delete')}
            className="min-h-[44px] rounded-lg bg-red-700 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-800"
          >
            Supprimer
          </button>
          <button
            onClick={() => setSelectedIds(new Set())}
            className="min-h-[44px] ml-auto text-xs text-blue-600 hover:text-blue-800 dark:text-blue-400"
          >
            Tout désélectionner
          </button>
        </div>
      )}

      {loading && <LoadingSpinner text="Chargement des demandes RGPD..." />}

      {!loading && filtered.length === 0 && (
        <div className="rounded-lg border border-dashed border-gray-300 p-8 text-center text-sm text-gray-400 dark:border-slate-700 dark:text-slate-500">
          Aucune demande RGPD pour le moment.
        </div>
      )}

      {!loading && filtered.length > 0 && (
        <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-slate-700">
          <table className="min-w-full divide-y divide-gray-200 text-sm dark:divide-slate-700">
            <thead className="bg-gray-50 dark:bg-slate-700/50">
              <tr>
                <th className="px-4 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={allFilteredSelected}
                    onChange={toggleSelectAll}
                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    aria-label="Tout sélectionner"
                  />
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-slate-400">Date</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-slate-400">Alumni</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-slate-400">Type</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-slate-400">Statut</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-slate-400">Compte</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-slate-400">Traitée par</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((d) => (
                <tr key={d.id_demande} className="border-t border-gray-100 hover:bg-gray-50 dark:border-slate-700 dark:hover:bg-slate-700/30">
                  <td className="px-4 py-3">
                    <input
                      type="checkbox"
                      checked={selectedIds.has(d.id_demande)}
                      onChange={() => toggleSelect(d.id_demande)}
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      aria-label={`Sélectionner la demande ${d.id_demande}`}
                    />
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    {new Date(d.date_demande).toLocaleDateString('fr-FR')}
                  </td>
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-900 dark:text-slate-100">{d.nom_complet || '—'}</div>
                    <div className="text-xs text-gray-500 dark:text-slate-400">{d.email || ''}</div>
                  </td>
                  <td className="px-4 py-3">
                    {d.type_demande === 'suppression' ? (
                      <span className="inline-flex rounded-full bg-red-100 px-2 py-1 text-xs font-medium text-red-800 dark:bg-red-900 dark:text-red-200">Suppression</span>
                    ) : (
                      <span className="inline-flex rounded-full bg-blue-100 px-2 py-1 text-xs font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200">Export</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
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
                  <td className="px-4 py-3">
                    {d.id_etudiant == null ? (
                      <span className="text-xs text-gray-400 dark:text-slate-500">—</span>
                    ) : d.compte_active === false ? (
                      <div className="space-y-0.5">
                        <span className="inline-flex rounded-full bg-gray-100 px-2 py-1 text-xs font-medium text-gray-600 dark:bg-slate-700 dark:text-slate-300">Anonymisé</span>
                        {d.purge_dans_jours != null && (
                          <div className={`text-xs ${d.purge_dans_jours === 0 || d.eligible_purge ? 'text-orange-600 dark:text-orange-400' : 'text-gray-500 dark:text-slate-400'}`}>
                            {d.purge_dans_jours > 0
                              ? `Purge dans ${d.purge_dans_jours} j`
                              : 'Éligible à la purge définitive'}
                          </div>
                        )}
                      </div>
                    ) : (
                      <span className="text-xs text-gray-400 dark:text-slate-500">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {d.statut === 'en_traitement' ? (
                      <div className="text-xs">
                        <span className="text-gray-500 dark:text-slate-400">En charge : </span>
                        <span className="font-medium text-gray-900 dark:text-slate-100">{d.prise_en_charge_par || '—'}</span>
                      </div>
                    ) : d.type_demande === 'export' && d.statut === 'traitee' && !d.traitee_par ? (
                      <span className="text-xs text-gray-400 dark:text-slate-500">Automatique</span>
                    ) : (
                      <div className="text-xs">
                        <span className="font-medium text-gray-900 dark:text-slate-100">{d.traitee_par || '—'}</span>
                        {d.statut === 'rejetee' && d.motif_refus ? (
                          <div
                            className="mt-0.5 max-w-[240px] truncate text-gray-500 dark:text-slate-400"
                            title={d.motif_refus}
                          >
                            Motif : {d.motif_refus}
                          </div>
                        ) : null}
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {d.statut === 'envoyee' ? (
                      <button
                        onClick={() => openModal(d, 'prendre')}
                        className="min-h-[44px] rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700"
                      >
                        Prendre en charge
                      </button>
                    ) : d.statut === 'en_traitement' ? (
                      <div className="flex gap-2">
                        <button
                          onClick={() => openModal(d, 'traiter')}
                          className="min-h-[44px] rounded-lg bg-green-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-green-700"
                        >
                          Traiter
                        </button>
                        <button
                          onClick={() => openModal(d, 'rejeter')}
                          className="min-h-[44px] rounded-lg bg-red-500 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-600"
                        >
                          Rejeter
                        </button>
                      </div>
                    ) : d.statut === 'traitee' ? (
                      <button
                        onClick={() => handleExport(d.id_demande)}
                        disabled={exportingId === d.id_demande}
                        className="min-h-[44px] rounded-lg bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-200 disabled:opacity-50 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600"
                      >
                        {exportingId === d.id_demande ? 'Export...' : `Exporter (${labelFormat(exportFormat)})`}
                      </button>
                    ) : (
                      <span className="text-xs text-gray-400 dark:text-slate-500">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal traitement individuel / prise en charge */}
      {traitementModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl dark:bg-slate-800">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">
              {modalAction === 'rejeter'
                ? 'Rejeter la demande'
                : modalAction === 'prendre'
                  ? 'Prendre en charge la demande'
                  : 'Traiter la demande'}
            </h2>
            {modalAction === 'prendre' ? (
              <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">
                Vous réservez cette demande pour vous. Aucun autre administrateur ne pourra la traiter.
              </p>
            ) : (
              <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">
                {traitementModal.type_demande === 'suppression'
                  ? 'Demande de suppression : le profil sera anonymisé de façon irréversible.'
                  : "Demande d'export : valider pour clôturer."}
              </p>
            )}

            <label className="mt-4 block text-sm font-medium text-gray-700 dark:text-slate-300">
              Votre nom (traçabilité)
              <input
                type="text"
                value={adminName}
                onChange={(e) => setAdminName(e.target.value)}
                className="mt-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
                placeholder="Ex : C. Diallo"
              />
            </label>

            {modalAction === 'rejeter' && (
              <label className="mt-4 block text-sm font-medium text-gray-700 dark:text-slate-300">
                Motif du refus
                <textarea
                  value={motifRefus}
                  onChange={(e) => setMotifRefus(e.target.value)}
                  rows="2"
                  className="mt-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
                  placeholder="Expliquez à l'alumni pourquoi sa demande est rejetée..."
                />
              </label>
            )}

            <div className="mt-5 flex flex-col gap-2">
              {modalAction === 'rejeter' ? (
                <button
                  onClick={() => handleTraiter('rejetee')}
                  disabled={submitting}
                  className="w-full min-h-[44px] rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
                >
                  {submitting ? 'Traitement...' : 'Rejeter la demande'}
                </button>
              ) : modalAction === 'traiter' ? (
                <button
                  onClick={() => handleTraiter('traitee')}
                  disabled={submitting}
                  className="w-full min-h-[44px] rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
                >
                  {submitting ? 'Traitement...' : 'Valider le traitement'}
                </button>
              ) : (
                <button
                  onClick={handlePrendreEnCharge}
                  disabled={submitting}
                  className="w-full min-h-[44px] rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {submitting ? 'Traitement...' : 'Confirmer la prise en charge'}
                </button>
              )}
              <button
                onClick={() => setTraitementModal(null)}
                className="w-full min-h-[44px] rounded-lg bg-gray-200 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-300 dark:bg-slate-700 dark:text-slate-200"
              >
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal aperçu purge des comptes anonymisés */}
      {purgePreview && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl dark:bg-slate-800">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">
              Purge des comptes anonymisés
            </h2>
            <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">
              {purgePreview.candidats} compte(s) anonymisé(s) éligible(s) à la purge définitive
              (délai de conservation de {purgePreview.delay_months} mois). Toutes les données liées seront supprimées.
            </p>

            {purgePreview.comptes?.length > 0 ? (
              <ul className="mt-3 max-h-56 space-y-1 overflow-y-auto rounded-lg border border-gray-200 p-3 text-sm dark:border-slate-700">
                {purgePreview.comptes.map((c) => (
                  <li
                    key={c.id_etudiant}
                    className="flex items-center justify-between gap-2 text-gray-700 dark:text-slate-200"
                  >
                    <span className="font-medium">Compte alumni n° {c.id_etudiant}</span>
                    <span className="text-xs text-gray-500 dark:text-slate-400">
                      anonymisé le{' '}
                      {c.date_anonymisation
                        ? new Date(c.date_anonymisation).toLocaleDateString('fr-FR')
                        : '—'}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="mt-3 rounded-lg border border-gray-100 bg-gray-50 p-3 text-sm text-gray-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">
                Aucun compte éligible pour le moment.
              </p>
            )}

            <div className="mt-5 flex flex-col gap-2">
              <button
                onClick={() => setPurgeConfirm(true)}
                disabled={purgePreview.candidats === 0 || purgeLoading}
                className="w-full min-h-[44px] rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
              >
                Lancer la purge définitive
              </button>
              <button
                onClick={() => setPurgePreview(null)}
                className="w-full min-h-[44px] rounded-lg bg-gray-200 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-300 dark:bg-slate-700 dark:text-slate-200"
              >
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal confirmation purge définitive */}
      {purgeConfirm && purgePreview && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl dark:bg-slate-800">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">
              Confirmer la purge définitive
            </h2>
            <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">
              Supprimer définitivement {purgePreview.candidats} compte(s) anonymisé(s) et toutes leurs données. Action irréversible et tracée.
            </p>
            <div className="mt-5 flex flex-col gap-2">
              <button
                onClick={launchPurge}
                disabled={purgeLoading}
                className="w-full min-h-[44px] rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
              >
                {purgeLoading ? 'Purge en cours...' : 'Confirmer la purge'}
              </button>
              <button
                onClick={() => setPurgeConfirm(false)}
                className="w-full min-h-[44px] rounded-lg bg-gray-200 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-300 dark:bg-slate-700 dark:text-slate-200"
              >
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal confirmation action groupée / purge */}
      {confirmModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl dark:bg-slate-800">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">{confirmModal.title}</h2>
            <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">{confirmModal.message}</p>

            <label className="mt-4 block text-sm font-medium text-gray-700 dark:text-slate-300">
              Votre nom (traçabilité)
              <input
                type="text"
                value={adminName}
                onChange={(e) => setAdminName(e.target.value)}
                className="mt-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
                placeholder="Ex : C. Diallo"
              />
            </label>

            {confirmModal.type === 'bulk-rejetee' && (
              <label className="mt-4 block text-sm font-medium text-gray-700 dark:text-slate-300">
                Motif du refus (appliqué à toutes les demandes sélectionnées)
                <textarea
                  value={motifRefus}
                  onChange={(e) => setMotifRefus(e.target.value)}
                  rows="2"
                  className="mt-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100"
                  placeholder="Expliquez le motif du rejet..."
                />
              </label>
            )}

            <div className="mt-5 flex flex-col gap-2">
              <button
                onClick={handleBulkConfirm}
                disabled={bulkSubmitting}
                className={`w-full min-h-[44px] rounded-lg px-4 py-2 text-sm font-medium text-white disabled:opacity-50 ${
                  confirmModal.type === 'bulk-delete' || confirmModal.type === 'purge' || confirmModal.type === 'bulk-rejetee'
                    ? 'bg-red-600 hover:bg-red-700'
                    : confirmModal.type === 'bulk-traitee'
                      ? 'bg-green-600 hover:bg-green-700'
                      : 'bg-gray-600 hover:bg-gray-700'
                }`}
              >
                {bulkSubmitting ? 'Traitement...' : 'Confirmer'}
              </button>
              <button
                onClick={() => setConfirmModal(null)}
                className="w-full min-h-[44px] rounded-lg bg-gray-200 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-300 dark:bg-slate-700 dark:text-slate-200"
              >
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
