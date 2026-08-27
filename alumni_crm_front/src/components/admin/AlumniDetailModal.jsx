import { useState, useEffect } from 'react';
import { alumniAPI, careerAPI } from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';

const AVAILABILITY_LABELS = {
  en_poste: 'En poste',
  a_lecoute: "À l'écoute d'opportunités",
  en_recherche: 'En recherche active',
};

const AVAILABILITY_COLORS = {
  en_poste: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  a_lecoute: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  en_recherche: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
};

function formatDate(d) {
  if (!d) return '-';
  if (/^\d{4}-\d{2}-\d{2}$/.test(d)) {
    const [y, m] = d.split('-');
    const months = ['Janv.', 'Févr.', 'Mars', 'Avr.', 'Mai', 'Juin', 'Juil.', 'Août', 'Sept.', 'Oct.', 'Nov.', 'Déc.'];
    return `${months[parseInt(m, 10) - 1]} ${y}`;
  }
  if (/^\d{4}-\d{2}$/.test(d)) {
    const [y, m] = d.split('-');
    const months = ['Janv.', 'Févr.', 'Mars', 'Avr.', 'Mai', 'Juin', 'Juil.', 'Août', 'Sept.', 'Oct.', 'Nov.', 'Déc.'];
    return `${months[parseInt(m, 10) - 1]} ${y}`;
  }
  return d;
}

