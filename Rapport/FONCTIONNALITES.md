# Cartographie des Fonctionnalités — Alumni CRM (Frontend)

> Vue exhaustive des fonctionnalités de l'application web, côté **administration** et côté **alumni**, avec les routes, actions utilisateur et endpoints associés.

---

## 🔐 Authentification (commune)

- **Connexion** par email → **code OTP** (vérifié côté backend) ; aperçu du code en environnement de développement.
- **Connexion admin** séparée (JWT admin) et **connexion alumni** (JWT alumni).
- **Inscription alumni** en 3 sections (informations personnelles / parcours académique / réseaux sociaux) avec :
  - Stepper de progression visuel (cercles + barre + compteur `X/3 complété`)
  - Validation à la volée (bordure rouge/verte après `blur`)
  - Pré-remplissage automatique de l'email académique à partir du prénom + nom

---

## 👨‍💼 Espace ADMINISTRATION — `/admin`

Menu : **Dashboard · Annuaire · Promotions · Import/Export · Questionnaires · Demandes RGPD**

### 1. Dashboard (lecture / visualisation)
| Élément | Détail |
|---|---|
| Carte hero | Total Alumni actifs + micro-répartition (avec/sans expérience) |
| KPI cards | Taux d'emploi à 6 mois, Taux d'emploi global, Alumni actifs, Taux de complétion (compteurs animés) |
| Indicateurs d'enquête | Cartes générées dynamiquement depuis les tags KPI (distribution / étoiles) |
| Répartition par secteur | Graphique en donut |
| Alumni par promotion | Barres verticales (ou horizontales si 1 seule promo) + timeline de maturité des cohortes |
| Indicateurs complémentaires | Jauge salaire moyen (fourchette calculée dynamiquement sur données réelles), anneau de couverture, barres des types de contrat, badge fraîcheur |

- Endpoints appelés : `GET /admin/indicateurs`, `/admin/indicateurs/secteurs`, `/admin/indicateurs/kpi-tags`, `/admin/indicateurs/types-contrat`.

### 2. Annuaire
- **Recherche** libre + **filtres** : promotion, secteur (avec champ « Autre » à préciser), entreprise, disponibilité, contact autorisé, statut du compte (actifs/anonymisés), compétence.
- **Tri** sur les colonnes (asc/desc).
- Colonnes : Nom, Prénom, Email, Promotion, Entreprise, Poste, Secteur, Disponibilité, Contact, Certifications, Compétences, Actions.
- **Actions par ligne** :
  - **Modifier** → modal d'édition complète (nom, prénom, email, téléphone, dates, promotion, disponibilité, secteur, compétences, ville/pays, LinkedIn, adresse, parcours antérieur).
  - **Anonymiser** (RGPD) → confirmation, conserve un compte anonymisé pour les indicateurs agrégés.
  - **Supprimer définitivement** (menu ⋮) → réservé aux doublons/erreurs de saisie (action irréversible).
  - **Voir détail** → fiche read-only : profil, expériences, certifications, compétences.

- Endpoints : `GET /admin/etudiants/filtrer`, `GET/PUT/PATCH/DELETE /etudiants/{id}`, `POST /etudiants/{id}/anonymiser`, `GET /etudiants/{id}/experiences`, `GET /etudiants/{id}/certifications`, `GET /promotions/?limit=500`.

### 3. Promotions (CRUD complet)
- **Ajouter / Modifier / Supprimer** une promotion (nom, année de diplôme, filière).
- **Suppression en cascade forcée** : si la promotion contient des étudiants, l'API renvoie un 409 → modal rouge d'avertissement irréversible avec nombre d'étudiants.
- Endpoints : `GET/POST /promotions/`, `PUT/DELETE /promotions/{id}`, `DELETE /promotions/{id}?force=true`.

### 4. Import / Export
- **Upload Excel/CSV** d'une liste d'admis (26 colonnes attendues) avec :
  - Drag & drop + sélection de fichier (`.xlsx, .xls, .csv`)
  - Aperçu des 10 premières lignes, coloration des en-têtes (vert = reconnue, orange = ignorée)
  - Compte rendu d'import (succès / erreurs ligne par ligne)
- **Télécharger le modèle** Excel et **Exporter** les données (backup client si backend indisponible).
- Endpoints : `POST /import/excel`, `GET /import/export/alumni`, `GET /import/template`.

