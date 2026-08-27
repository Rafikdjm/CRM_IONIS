import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const token = localStorage.getItem('token');
      const isAlumni = localStorage.getItem('alumni_id');
      if (token && !isAlumni) {
        localStorage.removeItem('token');
        window.location.href = '/';
      }
    }
    return Promise.reject(error);
  }
);

/**
 * Normalise une erreur API en message affichable.
 *
 * FastAPI renvoie `detail` sous forme de chaîne (ex. 409 « email déjà pris »)
 * OU sous forme de tableau d'objets pour les erreurs de validation Pydantic
 * 422 (ex. dates incohérentes) : `[{type, loc, msg, input}, ...]`. Le tableau
 * ne doit jamais être affiché tel quel (React ne rend pas les objets).
 */
export const apiErrorMessage = (err, fallback = 'Une erreur est survenue.') => {
  const detail = err?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    const messages = detail
      .map((d) => (d && typeof d.msg === 'string' ? d.msg.replace(/^Value error,\s*/i, '') : null))
      .filter(Boolean);
    if (messages.length > 0) return messages.join(' ');
  }
  const message = err?.response?.data?.message;
  if (typeof message === 'string') return message;
  return fallback;
};

/**
 * Décode le payload d'un JWT sans vérifier la signature (côté client, diagnostic).
 * Retourne null si le token est mal formé.
 */
const decodeJwtPayload = (token) => {
  try {
    const base64 = token.split('.')[1];
    const decoded = decodeURIComponent(
      atob(base64.replace(/-/g, '+').replace(/_/g, '/'))
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join(''),
    );
    return JSON.parse(decoded);
  } catch {
    return null;
  }
};

/**
 * Garantit que le token stocké correspond bien à une session alumni.
 * Si le navigateur contient un token admin (connexion admin dans un autre onglet),
 * il est supprimé pour forcer la reconnexion alumni et éviter l'erreur 403
 * « Cette action requiert un compte alumni connecté » sur les routes /rgpd/*.
 */
const ensureAlumniToken = () => {
  const token = localStorage.getItem('token');
  if (!token) return;
  const payload = decodeJwtPayload(token);
  if (payload && payload.role === 'admin') {
    localStorage.removeItem('token');
    throw {
      response: {
        data: { detail: 'Session administrateur détectée. Reconnectez-vous avec votre compte alumni.' },
      },
    };
  }
};

const mapBackendAlumni = (e) => {
  const mapped = {
    id: e.id_etudiant,
    last_name: e.nom,
    first_name: e.prenom,
    email: e.email || e.adresse_email || e.mail || e.email_address || e.email_academique || e.courriel || e.email_professionnelle || e.adresse_mail || '',
    promotion: e.nom_promotion || '',
    current_company: e.nom_entreprise || null,
    current_position: e.intitule_poste || e.poste || e.position || e.titre_poste || null,
    sector: e.secteur_activite || null,
    phone: e.telephone || e.phone || '',
    city: e.city || e.ville || '',
    availability_status: e.availability_status || '',
    contact_allowed: e.contact_autorise === 'actif',
    contact_status: e.contact_autorise || 'inconnu',
    skills: e.skills || [],
    date_anonymisation: e.date_anonymisation || null,
    is_anonymised: e.date_anonymisation != null,
  };
  return mapped;
};

const mapAlumniToBackend = (a) => ({
  nom: a.last_name || a.nom || '',
  prenom: a.first_name || a.prenom || '',
  email: (a.email || '').trim().toLowerCase(),
  telephone: a.phone || a.telephone || '',
  date_naissance: a.date_of_birth || a.date_naissance || '2000-01-01',
  parcours_anterieur: (a.previous_education || a.parcours_anterieur || '').substring(0, 255),
  etablissement_precedent: a.previous_school || a.etablissement_precedent || null,
  date_inscription: a.date_inscription || new Date().toISOString().split('T')[0],
  id_promotion: a.id_promotion || 1,
  email_academique: a.email_academique || null,
  address: a.address || '',
  city: a.city || '',
  country: a.country || '',
  linkedin: a.linkedin || '',
  availability_status: a.availability_status || '',
  skills: a.skills || [],
});