export default function AlumniDetailModal({ alumniId, onClose }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [profile, setProfile] = useState(null);
  const [experiences, setExperiences] = useState([]);
  const [certifications, setCertifications] = useState([]);

  useEffect(() => {
    if (!alumniId) return;
    let cancelled = false;
    const fetchAll = async () => {
      setLoading(true);
      setError(null);
      try {
        const [profileRes, expRes, certRes] = await Promise.all([
          alumniAPI.getById(alumniId),
          careerAPI.getByAlumni(alumniId).catch(() => ({ data: [] })),
          careerAPI.getCertifications(alumniId).catch(() => ({ data: [] })),
        ]);
        if (!cancelled) {
          setProfile(profileRes.data);
          setExperiences(expRes.data || []);
          setCertifications(certRes.data || []);
        }
      } catch {
        if (!cancelled) setError('Erreur lors du chargement des données.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    fetchAll();
    return () => { cancelled = true; };
  }, [alumniId]);

  useEffect(() => {
    const handleKey = (e) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [onClose]);

  if (!alumniId) return null;

  const sectionClass = 'rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800';
  const labelClass = 'text-xs font-medium text-gray-500 dark:text-slate-400';
  const valueClass = 'mt-1 text-sm text-gray-900 dark:text-slate-100';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" role="dialog" aria-modal="true">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />

      <div className="relative z-10 flex max-h-[90vh] w-full max-w-3xl flex-col overflow-hidden rounded-2xl border border-gray-200 bg-gray-50 shadow-2xl dark:border-slate-700 dark:bg-slate-900">
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4 dark:border-slate-700">
          <h2 className="text-lg font-bold text-gray-900 dark:text-slate-100">Fiche Alumni</h2>
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
          ) : error ? (
            <div className="py-12 text-center text-sm text-red-500 dark:text-red-400">{error}</div>
          ) : profile ? (
            <div className="space-y-5">
              <div className={sectionClass}>
                <div className="mb-4 flex items-start justify-between">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900 dark:text-slate-100">
                      {profile.first_name} {profile.last_name}
                    </h3>
                    <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">{profile.email}</p>
                  </div>
                  <div className="flex flex-wrap items-center gap-2">
                    {profile.promotion && (
                      <span className="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                        {profile.promotion}
                      </span>
                    )}
                    {profile.availability_status && (
                      <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${AVAILABILITY_COLORS[profile.availability_status] || ''}`}>
                        {AVAILABILITY_LABELS[profile.availability_status] || profile.availability_status}
                      </span>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  {[
                    { label: 'Téléphone', value: profile.phone },
                    { label: 'Ville', value: profile.city },
                    { label: 'Pays', value: profile.country },
                    { label: 'Date de naissance', value: formatDate(profile.date_naissance) },
                    { label: 'Email académique', value: profile.email_academique },
                    { label: 'LinkedIn', value: profile.linkedin, isLink: true },
                  ].filter((f) => f.value).map((field) => (
                    <div key={field.label}>
                      <p className={labelClass}>{field.label}</p>
                      {field.isLink ? (
                        <a
                          href={profile.linkedin}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="mt-1 block truncate text-sm text-blue-600 hover:underline dark:text-blue-400"
                        >
                          {profile.linkedin}
                        </a>
                      ) : (
                        <p className={valueClass}>{field.value}</p>
                      )}
                    </div>
                  ))}
                </div>
                {profile.sector && (
                  <div className="mt-4">
                    <p className={labelClass}>Secteur d'activité</p>
                    <p className={valueClass}>{profile.sector}</p>
                  </div>
                )}
                {profile.parcours_anterieur && (
                  <div className="mt-4">
                    <p className={labelClass}>Parcours antérieur</p>
                    <p className={valueClass}>{profile.parcours_anterieur}</p>
                  </div>
                )}
              </div>

              <div className={sectionClass}>
                <h4 className="mb-3 text-sm font-semibold uppercase tracking-wider text-gray-500 dark:text-slate-400">
                  Expériences professionnelles ({experiences.length})
                </h4>
                {experiences.length === 0 ? (
                  <p className="text-sm text-gray-400 dark:text-slate-500">Aucune expérience renseignée.</p>
                ) : (
                  <div className="space-y-3">
                    {experiences.map((exp, i) => (
                      <div key={exp.id || i} className="rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-slate-600 dark:bg-slate-800/50">
                        <div className="flex flex-wrap items-start justify-between gap-2">
                          <div>
                            <p className="text-sm font-semibold text-gray-900 dark:text-slate-100">
                              {exp.position || exp.intitule_poste || 'Poste non renseigné'}
                            </p>
                            <p className="text-sm text-gray-600 dark:text-slate-300">
                              {exp.company || exp.nom_entreprise || 'Entreprise non renseignée'}
                            </p>
                          </div>
                          {exp.is_current && (
                            <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900 dark:text-green-300">
                              Actuel
                            </span>
                          )}
                        </div>
                        <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500 dark:text-slate-400">
                          {exp.start_date && (
                            <span>{formatDate(exp.start_date)} {exp.end_date ? `- ${formatDate(exp.end_date)}` : exp.is_current ? '- En cours' : ''}</span>
                          )}
                          {exp.ville && <span>{exp.ville}{exp.pays ? `, ${exp.pays}` : ''}</span>}
                          {exp.salary_range && <span>{exp.salary_range}</span>}
                          {exp.type_contrat && <span>{exp.type_contrat}</span>}
                        </div>
                        {exp.sector && (
                          <p className="mt-1 text-xs text-gray-500 dark:text-slate-400">Secteur : {exp.sector}</p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className={sectionClass}>
                <h4 className="mb-3 text-sm font-semibold uppercase tracking-wider text-gray-500 dark:text-slate-400">
                  Certifications ({certifications.length})
                </h4>
                {certifications.length === 0 ? (
                  <p className="text-sm text-gray-400 dark:text-slate-500">Aucune certification renseignée.</p>
                ) : (
                  <div className="space-y-2">
                    {certifications.map((cert, i) => (
                      <div key={cert.id || i} className="flex items-center justify-between rounded-lg border border-gray-200 bg-gray-50 px-4 py-3 dark:border-slate-600 dark:bg-slate-800/50">
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-slate-100">{cert.name}</p>
                          {cert.issuer && (
                            <p className="text-xs text-gray-500 dark:text-slate-400">{cert.issuer}</p>
                          )}
                        </div>
                        {cert.date_obtained && (
                          <span className="text-xs text-gray-500 dark:text-slate-400">{formatDate(cert.date_obtained)}</span>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {profile.skills && profile.skills.length > 0 && (
                <div className={sectionClass}>
                  <h4 className="mb-3 text-sm font-semibold uppercase tracking-wider text-gray-500 dark:text-slate-400">
                    Compétences
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {profile.skills.map((skill) => (
                      <span
                        key={skill}
                        className="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : null}
        </div>

        <div className="border-t border-gray-200 px-6 py-3 dark:border-slate-700">
          <button
            onClick={onClose}
            className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 min-h-[44px]"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  );
}