### 5. Questionnaires (enquêtes envoyées aux alumni)
- **Créer / Modifier / Désactiver / Réactiver / Supprimer** un questionnaire annuel.
- Éditeur de questions : texte libre, choix multiple (avec options), oui/non, note 1-5, **tag KPI optionnel**, **conditionnement au statut d'emploi**.
- **Voir les réponses** : liste des répondants (nom, email, date, réponses + questions).

### 6. Demandes RGPD
- Suivi des demandes (export / suppression) avec filtres par statut et type.
- Workflow complet :
  - **Prendre en charge** (verrou)
  - **Traiter** (la suppression → anonymisation irréversible)
  - **Rejeter** (avec motif)
  - **Actions groupées** (traiter, rejeter, exporter, supprimer en masse)
- **Purge des demandes clôturées** et **purge définitive des comptes anonymisés** (aperçu → délai 6 mois → confirmation).

---

## 👤 Espace ALUMNI — `/alumni`

Menu : **Mon Profil · Mon Parcours · RGPD & Consentement · Enquête annuelle**

### 1. Mon Profil
- Édition complète : nom, prénom, email, téléphone, adresse, ville, pays, LinkedIn, date de naissance, email académique, parcours antérieur.
- **Statut de disponibilité** (obligatoire) : En poste / À l'écoute / En recherche active (radio).
- **Secteur** affiché en lecture seule (déduit de l'expérience).
- **Compétences** en tags (ajout par Entrée, suppression).
- Endpoints : `GET /etudiants/{id}`, `PATCH /etudiants/{id}`.

### 2. Mon Parcours
- **CRUD des expériences professionnelles** : entreprise, poste, type de contrat (CDI/CDD/Freelance/Alternance/Stage/Intérim/Autre), secteur (avec « Autre » à préciser), tranche salariale annuelle, ville/pays, dates (mois), description, **case « poste actuel »** (désactive et vide la date de fin).
- **CRUD des certifications** (nom, organisme, date).
- Confirmation modale avant suppression, avertissement « poste actuel manquant » si statut « en poste ».
- **Blocage total des modifications si le compte est anonymisé (RGPD)**.
- Endpoints : `GET/POST /etudiants/{id}/experiences`, `DELETE /experiences/{id}`, `GET/POST /etudiants/{id}/certifications`, `DELETE /etudiants/{id}/certifications/{id}`.

### 3. RGPD & Consentement
- **4 interrupteurs de consentement** (`role=switch`) :
  - Prise de contact (recommandé)
  - Partage des données partenaires
  - Participation aux enquêtes
  - Newsletter
  - Endpoint : `GET /consentements/etudiant/{id}`, `POST /consentements/`.
- **Export de ses données** (droit d'accès) au format JSON / Excel / CSV → téléchargement ; trace enregistrée dans les demandes.
  - Endpoint : `GET /rgpd/export`.
- **Demande de suppression de compte** (droit à l'effacement) avec confirmation, bloquée si une demande est déjà en attente.
  - Endpoint : `POST /rgpd/demandes`, `DELETE /rgpd/demandes/{id}`.
- **Suivi de ses demandes** : statut, traité par, annulation si en attente.
  - Endpoint : `GET /rgpd/demandes/moi`.
- Rappel des droits RGPD (accès, rectification, effacement, retrait du consentement), durée de conservation (6 mois après anonymisation), contact DPO.

### 4. Enquête annuelle
- Répondre au **questionnaire actif** (types : texte, choix, oui/non, note 1-5).
- **Pré-remplissage** avec la dernière réponse enregistrée, **modifier** ou **supprimer** sa réponse.
- **Questions conditionnées au statut d'emploi** masquées si en recherche active (→ enregistrées « Non applicable »).
- **Blocage si le consentement aux enquêtes est refusé** (403).
- Contrôle de complétude avant envoi ; message « N question(s) restante(s) ».
- Endpoints : `GET /questionnaires/actif`, `GET /questionnaires/etudiant/{id}/reponses`, `POST/DELETE /questionnaires/{id}/repondre?id_etudiant={id}`.

---

## 🔁 Interactions cross (alumni → admin → dashboard)

- Le **dashboard admin** est alimenté par les données renseignées par les **alumni** (profil, parcours, enquêtes) : taux d'emploi, salaire, adéquation, secteurs, types de contrat.
- Le **RGPD** (anonymisation côté admin, suppression/export côté alumni) retire automatiquement un alumni de tous les indicateurs.
- Tous les composants lisent `alumni_id` depuis `localStorage` ; le token JWT est ajouté automatiquement en en-tête par l'intercepteur axios.
