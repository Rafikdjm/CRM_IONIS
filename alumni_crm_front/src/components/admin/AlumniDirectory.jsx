import { useState, useEffect, useMemo } from 'react';
import { alumniAPI, promotionsAPI, adminIdentityAPI, apiErrorMessage } from '../../services/api';
import { SECTORS } from '../../constants';
import LoadingSpinner from '../shared/LoadingSpinner';
import ErrorMessage from '../shared/ErrorMessage';
import AlumniDetailModal from './AlumniDetailModal';
import AlumniEditModal from './AlumniEditModal';

export default function AlumniDirectory() {
  const [alumni, setAlumni] = useState([]);
  const [promotions, setPromotions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [filterPromotion, setFilterPromotion] = useState('');
  const [filterSector, setFilterSector] = useState('');
  const [filterCustomSector, setFilterCustomSector] = useState('');
  const [filterCompany, setFilterCompany] = useState('');
  const [filterAvailability, setFilterAvailability] = useState('');
  const [filterContact, setFilterContact] = useState('');
  const [filterAnonymise, setFilterAnonymise] = useState('');
  const [filterSkill, setFilterSkill] = useState('');
  const [allSkills, setAllSkills] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortField, setSortField] = useState('last_name');
  const [sortDirection, setSortDirection] = useState('asc');
  const [selectedAlumniId, setSelectedAlumniId] = useState(null);
  const [editingAlumniId, setEditingAlumniId] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [anonymiseTarget, setAnonymiseTarget] = useState(null);
  const [anonymising, setAnonymising] = useState(false);
  const [openActionsFor, setOpenActionsFor] = useState(null);
  const [actionsMenuRect, setActionsMenuRect] = useState(null);

  const adminName = () => adminIdentityAPI.getName().trim() || 'admin';

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {};
      if (filterPromotion) params.promotion = filterPromotion;
      if (searchQuery) params.search = searchQuery;
      if (filterContact) params.contact_autorise = filterContact;

      const [alumniRes, promoRes] = await Promise.all([
        alumniAPI.getAll(params),
        promotionsAPI.getAll().catch(() => ({ data: [] })),
      ]);
      setAlumni(alumniRes.data || []);
      setPromotions(promoRes.data || []);
    } catch (err) {
      setError(apiErrorMessage(err, 'Erreur de chargement de l\'annuaire. Vérifiez que le serveur backend est accessible.'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [filterPromotion, searchQuery, filterContact]);

  useEffect(() => {
    const skillsSet = new Set();
    alumni.forEach((a) => {
      if (Array.isArray(a.skills)) a.skills.forEach((s) => skillsSet.add(s));
    });
    setAllSkills([...skillsSet].sort());
  }, [alumni]);

  const filteredAlumni = useMemo(() => {
    let result = alumni;

    const effectiveSector = filterSector === 'Autre' ? filterCustomSector : filterSector;
    if (effectiveSector) {
      const sq = effectiveSector.toLowerCase();
      result = result.filter((a) => (a.sector || '').toLowerCase().includes(sq));
    }

    if (filterAvailability) {
      result = result.filter((a) => (a.availability_status || '') === filterAvailability);
    }

    if (filterCompany) {
      const cq = filterCompany.toLowerCase();
      result = result.filter((a) => (a.current_company || '').toLowerCase().includes(cq));
    }

    if (filterSkill) {
      const sk = filterSkill.toLowerCase();
      result = result.filter((a) =>
        Array.isArray(a.skills) && a.skills.some((s) => s.toLowerCase().includes(sk))
      );
    }

    if (filterAnonymise === 'actifs') {
      result = result.filter((a) => !a.is_anonymised);
    } else if (filterAnonymise === 'anonymises') {
      result = result.filter((a) => a.is_anonymised);
    }

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (a) =>
          `${a.first_name} ${a.last_name}`.toLowerCase().includes(q) ||
          (a.email || '').toLowerCase().includes(q) ||
          (a.current_company || '').toLowerCase().includes(q)
      );
    }

    return result;
  }, [alumni, filterSector, filterCustomSector, filterCompany, filterAvailability, filterSkill, searchQuery, filterAnonymise]);

  const sortedAlumni = useMemo(() => {
    return [...filteredAlumni].sort((a, b) => {
      let valA = a[sortField] || '';
      let valB = b[sortField] || '';
      if (typeof valA === 'string') valA = valA.toLowerCase();
      if (typeof valB === 'string') valB = valB.toLowerCase();
      if (valA < valB) return sortDirection === 'asc' ? -1 : 1;
      if (valA > valB) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }, [filteredAlumni, sortField, sortDirection]);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const clearFilters = () => {
    setFilterPromotion('');
    setFilterSector('');
    setFilterCustomSector('');
    setFilterCompany('');
    setFilterAvailability('');
    setFilterContact('');
    setFilterAnonymise('');
    setFilterSkill('');
    setSearchQuery('');
  };

  const hasActiveFilters = filterPromotion || filterSector || filterCompany || filterAvailability || filterSkill || searchQuery || filterContact || filterAnonymise;

  const isExperienceFallback = (person) => {
    return !person.has_confirmed_current && person.availability_status !== 'en_poste';
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    setError(null);
    try {
      await alumniAPI.delete(deleteTarget.id, adminName());
      setDeleteTarget(null);
      await fetchData();
    } catch (err) {
      setError(apiErrorMessage(err, 'Erreur lors de la suppression.'));
      setDeleteTarget(null);
    } finally {
      setDeleting(false);
    }
  };

  const confirmAnonymise = async () => {
    if (!anonymiseTarget) return;
    setAnonymising(true);
    setError(null);
    try {
      await alumniAPI.anonymise(anonymiseTarget.id, adminName());
      setAnonymiseTarget(null);
      await fetchData();
    } catch (err) {
      setError(apiErrorMessage(err, 'Erreur lors de l\'anonymisation.'));
      setAnonymiseTarget(null);
    } finally {
      setAnonymising(false);
    }
  };

  if (loading && alumni.length === 0) return <LoadingSpinner text="Chargement de l'annuaire..." />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-slate-100">Annuaire des Alumni</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">
          Recherchez et filtrez les anciens élèves par promotion, secteur ou entreprise
        </p>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white dark:border-slate-700 dark:bg-slate-800 p-4 shadow-sm">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6">
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Recherche</label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Nom, email, entreprise..."
              className="w-full rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Promotion</label>
            <select
              value={filterPromotion}
              onChange={(e) => setFilterPromotion(e.target.value)}
              className="w-full rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">Toutes les promotions</option>
              {promotions.map((p) => (
                <option key={p.id} value={p.name}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Secteur d'activité</label>
            <select
              value={filterSector}
              onChange={(e) => {
                setFilterSector(e.target.value);
                if (e.target.value !== 'Autre') setFilterCustomSector('');
              }}
              className="w-full rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">Tous les secteurs</option>
              {SECTORS.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
          {filterSector === 'Autre' && (
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Précisez le secteur</label>
              <input
                type="text"
                value={filterCustomSector}
                onChange={(e) => setFilterCustomSector(e.target.value)}
                placeholder="Nom du secteur..."
                className="w-full rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
          )}
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Entreprise</label>
            <input
              type="text"
              value={filterCompany}
              onChange={(e) => setFilterCompany(e.target.value)}
              placeholder="Nom de l'entreprise..."
              className="w-full rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Disponibilité</label>
            <select
              value={filterAvailability}
              onChange={(e) => setFilterAvailability(e.target.value)}
              className="w-full rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">Tous les statuts</option>
              <option value="en_poste">En poste</option>
              <option value="a_lecoute">À l'écoute d'opportunités</option>
              <option value="en_recherche">En recherche active</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Contact autorisé</label>
            <select
              value={filterContact}
              onChange={(e) => setFilterContact(e.target.value)}
              className="w-full rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">Tous</option>
              <option value="actif">Autorisé</option>
              <option value="refuse">Refusé</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Statut du compte</label>
            <select
              value={filterAnonymise}
              onChange={(e) => setFilterAnonymise(e.target.value)}
              className="w-full rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">Tous</option>
              <option value="actifs">Actifs (non anonymisés)</option>
              <option value="anonymises">Anonymisés</option>
            </select>
          </div>
          {allSkills.length > 0 && (
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-slate-400">Compétence</label>
              <select
                value={filterSkill}
                onChange={(e) => setFilterSkill(e.target.value)}
                className="w-full rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="">Toutes les compétences</option>
                {allSkills.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
          )}
        </div>
        {hasActiveFilters && (
          <div className="mt-3 flex items-center justify-between">
            <span className="text-xs text-gray-500 dark:text-slate-400">
              {sortedAlumni.length} résultat{sortedAlumni.length !== 1 ? 's' : ''}
            </span>
            <button
              onClick={clearFilters}
              className="inline-flex items-center rounded-lg px-3 py-1.5 text-xs font-medium text-blue-600 hover:bg-blue-50 hover:text-blue-800 dark:hover:bg-blue-950 min-h-[44px]"
            >
              Effacer les filtres
            </button>
          </div>
        )}
      </div>

      {error && <ErrorMessage message={error} onRetry={fetchData} />}

      <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-slate-700 dark:bg-slate-800 shadow-sm">
        <div className="overflow-x-auto">
          <div className="mb-2 flex items-center gap-1 px-4 pt-3 text-xs text-gray-400 dark:text-slate-500 md:hidden">
            <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 21 3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" />
            </svg>
            Glissez horizontalement pour voir plus de colonnes
          </div>
          <table className="min-w-full divide-y divide-gray-200 dark:divide-slate-700">
            <thead className="bg-gray-50 dark:bg-slate-700/50">
              <tr>
                {[
                  { key: 'last_name', label: 'Nom' },
                  { key: 'first_name', label: 'Prénom' },
                  { key: 'email', label: 'Email', hiddenMobile: true },
                  { key: 'promotion', label: 'Promotion' },
                  { key: 'current_company', label: 'Entreprise' },
                  { key: 'current_position', label: 'Poste', hiddenMobile: true },
                  { key: 'sector', label: 'Secteur', hiddenMobile: true },
                  { key: 'availability_status', label: 'Disponibilité' },
                  { key: 'contact_allowed', label: 'Contact' },
                  { key: 'certifications_count', label: 'Certifications', hiddenMobile: true },
                  { key: 'skills', label: 'Compétences', hiddenMobile: true },
                  { key: 'actions', label: 'Actions' },
                ].map((col) => (
                  <th
                    key={col.key}
                    onClick={col.key === 'actions' ? undefined : () => handleSort(col.key)}
                    className={`${col.key === 'actions' ? '' : 'cursor-pointer'} px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 hover:text-gray-700 dark:text-slate-400 dark:hover:text-slate-200 ${col.hiddenMobile ? 'hidden md:table-cell' : ''}`}
                  >
                    <div className="flex items-center gap-1">
                      {col.label}
                      {sortField === col.key && (
                        <span className="text-blue-600">
                          {sortDirection === 'asc' ? '\u2191' : '\u2193'}
                        </span>
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white dark:divide-slate-700 dark:bg-slate-800">
              {sortedAlumni.length === 0 ? (
                <tr>
                  <td colSpan="12" className="px-4 py-12 text-center text-sm text-gray-400 dark:text-slate-500">
                    {hasActiveFilters ? 'Aucun résultat ne correspond à vos filtres.' : 'Aucun alumni enregistré.'}
                  </td>
                </tr>
              ) : (
                sortedAlumni.map((person) => (
                  <tr
                    key={person.id}
                    onClick={() => setSelectedAlumniId(person.id)}
                    className="cursor-pointer transition hover:bg-gray-50 dark:hover:bg-slate-700/50 min-h-[44px]"
                  >
                    <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-gray-900 dark:text-slate-100">
                      {person.last_name}
                      {person.is_anonymised && (
                        <span className="ml-2 inline-flex items-center rounded-full bg-red-50 dark:bg-red-900/60 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-red-600 dark:text-red-300">
                          Anonymisé
                        </span>
                      )}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-700 dark:text-slate-300">
                      {person.first_name}
                    </td>
                    <td className="hidden px-4 py-3 text-sm text-gray-500 dark:text-slate-400 md:table-cell">
                      {person.email || '-'}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3">
                      <span className="inline-flex items-center rounded-full bg-blue-50 dark:bg-blue-900 px-2 py-1 text-xs font-medium text-blue-700 dark:text-blue-300">
                        {person.promotion}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700 dark:text-slate-300">
                      {person.current_company
                        ? isExperienceFallback(person)
                          ? <span className="text-gray-400 italic dark:text-slate-500">Ex- {person.current_company}</span>
                          : person.current_company
                        : '-'}
                    </td>
                    <td className="hidden px-4 py-3 text-sm text-gray-700 dark:text-slate-300 md:table-cell">
                      {person.current_position
                        ? isExperienceFallback(person)
                          ? <span className="text-gray-400 italic dark:text-slate-500">Ex- {person.current_position}</span>
                          : person.current_position
                        : '-'}
                    </td>
                    <td className="hidden px-4 py-3 md:table-cell">
                      {person.sector ? (
                        isExperienceFallback(person) ? (
                          <span className="inline-flex items-center rounded-full bg-gray-100 dark:bg-slate-700 px-2 py-1 text-xs font-medium text-gray-500 dark:text-slate-400 italic">
                            Ex- {person.sector}
                          </span>
                        ) : (
                          <span className="inline-flex items-center rounded-full bg-emerald-50 dark:bg-emerald-900 px-2 py-1 text-xs font-medium text-emerald-700 dark:text-emerald-300">
                            {person.sector}
                          </span>
                        )
                      ) : (
                        <span className="text-gray-400 dark:text-slate-500">-</span>
                      )}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3">
                      {person.availability_status ? (
                        <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                          person.availability_status === 'en_poste'
                            ? 'bg-green-50 dark:bg-green-900 text-green-700 dark:text-green-300'
                            : person.availability_status === 'en_recherche'
                            ? 'bg-orange-50 dark:bg-orange-900 text-orange-700 dark:text-orange-300'
                            : 'bg-yellow-50 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-300'
                        }`}>
                          {person.availability_status === 'en_poste'
                            ? 'En poste'
                            : person.availability_status === 'en_recherche'
                            ? 'En recherche active'
                            : "À l'écoute"}
                        </span>
                      ) : (
                        <span className="text-gray-400 dark:text-slate-500">-</span>
                      )}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3">
                      {person.contact_status === 'actif' ? (
                        <span className="inline-flex items-center rounded-full bg-emerald-50 dark:bg-emerald-900 px-2 py-1 text-xs font-medium text-emerald-700 dark:text-emerald-300">
                          Autorisé
                        </span>
                      ) : person.contact_status === 'refuse' ? (
                        <span className="inline-flex items-center rounded-full bg-red-50 dark:bg-red-900 px-2 py-1 text-xs font-medium text-red-700 dark:text-red-300">
                          Refusé
                        </span>
                      ) : (
                        <span className="text-gray-400 dark:text-slate-500">-</span>
                      )}
                    </td>
                    <td className="hidden px-4 py-3 text-sm md:table-cell">
                      {person.certifications_count > 0 ? (
                        <span className="inline-flex items-center gap-1 rounded-full bg-violet-50 dark:bg-violet-900 px-2 py-1 text-xs font-medium text-violet-700 dark:text-violet-300">
                          <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.62 48.62 0 0 1 12 20.904a48.62 48.62 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347m-15.482 0a50.636 50.636 0 0 0-2.658-.813A59.906 59.906 0 0 1 12 3.493a59.903 59.903 0 0 1 10.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.717 50.717 0 0 1 12 13.489a50.702 50.702 0 0 1 7.74-3.342" />
                          </svg>
                          {person.certifications_count}
                        </span>
                      ) : (
                        <span className="text-gray-400 dark:text-slate-500">-</span>
                      )}
                    </td>
                    <td className="hidden px-4 py-3 md:table-cell">
                      {Array.isArray(person.skills) && person.skills.length > 0 ? (
                        <div className="flex flex-wrap gap-1">
                          {person.skills.slice(0, 3).map((skill) => (
                            <span
                              key={skill}
                              className="inline-flex items-center rounded-full bg-blue-50 dark:bg-blue-900 px-2 py-0.5 text-xs font-medium text-blue-700 dark:text-blue-300"
                            >
                              {skill}
                            </span>
                          ))}
                          {person.skills.length > 3 && (
                            <span className="inline-flex items-center rounded-full bg-gray-100 dark:bg-slate-700 px-2 py-0.5 text-xs font-medium text-gray-500 dark:text-slate-400">
                              +{person.skills.length - 3}
                            </span>
                          )}
                        </div>
                      ) : (
                        <span className="text-gray-400 dark:text-slate-500">-</span>
                      )}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3">
                      <div className="flex items-center gap-1.5" onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={() => setEditingAlumniId(person.id)}
                          disabled={person.is_anonymised}
                          className="inline-flex items-center gap-1 rounded-lg border border-blue-200 bg-blue-50 dark:bg-blue-950 px-3 py-2 text-xs font-medium text-blue-700 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900 disabled:cursor-not-allowed disabled:opacity-50 min-h-[44px]"
                          title={person.is_anonymised ? 'Compte anonymisé : modification impossible' : undefined}
                        >
                          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
                          </svg>
                          Modifier
                        </button>
                        <button
                          onClick={() => setAnonymiseTarget({ id: person.id, name: `${person.first_name} ${person.last_name}` })}
                          disabled={person.is_anonymised}
                          className="inline-flex items-center gap-1 rounded-lg bg-emerald-600 px-3 py-2 text-xs font-medium text-white shadow-sm hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50 min-h-[44px]"
                          title={person.is_anonymised ? 'Compte déjà anonymisé' : 'Anonymiser (RGPD) : masque les données personnelles, hors demande RGPD'}
                        >
                          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z" />
                          </svg>
                          Anonymiser
                        </button>
                        <div className="relative">
                          <button
                            onClick={(e) => {
                              const willOpen = openActionsFor !== person.id;
                              setOpenActionsFor(willOpen ? person.id : null);
                              if (willOpen) {
                                const rect = e.currentTarget.getBoundingClientRect();
                                setActionsMenuRect({
                                  top: rect.bottom,
                                  bottom: window.innerHeight - rect.top,
                                  right: window.innerWidth - rect.right,
                                  opensUp: rect.bottom + 64 > window.innerHeight,
                                });
                              }
                            }}
                            className="inline-flex items-center rounded-lg border border-gray-200 bg-white px-2.5 py-2 text-gray-500 hover:bg-gray-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700 min-h-[44px]"
                            title="Plus d'actions (suppression définitive…)"
                            aria-label={`Plus d'actions pour ${person.first_name} ${person.last_name}`}
                          >
                            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 12a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM12.75 12a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM18.75 12a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Z" />
                            </svg>
                          </button>
                          {openActionsFor === person.id && actionsMenuRect && (
                            <>
                              <div
                                className="fixed inset-0 z-10"
                                onClick={() => {
                                  setOpenActionsFor(null);
                                  setActionsMenuRect(null);
                                }}
                              />
                              <div
                                className="fixed z-20 w-56 rounded-lg border border-gray-200 bg-white p-1 shadow-lg dark:border-slate-600 dark:bg-slate-800"
                                style={
                                  actionsMenuRect.opensUp
                                    ? { bottom: actionsMenuRect.bottom + 4, right: actionsMenuRect.right }
                                    : { top: actionsMenuRect.top + 4, right: actionsMenuRect.right }
                                }
                              >
                                <button
                                  onClick={() => {
                                    setOpenActionsFor(null);
                                    setActionsMenuRect(null);
                                    setDeleteTarget({ id: person.id, name: `${person.first_name} ${person.last_name}` });
                                  }}
                                  className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-xs font-semibold text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950 min-h-[44px]"
                                >
                                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                                  </svg>
                                  Supprimer définitivement
                                </button>
                              </div>
                            </>
                          )}
                        </div>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {selectedAlumniId && (
        <AlumniDetailModal
          alumniId={selectedAlumniId}
          onClose={() => setSelectedAlumniId(null)}
        />
      )}

      {editingAlumniId && (
        <AlumniEditModal
          alumniId={editingAlumniId}
          onClose={() => setEditingAlumniId(null)}
          onSaved={fetchData}
        />
      )}

      {deleteTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={() => setDeleteTarget(null)}>
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
                <h2 className="text-lg font-bold text-gray-900 dark:text-slate-100">Supprimer définitivement</h2>
                <p className="mt-2 text-sm text-gray-600 dark:text-slate-300">
                  Confirmer la suppression définitive de <span className="font-semibold">{deleteTarget.name}</span> ?
                </p>
                <div className="mt-3 rounded-lg bg-red-50 dark:bg-red-950/60 p-3 text-sm text-red-700 dark:text-red-300">
                  <span className="font-semibold">Action irréversible</span> — à réserver aux erreurs de saisie ou
                  doublons, pas aux demandes de suppression RGPD normales. Cette opération supprime <span className="font-semibold">définitivement</span>
                  l&apos;alumni et toutes ses données liées (expériences professionnelles, certifications, consentements RGPD,
                  réponses aux questionnaires) de la base de données. Le processus d&apos;anonymisation RGPD (droit à
                  l&apos;effacement) est géré par le bouton <span className="font-semibold">Anonymiser</span> et est
                  <span className="font-semibold"> totalement distinct</span>.
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-2">
              <button
                onClick={() => setDeleteTarget(null)}
                className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 min-h-[44px]"
              >
                Annuler
              </button>
              <button
                onClick={confirmDelete}
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

      {anonymiseTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={() => setAnonymiseTarget(null)}>
          <div
            className="w-full max-w-md rounded-2xl bg-white dark:bg-slate-800 p-6 shadow-xl"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
          >
            <div className="flex items-start gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-emerald-100 dark:bg-emerald-950">
                <svg className="h-5 w-5 text-emerald-600 dark:text-emerald-400" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z" />
                </svg>
              </div>
              <div className="flex-1">
                <h2 className="text-lg font-bold text-gray-900 dark:text-slate-100">Anonymiser cet alumni</h2>
                <p className="mt-2 text-sm text-gray-600 dark:text-slate-300">
                  Confirmer l&apos;anonymisation RGPD de <span className="font-semibold">{anonymiseTarget.name}</span> ?
                </p>
                <div className="mt-3 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 p-3 text-sm text-emerald-700 dark:text-emerald-300">
                  L&apos;anonymisation masque les données personnelles (nom, prénom, email, téléphone, expériences…)
                  et marque le compte comme anonymisé. Les lignes sont conservées pour les indicateurs agrégés. La
                  purge définitive différée reste gérée par le workflow RGPD existant. Cette action est différente de
                  la <span className="font-semibold">suppression définitive</span> (réservée aux erreurs de saisie ou doublons).
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-2">
              <button
                onClick={() => setAnonymiseTarget(null)}
                className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 min-h-[44px]"
              >
                Annuler
              </button>
              <button
                onClick={confirmAnonymise}
                disabled={anonymising}
                className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50 min-h-[44px]"
              >
                {anonymising ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                    Anonymisation...
                  </>
                ) : (
                  'Anonymiser'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