const mapBackendToProfile = (e) => ({
  id: e.id_etudiant,
  first_name: e.prenom || '',
  last_name: e.nom || '',
  email: e.email || '',
  phone: e.telephone || '',
  address: e.address || '',
  city: e.city || '',
  country: e.country || '',
  linkedin: e.linkedin || '',
  availability_status: e.availability_status || '',
  sector: e.secteur_activite || '',
  skills: e.skills || [],
  promotion: e.promotion_nom || '',
  id_promotion: e.id_promotion,
  experiences_count: e.experiences_count || 0,
  date_naissance: e.date_naissance || '',
  date_inscription: e.date_inscription || '',
  email_academique: e.email_academique || '',
  parcours_anterieur: e.parcours_anterieur || '',
  date_anonymisation: e.date_anonymisation || null,
  is_anonymised: e.date_anonymisation != null,
});

const mapProfileToBackend = (a) => {
  const payload = {};
  if (a.last_name != null) payload.nom = a.last_name;
  if (a.first_name != null) payload.prenom = a.first_name;
  if (a.email != null) payload.email = (a.email || '').trim().toLowerCase();
  if (a.phone != null) payload.telephone = a.phone;
  if (a.address != null) payload.address = a.address;
  if (a.city != null) payload.city = a.city;
  if (a.country != null) payload.country = a.country;
  if (a.linkedin != null) payload.linkedin = a.linkedin;
  if (a.availability_status != null) payload.availability_status = a.availability_status;
  if (a.id_promotion != null) payload.id_promotion = a.id_promotion;
  if (a.skills != null) payload.skills = a.skills;
  if (a.date_naissance != null) payload.date_naissance = a.date_naissance || null;
  if (a.email_academique != null) payload.email_academique = a.email_academique || null;
  if (a.parcours_anterieur != null) payload.parcours_anterieur = (a.parcours_anterieur || '').substring(0, 255);
  return payload;
};

const toMonthInput = (v) => {
  if (!v) return '';
  if (/^\d{4}-\d{2}$/.test(v)) return v;
  if (/^\d{4}-\d{2}-\d{2}/.test(v)) return v.slice(0, 7);
  return '';
};

const mapExperienceToCareer = (exp) => ({
  id: exp.id_experience,
  company: exp.nom_entreprise || '',
  position: exp.intitule_poste || '',
  sector: exp.secteur_activite || '',
  start_date: toMonthInput(exp.date_debut),
  end_date: toMonthInput(exp.date_fin),
  salary_range: exp.salaire != null ? String(exp.salaire) : '',
  is_current: !!exp.poste_actuel,
  description: '',
  type_contrat: exp.type_contrat || '',
  pays: exp.pays || '',
  ville: exp.ville || '',
});

/**
 * Sélectionne l'expérience à afficher dans l'annuaire pour un alumni.
 *
 * Règle de sélection (par ordre de priorité) :
 *   1. Expérience avec poste_actuel = true (poste actuellement occupé)
 *   2. Expérience ayant la date_fin la plus récente (si aucune n'est marquée actuelle)
 *   3. À défaut de date_fin, utiliser date_debut la plus récente comme tiebreaker
 *
 * Cette règle est déterministe (tri chronologique sur dates ISO) sauf en cas
 * d'égalité parfaite de date, auquel cas l'ordre est indéfini entre les ex-aequo.
 *
 * Cas concret : si un alumni n'a coché aucun poste comme "actuel" dans
 * "Mon Parcours", c'est l'expérience la plus récente qui est affichée.
 */
const pickBestExperience = (experiences) => {
  if (!experiences || experiences.length === 0) return null;
  const current = experiences.find((e) => e.poste_actuel);
  if (current) return current;
  return [...experiences].sort((a, b) => {
    const dateA = a.date_fin || a.date_debut || '';
    const dateB = b.date_fin || b.date_debut || '';
    return dateB.localeCompare(dateA);
  })[0];
};

const toFullDate = (v) => {
  if (!v) return null;
  if (/^\d{4}-\d{2}$/.test(v)) return v + '-01';
  return v;
};

