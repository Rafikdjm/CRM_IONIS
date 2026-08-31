# Cartographie des Fonctionnalités — Alumni CRM

> Vue d'ensemble des fonctionnalités de l'application, côté **administration** et côté **alumni**.

---

## 🔐 Authentification

- Connexion par email → **code OTP** (vérifié côté backend).
- Espaces séparés : **admin** (JWT admin) et **alumni** (JWT alumni).
- **Inscription alumni** en 3 sections (infos personnelles / parcours académique / réseaux sociaux) avec stepper de progression et validation à la volée.

---

## 👨‍💼 Espace ADMINISTRATION — `/admin`

Menu : **Dashboard · Annuaire · Promotions · Import/Export · Questionnaires · Demandes RGPD**

### 1. Dashboard (`GET /admin/indicateurs`, `/secteurs`, `/kpi-tags`, `/types-contrat`)
- **KPI cards** : Total Alumni actifs, Taux d'emploi 6 mois, Taux d'emploi global, Taux de complétion.
- **Indicateurs d'enquête** générés depuis les tags KPI des questions actives.
- **Graphiques** : donut des secteurs, barres des promotions (avec maturité des cohortes), jauge salaire moyen, barres des types de contrat.

### 2. Annuaire (`/admin/etudiants/filtrer`, `/etudiants/{id}`, `/etudiants/{id}/anonymiser`, ...)
- Recherche + **filtres** : promotion, secteur, entreprise, disponibilité, contact autorisé, statut du compte, compétence.
- **Tri** sur les colonnes.
- **Actions** : Modifier (modal complet), Anonymiser (RGPD, conserve un compte pour les indicateurs), Supprimer définitivement (doublons/erreurs uniquement), Voir le détail.

### 3. Promotions (CRUD complet — `/promotions/`)
- Ajouter / Modifier / Supprimer.
- Suppression en cascade avec avertissement irréversible si la promotion contient des étudiants (409 → modal de confirmation).

### 4. Import / Export (`/import/excel`, `/import/export/alumni`, `/import/template`)
- **Upload Excel/CSV** d'une liste d'admis avec drag & drop, aperçu des 10 premières lignes, coloration des en-têtes (vert = reconnue, orange = ignorée), compte rendu d'import.
- **Télécharger le modèle** et **Exporter** les données.

### 5. Questionnaires
- Créer / Modifier / Activer-Désactiver / Supprimer un questionnaire annuel.
- Éditeur de questions : texte, choix multiple, oui/non, note 1-5, **tag KPI optionnel**, **conditionnement au statut d'emploi**.
- **Voir les réponses** des alumnis.

### 6. Demandes RGPD
- Suivi des demandes (export / suppression) avec filtres.
- Workflow : **Prendre en charge → Traiter / Rejeter**, actions groupées, **purge des demandes clôturées** et **purge définitive des comptes anonymisés** (délai 6 mois).

---

## 👤 Espace ALUMNI — `/alumni`

Menu : **Mon Profil · Mon Parcours · RGPD & Consentement · Enquête annuelle**

### 1. Mon Profil (`GET/PATCH /etudiants/{id}`)
- Édition : nom, prénom, contact, adresse, LinkedIn, parcours antérieur.
- **Statut de disponibilité** (obligatoire) : En poste / À l'écoute / En recherche active.
- **Secteur** en lecture seule (déduit de l'expérience) ; **compétences** en tags.

### 2. Mon Parcours (`/etudiants/{id}/experiences`, `/certifications`)
- **CRUD des expériences** : entreprise, poste, type de contrat, secteur (avec « Autre » à préciser), salaire, ville/pays, dates, case « poste actuel » (désactive la date de fin).
- **CRUD des certifications**.
- **Blocage des modifications si le compte est anonymisé (RGPD)**.

### 3. RGPD & Consentement
- **4 interrupteurs de consentement** : prise de contact, partage partenaires, enquêtes, newsletter (`/consentements/`).
- **Export de ses données** (droit d'accès) en JSON / Excel / CSV (`GET /rgpd/export`).
- **Demande de suppression** de compte (droit à l'effacement) avec confirmation (`POST /rgpd/demandes`).
- **Suivi de ses demandes** (`GET /rgpd/demandes/moi`) + rappel des droits RGPD et durée de conservation (6 mois après anonymisation).

### 4. Enquête annuelle
- Répondre au **questionnaire actif** (types : texte, choix, oui/non, note 1-5), pré-remplissage de la dernière réponse.
- Questions conditionnées masquées si en recherche active.
- **Blocage si le consentement aux enquêtes est refusé** (403).
- Endpoints : `GET /questionnaires/actif`, `POST /questionnaires/{id}/repondre`, ...

---

## 🔁 Interactions

- Le **dashboard admin** est alimenté par les données des **alumni** (profil, parcours, enquêtes).
- L'**anonymisation RGPD** retire un alumni de tous les indicateurs.
- L'identité alumni est lue dans `localStorage`, le token JWT ajouté automatiquement par l'intercepteur axios.