const extractItems = (raw) => {
  if (Array.isArray(raw)) return raw;
  if (raw && typeof raw === 'object') {
    for (const key of [
      'anciens_eleves', 'items', 'results', 'data', 'etudiants',
      'alumni', 'students', 'records', 'rows', 'list',
    ]) {
      if (Array.isArray(raw[key])) return raw[key];
    }
  }
  return [];
};

export const alumniAPI = {
  getAll: async (params) => {
    const backendParams = {};
    if (params.promotion) backendParams.promotion = params.promotion;
    if (params.sector) backendParams.secteur = params.sector;
    if (params.company) backendParams.entreprise = params.company;
    if (params.search) backendParams.search = params.search;
    if (params.contact_autorise) backendParams.contact_autorise = params.contact_autorise;
    const res = await api.get('/admin/etudiants/filtrer', { params: backendParams });
    const alumniList = extractItems(res.data).map(mapBackendAlumni);

    const enriched = await Promise.allSettled(
      alumniList.map(async (a) => {
        a.has_confirmed_current = false;
        a.certifications_count = 0;
        a.experiences_count = 0;

        const [expResult, certResult, detailResult] = await Promise.allSettled([
          api.get(`/etudiants/${a.id}/experiences`),
          api.get(`/etudiants/${a.id}/certifications`),
          api.get(`/etudiants/${a.id}`),
        ]);

        if (expResult.status === 'fulfilled') {
          const experiences = Array.isArray(expResult.value.data) ? expResult.value.data : [];
          a.experiences_count = experiences.length;
          const best = pickBestExperience(experiences);
          if (best) {
            a.has_confirmed_current = !!best.poste_actuel;
            a.last_experience = {
              company: best.nom_entreprise || '',
              position: best.intitule_poste || '',
              sector: best.secteur_activite || '',
            };
            a.current_company = best.nom_entreprise || a.current_company;
            a.current_position = best.intitule_poste || a.current_position;
            a.sector = best.secteur_activite || a.sector;
          }
        }

        if (certResult.status === 'fulfilled') {
          const certs = Array.isArray(certResult.value.data) ? certResult.value.data : [];
          a.certifications_count = certs.length;
        }

        if (detailResult.status === 'fulfilled') {
          const detail = detailResult.value.data;
          if (Array.isArray(detail?.skills) && detail.skills.length > 0) {
            a.skills = detail.skills;
          }
        }

        return a;
      }),
    );

    return { data: enriched.map((r) => r.status === 'fulfilled' ? r.value : r.reason) };
  },

  getById: async (id) => {
    const res = await api.get(`/etudiants/${id}`);
    return { data: mapBackendToProfile(res.data) };
  },

  create: async (data) => {
    const payload = mapAlumniToBackend(data);
    return api.post('/etudiants/', payload);
  },

  update: (id, data) => {
    const payload = mapAlumniToBackend(data);
    return api.put(`/etudiants/${id}`, payload);
  },

  partialUpdate: async (id, data) => {
    const updates = mapProfileToBackend(data);
    if (updates.availability_status !== undefined && !updates.availability_status) {
      throw { response: { data: { detail: 'Le statut de disponibilité est obligatoire.' } } };
    }
    const res = await api.patch(`/etudiants/${id}`, updates);
    return { data: mapBackendToProfile(res.data) };
  },

  delete: (id, acteur) => api.delete(`/etudiants/${id}`, { params: { acteur } }),

  /** Anonymisation RGPD directe par un admin (hors demande RGPD). */
  anonymise: (id, acteur) => api.post(`/etudiants/${id}/anonymiser`, { acteur }),
};

export const careerAPI = {
  getByAlumni: async (alumniId) => {
    const res = await api.get(`/etudiants/${alumniId}/experiences`);
    const items = Array.isArray(res.data) ? res.data : [];
    return { data: items.map(mapExperienceToCareer) };
  },

  add: (alumniId, data) => {
    const salaryVal = parseFloat(data.salary_range) || 0;
    const payload = {
      intitule_poste: data.position || data.intitule_poste || '',
      type_contrat: data.type_contrat || 'CDI',
      date_debut: toFullDate(data.start_date || data.date_debut) || '2024-01-01',
      date_fin: toFullDate(data.end_date || data.date_fin) || null,
      salaire: salaryVal,
      salary_annuel: salaryVal,
      nom_entreprise: data.company || data.nom_entreprise || '',
      secteur_activite: data.sector || data.secteur_activite || '',
      poste_actuel: data.is_current || data.poste_actuel || false,
      pays: data.pays || '',
      ville: data.ville || '',
    };
    return api.post(`/etudiants/${alumniId}/experiences`, payload);
  },

  update: async (alumniId, careerId, data) => {
    await api.delete(`/experiences/${careerId}`);
    return careerAPI.add(alumniId, data);
  },

  delete: (alumniId, careerId) => api.delete(`/experiences/${careerId}`),

  getCertifications: async (alumniId) => {
    const res = await api.get(`/etudiants/${alumniId}/certifications`);
    const items = Array.isArray(res.data) ? res.data : [];
    return {
      data: items.map((c) => ({
        id: c.id_certification || c.id,
        name: c.nom || c.name || '',
        issuer: c.organisme || c.issuer || '',
        date_obtained: toMonthInput(c.date_obtention || c.date_obtained || ''),
      })),
    };
  },

  addCertification: (alumniId, data) => {
    const payload = {
      nom: data.name || '',
      organisme: data.issuer || '',
      date_obtention: toFullDate(data.date_obtained) || null,
    };
    return api.post(`/etudiants/${alumniId}/certifications`, payload);
  },

  deleteCertification: (alumniId, certId) => api.delete(`/etudiants/${alumniId}/certifications/${certId}`),
};

const CONSENT_TYPES = {
  contact_allowed: 'prise_de_contact',
  data_sharing: 'partage_donnees',
  survey_participation: 'enquetes',
  newsletter: 'newsletter',
};

const CONSENT_TYPE_KEYS = Object.fromEntries(
  Object.entries(CONSENT_TYPES).map(([k, v]) => [v, k]),
);

export const mapBackendConsent = (items) => {
  const defaults = {
    contact_allowed: false,
    data_sharing: false,
    survey_participation: false,
    newsletter: false,
    last_updated: null,
  };
  if (!Array.isArray(items)) return defaults;
  // Pour chaque type, on garde le consentement le PLUS RÉCENT
  // (date la plus grande, puis id le plus grand en cas d'égalité).
  const best = {};
  for (const c of items) {
    const key = CONSENT_TYPE_KEYS[c.type_consentement];
    if (!key) continue;
    const current = best[key];
    const isNewer =
      !current ||
      c.date_consentement > current.date ||
      (c.date_consentement === current.date && (c.id_consentement ?? 0) > current.id);
    if (isNewer) {
      best[key] = {
        date: c.date_consentement,
        id: c.id_consentement ?? 0,
        statut: c.statut,
      };
    }
  }
  let latest = null;
  for (const [key, b] of Object.entries(best)) {
    defaults[key] = b.statut === 'actif';
    if (!latest || b.date > latest) latest = b.date;
  }
  defaults.last_updated = latest;
  return defaults;
};

export const consentAPI = {
  get: async (alumniId) => {
    const res = await api.get(`/consentements/etudiant/${alumniId}`);
    const raw = Array.isArray(res.data) ? res.data : (res.data?.items || []);
    return { data: mapBackendConsent(raw) };
  },

  update: async (alumniId, data) => {
    const today = new Date().toISOString().split('T')[0];
    const results = await Promise.all(
      Object.entries(CONSENT_TYPES).map(([frontendKey, backendType]) =>
        api.post('/consentements/', {
          date_consentement: today,
          type_consentement: backendType,
          statut: data[frontendKey] ? 'actif' : 'refuse',
          canal: 'web',
          id_etudiant: parseInt(alumniId),
        }),
      ),
    );
    return results[results.length - 1];
  },
};

export const adminIdentityAPI = {
  getName: () => localStorage.getItem('admin_name') || '',
  setName: (name) => localStorage.setItem('admin_name', name),
};

const dateFichier = () => new Date().toISOString().split('T')[0];

/** Télécharge l'export au format demandé et renvoie {blob, filename}. */
const telechargerExport = async (url, format, baseNom, optionsRequete = {}) => {
  if (format === 'json') {
    const res = await api.get(url, optionsRequete);
    return {
      blob: new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' }),
      filename: `${baseNom}_${dateFichier()}.json`,
    };
  }
  const res = await api.get(url, {
    ...optionsRequete,
    params: { ...(optionsRequete.params || {}), format },
    responseType: 'blob',
  });
  return { blob: res.data, filename: `${baseNom}_${dateFichier()}.${format}` };
};

export const rgpdAPI = {
  /** Crée une demande RGPD ('export' | 'suppression'). */
  create: async (typeDemande) => {
    ensureAlumniToken();
    const res = await api.post('/rgpd/demandes', { type_demande: typeDemande });
    return res.data;
  },

  /** Liste ses propres demandes. */
  listMine: async () => {
    ensureAlumniToken();
    const res = await api.get('/rgpd/demandes/moi');
    return res.data?.demandes || [];
  },

  /** Annule une demande en attente. */
  cancel: async (idDemande) => {
    ensureAlumniToken();
    await api.delete(`/rgpd/demandes/${idDemande}`);
  },

  /** Export auto-service immédiat (droit d'accès) — format : json|xlsx|csv. */
  exportData: async (format = 'json') => {
    ensureAlumniToken();
    return telechargerExport('/rgpd/export', format, 'mes_donnees_rgpd');
  },
};

export const adminRgpdAPI = {
  /** Liste des demandes RGPD (filtres : statut, type_demande). */
  list: async (params = {}) => {
    const res = await api.get('/admin/demandes-rgpd', { params });
    return res.data?.demandes || [];
  },

  /** Traite (traitee) ou rejette (rejetee) une demande. */
  traiter: async (idDemande, body) => {
    const res = await api.post(`/admin/demandes-rgpd/${idDemande}/traiter`, body);
    return res.data;
  },

  /** Prend la demande en charge : 'envoyee' -> 'en_traitement' (verrou). */
  prendreEnCharge: async (idDemande, traiteePar) => {
    const res = await api.post(`/admin/demandes-rgpd/${idDemande}/prendre-en-charge`, {
      traitee_par: traiteePar,
    });
    return res.data;
  },

  /** Export d'un alumni (vérification / historique admin) — json|xlsx|csv. */
  exportData: async (idDemande, format = 'json') => {
    return telechargerExport(
      `/admin/demandes-rgpd/${idDemande}/export`,
      format,
      `export_rgpd_${idDemande}`,
    );
  },

  /** Traite/rejette en masse (ids: number[], decision: 'traitee'|'rejetee'). */
  bulkTraiter: async (ids, decision, traiteePar, motifRefus = null) => {
    const res = await api.post('/admin/demandes-rgpd/bulk/traiter', {
      ids,
      decision,
      traitee_par: traiteePar,
      motif_refus: motifRefus,
    });
    return res.data;
  },

  /** Suppression définitive en masse. */
  bulkDelete: async (ids) => {
    const res = await api.post('/admin/demandes-rgpd/bulk/delete', { ids });
    return res.data;
  },

  /** Export groupé : json -> {exports, erreurs} ; xlsx/csv -> {blob, filename}. */
  bulkExport: async (ids, format = 'json') => {
    if (format === 'json') {
      const res = await api.post('/admin/demandes-rgpd/bulk/export', { ids });
      return {
        data: res.data,
        blob: new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' }),
        filename: `export_rgpd_groupe_${dateFichier()}.json`,
      };
    }
    const res = await api.post(
      '/admin/demandes-rgpd/bulk/export',
      { ids },
      { params: { format }, responseType: 'blob' },
    );
    return { data: null, blob: res.data, filename: `export_rgpd_groupe_${dateFichier()}.${format}` };
  },

  /** Purge toutes les demandes clôturées (traitee/rejetee). */
  purgeCloturees: async () => {
    const res = await api.post('/admin/demandes-rgpd/purge-cloturees');
    return res.data;
  },
};

export const statsAPI = {
  getDashboard: async () => {
    const res = await api.get('/admin/indicateurs');
    return { data: res.data };
  },

  getKPIs: async () => {
    const res = await api.get('/admin/indicateurs');
    const d = res.data;
    return {
      data: {
        total_alumni: d.total_alumni || 0,
        employment_rate_6m: d.taux_emploi_6mois || 0,
        employment_rate_brut: (() => {
          const promos = d.indicateurs_par_promotion || [];
          const total = promos.reduce((s, i) => s + (i.total_etudiants || 0), 0);
          const enPoste = promos.reduce((s, i) => s + (i.etudiants_en_poste || 0), 0);
          return total > 0 ? Math.round((enPoste / total) * 100) : 0;
        })(),
        avg_response_rate: d.taux_reponse || 0,
        active_alumni: d.alumni_actifs || 0,
        recent_updates: 0,
      },
    };
  },

  /** Tags KPI des questionnaires actifs : [{tag, libelle, pourcentage, nb_repondants, question_type, valeur, unite, libelle_valeur, distribution, detail}, ...]. */
  getKpiTags: async () => {
    const res = await api.get('/admin/indicateurs/kpi-tags');
    return { data: Array.isArray(res.data) ? res.data : [] };
  },

  getByPromotion: async () => {
    const res = await api.get('/admin/indicateurs');
    const indicateurs = res.data.indicateurs_par_promotion || [];
    return {
      data: indicateurs.map((i) => ({
        promotion: i.nom_promotion,
        count: i.total_etudiants,
        percentage: i.total_etudiants > 0
          ? Math.round((i.etudiants_en_poste / i.total_etudiants) * 100)
          : 0,
      })),
    };
  },

  getBySector: async () => {
    const res = await api.get('/admin/indicateurs/secteurs');
    const total = res.data.total_alumni || 0;
    return {
      data: (res.data.secteurs || []).map((s) => ({
        sector: s.secteur || 'Non renseigné',
        count: s.count,
        percentage: total > 0 ? Math.round((s.count / total) * 100) : 0,
        nonRenseigne: s.secteur == null,
      })),
    };
  },

  /** Indicateurs complementaires (cartes bas du Dashboard) : salaire moyen,
   *  taux de couverture et statut de maturite des cohortes a 6 mois. */
  getIndicateursComplementaires: async () => {
    const res = await api.get('/admin/indicateurs');
    const d = res.data || {};
    const promos = d.indicateurs_par_promotion || [];
    const totalEtudiants = promos.reduce((s, p) => s + (p.total_etudiants || 0), 0);
    const avecExp = promos.reduce((s, p) => s + (p.etudiants_avec_experience || 0), 0);
    return {
      data: {
        salaire_moyen: d.salaire_moyen ?? null,
        salaires_renseignes: d.salaires_renseignes || 0,
        // Min/max REELS des salaires renseignes (meme perimetre que le salaire
        // moyen : poste en cours, salaire > 0, alumni non anonymises). Servent
        // a calculer dynamiquement la fourchette de la jauge salaire du
        // Dashboard — aucune fourchette codee en dur, aucune source externe.
        salaire_min: d.salaire_min ?? null,
        salaire_max: d.salaire_max ?? null,
        taux_emploi_6mois_par_promotion: d.taux_emploi_6mois_par_promotion || [],
        total_alumni: d.total_alumni || 0,
        alumni_actifs: d.alumni_actifs || 0,
        taux_couverture: totalEtudiants > 0
          ? Math.round((avecExp / totalEtudiants) * 100)
          : (d.taux_reponse || 0),
      },
    };
  },

  /** Experiences professionnelles EN COURS par type de contrat. */
  getTypesContrat: async () => {
    const res = await api.get('/admin/indicateurs/types-contrat');
    return {
      data: (res.data?.types_contrat || []).map((t) => ({
        type_contrat: t.type_contrat || 'Non renseigné',
        count: t.count,
        nonRenseigne: t.type_contrat == null,
      })),
    };
  },
};

export const questionnaireAPI = {
  getActif: async () => {
    const res = await api.get('/questionnaires/actif');
    return { data: res.data };
  },

  getMesReponses: async (alumniId) => {
    const res = await api.get(`/questionnaires/etudiant/${alumniId}/reponses`);
    return { data: Array.isArray(res.data) ? res.data : [] };
  },

  repondre: async (questionnaireId, alumniId, reponses) => {
    const res = await api.post(`/questionnaires/${questionnaireId}/repondre?id_etudiant=${alumniId}`, { reponses });
    return res.data;
  },

  supprimerReponse: async (questionnaireId, alumniId) => {
    const res = await api.delete(`/questionnaires/${questionnaireId}/repondre?id_etudiant=${alumniId}`);
    return res.data;
  },

  listAll: async () => {
    const res = await api.get('/admin/questionnaires/');
    return { data: Array.isArray(res.data) ? res.data : [] };
  },

  getDetail: async (id) => {
    const res = await api.get(`/admin/questionnaires/${id}`);
    return { data: res.data };
  },

  creer: async (data) => {
    const res = await api.post('/admin/questionnaires/', data);
    return { data: res.data };
  },

  supprimer: async (id) => api.delete(`/admin/questionnaires/${id}`),

  desactiver: async (id) => api.patch(`/admin/questionnaires/${id}/desactiver`),

  reactiver: async (id) => api.patch(`/admin/questionnaires/${id}/reactiver`),

  modifier: async (id, data) => {
    const res = await api.put(`/admin/questionnaires/${id}`, data);
    return { data: res.data };
  },

  getReponses: async (id) => {
    const res = await api.get(`/admin/questionnaires/${id}/reponses`);
    return { data: res.data };
  },
};

export const importAPI = {
  uploadExcel: (formData) =>
    api.post('/import/excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  downloadTemplate: () =>
    api.get('/import/template', { responseType: 'blob' }),
  exportData: (params) =>
    api.get('/import/export/alumni', { params, responseType: 'blob' }),
};

export const promotionsAPI = {
  getAll: async () => {
    const res = await api.get('/promotions/', { params: { limit: 500 } });
    const items = res.data.items || [];
    return {
      data: items.map((p) => ({
        id: p.id_promotion,
        name: p.nom_promotion,
        year: p.annee_diplome,
        filiere: p.filiere,
        nb_etudiants: p.nb_etudiants || 0,
      })),
    };
  },
  create: (data) => api.post('/promotions/', data),
  update: (id, data) => api.put(`/promotions/${id}`, data),
  remove: (id, force = false) =>
    api.delete(`/promotions/${id}`, {
      params: force ? { force: true } : {},
    }),
};

export const loginAPI = {
  requestOTP: async (email) => {
    const normalizedEmail = email.trim().toLowerCase();
    const url = '/auth/otp/request';
    const res = await api.post(url, { email: normalizedEmail });
    return res.data;
  },

  verifyOTP: async (email, code) => {
    const normalizedEmail = email.trim().toLowerCase();
    const res = await api.post('/auth/otp/verify', { email: normalizedEmail, code });
    const { token, alumni, role } = res.data;

    if (token) {
      localStorage.setItem('token', token);
    }

    if (role === 'admin') {
      localStorage.setItem('admin_role', 'admin');
      localStorage.removeItem('alumni_id');
      localStorage.removeItem('alumni_email');
      localStorage.removeItem('alumni_name');
    } else if (alumni) {
      const mapped = mapBackendAlumni(alumni);
      localStorage.setItem('alumni_id', String(mapped.id));
      localStorage.setItem('alumni_email', mapped.email);
      localStorage.setItem('alumni_name', `${mapped.first_name} ${mapped.last_name}`);
      localStorage.removeItem('admin_role');
    }

    return { data: { token, alumni: alumni ? mapBackendAlumni(alumni) : null, role } };
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('alumni_id');
    localStorage.removeItem('alumni_email');
    localStorage.removeItem('alumni_name');
    localStorage.removeItem('admin_role');
  },

  getCurrentUser: () => {
    const id = localStorage.getItem('alumni_id');
    if (!id) return null;
    return {
      id,
      email: localStorage.getItem('alumni_email') || '',
      name: localStorage.getItem('alumni_name') || '',
    };
  },

  isAdmin: () => localStorage.getItem('admin_role') === 'admin',

  adminLogin: async (code) => {
    const res = await api.post('/auth/admin/login', { code });
    const { token, role } = res.data;

    if (token) {
      localStorage.setItem('token', token);
    }

    localStorage.setItem('admin_role', role || 'admin');
    localStorage.removeItem('alumni_id');
    localStorage.removeItem('alumni_email');
    localStorage.removeItem('alumni_name');

    return { data: { token, role: role || 'admin' } };
  },
};

export default api;
