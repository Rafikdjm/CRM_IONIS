# Rapport de Stage Pré-MSc 2026

**Conception et développement d'un système de suivi du parcours étudiant et de valorisation du réseau des anciens (Alumni CRM)**

**Auteur :** Rafik Djemadi
**Formation :** Pré-MSc — IONIS-STM
**Tuteur pédagogique :** [À COMPLÉTER : nom et fonction]
**Période du stage :** [À COMPLÉTER : dates exactes]
**Soutenance :** 19 septembre 2026

---

## Résumé

Ce stage, réalisé au sein d'IONIS-STM dans le cadre du programme Pré-MSc 2026, porte sur la conception et le développement d'un Alumni CRM : un système web centralisé destiné au suivi du parcours étudiant et à la valorisation du réseau des anciens diplômés.

Mon objectif était de construire une application complète — backend, base de données, frontend et conformité réglementaire — pour qu'un établissement d'enseignement supérieur puisse gérer le cycle de vie de ses étudiants, de l'inscription administrative à l'évolution professionnelle post-diplôme. Le système devait aussi fournir des indicateurs d'insertion professionnelle exploitables par le service des relations entreprises.

Le projet a abouti à un prototype fonctionnel reposant sur une architecture 3-tiers (FastAPI, React/Vite, PostgreSQL), avec 14 tables de base de données, 80 endpoints API, un tableau de bord administrateur et un espace alumni complet. J'ai intégré la conformité RGPD dès la conception : consentements traçables, workflow de demandes de suppression/anonymisation, journal d'audit, durée de conservation affichée et contact DPO. Un audit de sécurité m'a permis de corriger des failles d'authentification, de protéger des routes initialement ouvertes et de rotater une clé API exposée. J'ai enfin doté le système des dernières briques attendues : endpoint de newsletter avec filtres de ciblage, champ salaire numérique pour les calculs statistiques, relances automatiques pour les questionnaires, et dépôt Git initialisé.

Ce stage m'a permis de développer des compétences en développement web full-stack, en modélisation de bases de données relationnelles et en ingénierie des données personnelles. J'ai aussi identifié des axes d'amélioration concrets pour la pérennité du système.

---

## Abstract

This internship, completed at IONIS-STM as part of the 2026 Pre-MSc program, focuses on designing and building an Alumni CRM: a centralized web application for tracking student paths and strengthening the alumni network.

The main objective was to develop a full-stack application — backend, database, frontend and regulatory compliance — enabling a higher education institution to manage the complete student lifecycle, from administrative enrollment to post-graduation career progression. The system also needed to provide professional insertion indicators for the corporate relations department.

The project delivered a functional prototype based on a 3-tier architecture (FastAPI, React/Vite, PostgreSQL), featuring 14 database tables, 80 API endpoints, an admin dashboard and a complete alumni portal. GDPR compliance was built in from the start: auditable consent management, a workflow for deletion/anonymization requests, an audit log, data retention information and a DPO contact. A security audit led to the correction of authentication flaws, the protection of initially unprotected routes and the rotation of an exposed API key. Finally, I completed the system with its remaining building blocks: a newsletter endpoint with targeting filters, a numeric salary field for statistical calculations, automatic questionnaire reminders, and an initialized Git repository.

This internship allowed me to develop skills in full-stack web development, relational database design, and personal data engineering, while identifying concrete areas for improvement to ensure the system's long-term viability.

---

## Remerciements

Je tiens à remercier [À COMPLÉTER : nom du tuteur pédagogique, fonction] pour son accompagnement tout au long de ce stage, pour la pertinence de ses retours et sa disponibilité. Je remercie également [À COMPLÉTER : nom(s) et fonction(s) des autres interlocuteurs IONIS-STM impliqués] pour les échanges qui ont orienté les choix techniques et fonctionnels du projet.

Ce stage de substitution, proposé directement par IONIS-STM, m'a offert un cadre de travail encadré et exigeant. L'absence d'une équipe technique dédiée m'a contraint à structurer seul l'ensemble du processus de développement, de la modélisation à la documentation — une expérience formatrice sur le plan de l'autonomie et de la prise de décision technique.

---

## Liste des abréviations et glossaire

| Abréviation | Signification |
|---|---|
| API | Application Programming Interface |
| CRM | Customer Relationship Management (ici : Alumni CRM) |
| CTI | Commission des Titres d'Ingénieur |
| CRUD | Create, Read, Update, Delete |
| DPO | Data Protection Officer (Délégué à la Protection des Données) |
| HCERES | Haute Autorité pour l'Évaluation de la Recherche et l'Enseignement Supérieur |
| JWT | JSON Web Token |
| KPI | Key Performance Indicator (Indicateur Clé de Performance) |
| MCD | Modèle Conceptuel de Données |
| MLD | Modèle Logique de Données |
| N:M | Relation many-to-many (cardinalité plusieurs-à-plusieurs) |
| OTP | One-Time Password (mot de passe à usage unique) |
| RGPD | Règlement Général sur la Protection des Données (Règlement UE 2016/679) |
| REST | Representational State Transfer |
| SPA | Single Page Application |

---

## Liste des figures et tableaux

| N° | Titre | Type |
|---|---|---|
| 1 | Architecture 3-tiers du système | Figure |
| 2 | Schéma relationnel de la base de données (MLD) | Figure |
| 3 | Dashboard administrateur — Vue d'ensemble | Figure |
| 4 | Espace alumni — Formulaire d'inscription | Figure |
| 5 | Répartition des 14 tables par domaine fonctionnel | Tableau |
| 6 | Endpoints API — Modules et nombre de routes | Tableau |
| 7 | Indicateurs d'insertion professionnelle | Tableau |
| 8 | Types de consentement RGPD | Tableau |
| 9 | Types de questions du questionnaire | Tableau |
| 10 | Correctifs de sécurité appliqués | Tableau |

---

## 1. Contexte de la structure d'accueil

### 1.1 Présentation d'IONIS-STM

IONIS-STM est une école du groupe IONIS Education Group, acteur privé de l'enseignement supérieur en France. Le groupe regroupe plusieurs écoles d'ingénieurs et de management (EPITECH, ESGI, ESM, ISA, IIM, ISEN, ICS, entre autres), couvrant les domaines du numérique, de l'ingénierie et du management.

IONIS-STM dispense des programmes de niveau Pré-MSc, MSc1 et MSc2, ciblant des étudiants en reconversion ou en poursuite d'études après un diplôme initial. Les formations sont organisées en filières spécialisées et débouchent sur des métiers du développement, de la cybersécurité, de la data, du management et du marketing digital.

L'établissement forme chaque année plusieurs centaines de diplômés. Suivre l'insertion professionnelle de ces anciens élèves est un enjeu stratégique pour piloter la formation, respecter les exigences des organismes de tutelle (CTI, HCERES) et animer le réseau alumni.

### 1.2 Secteur d'activité et acteurs clés

Le secteur de l'enseignement supérieur privé en France se caractérise par une concurrence croissante entre établissements pour attirer les candidats, garantir l'employabilité des diplômés et maintenir des relations durables avec les entreprises partenaires. Les acteurs clés dans ce contexte sont :

- **Les étudiants et alumni** : bénéficiaires des formations, dont la trajectoire professionnelle est le principal indicateur de qualité.
- **Le service des relations entreprises** : responsable du placement, des partenariats et du suivi de l'insertion.
- **La direction pédagogique** : pilote l'offre de formation au regard des besoins du marché.
- **Les organismes de certification** (CTI, HCERES) : exigent des rapports d'insertion réguliers comme condition de accréditation.

### 1.3 Problématique spécifique du projet

L'absence d'un outil centralisé de suivi alumni posait plusieurs problèmes concrets au sein d'IONIS-STM :

1. **Données dispersées** : les informations d'insertion étaient collectées ponctuellement (par email, formulaire papier, appels téléphoniques) sans stockage structuré ni traçabilité.
2. **Indicateurs non fiables** : le calcul des taux d'insertion (à 6 mois, à 12 mois) nécessitait des croisements manuels fastidieux, propices aux erreurs.
3. **Réseau inanimé** : aucun canal structuré ne permettait aux anciens diplômés de maintenir leur profil à jour ni de rester en contact avec l'école.
4. **Conformité RGPD non formalisée** : la collecte et le traitement des données personnelles des alumni n'obéissaient à aucun workflow traçable.

La problématique du stage était donc de concevoir et développer un système capable de répondre simultanément à ces quatre problèmes, tout en étant conforme aux exigences réglementaires et en fournissant des indicateurs exploitables pour le pilotage.

---

## 2. Présentation du stage et déroulement des missions

### 2.1 Contexte et objectifs du stage

Ce stage est un **stage de substitution**, proposé directement par IONIS-STM aux étudiants n'ayant pas trouvé de placement en entreprise. C'est un cas de figure explicitement prévu par le programme Pré-MSc. La structure d'accueil est IONIS-STM elle-même, et l'encadrement est assuré par un tuteur pédagogique interne.

Le sujet officiel du stage est : *« Conception et développement d'un système de suivi du parcours étudiant et de valorisation du réseau des anciens (Alumni CRM) »*.

Les objectifs fonctionnels du projet, définis dans le sujet officiel, étaient :

- Créer une solution centralisée permettant de suivre le cycle de vie de l'étudiant, de son inscription administrative jusqu'à son évolution professionnelle post-diplôme.
- Fournir des indicateurs d'insertion professionnelle exploitables par le service des relations entreprises.
- Assurer la conformité RGPD de toutes les opérations de collecte et de traitement des données personnelles.
- Produire un guide des processus d'animation du réseau alumni.

Les livrables attendus étaient : le rapport de stage, le schéma conceptuel MCD/MLD, un prototype fonctionnel, et le guide des processus d'animation du réseau.

### 2.2 Missions confiées et responsabilités

Le stage s'est articulé autour de **cinq domaines de mission** :

**Mission 1 — Modélisation et conception de la base de données**

J'ai conçu un modèle de données relationnel couvrant cinq domaines fonctionnels : données étudiantes, parcours professionnel, conformité RGPD, questionnaires et infrastructure technique. Le résultat est une base PostgreSQL de **14 tables** organisées en 5 groupes :

- *Données étudiantes* : ETUDIANT, PROMOTION
- *Parcours professionnel* : ENTREPRISE, EXPERIENCE_PRO, CERTIFICATION, OBTIENT (association N:M)
- *RGPD* : CONSENTEMENT_RGPD, DEMANDE_RGPD, AUDIT_LOG
- *Questionnaires* : QUESTIONNAIRE, QUESTION, REPONSE_QUESTIONNAIRE
- *Infrastructure* : otp_codes, schema_migrations

Le passage du MCD au MLD a respecté les règles de transformation standard (entité forte → table, association N:M → table de jonction). J'ai versionné 13 migrations SQL, appliquées via un script maison (`run_migrations.py`) qui ne rejoue que les migrations non encore exécutées.

**Mission 2 — Développement du backend API**

J'ai développé une API REST complète avec FastAPI (Python). L'API comprend **16 routeurs** et **80 endpoints** couvrant :

- Authentification (OTP email + code à 6 chiffres, clé d'accès API admin, sessions JWT)
- Gestion des promotions et des étudiants/alumni (CRUD complet)
- Entreprises et expériences professionnelles (CRUD avec création automatique de l'entreprise si inexistante)
- Certifications (catalogue + association N:M)
- RGPD (consentement, demandes de suppression/anonymisation, journal d'audit)
- Questionnaires (CRUD admin + soumission alumni avec validation des clés)
- Dashboard administrateur (indicateurs, statistiques, filtrage, évolution temporelle)
- Import/export (template Excel, import alumni CSV/Excel avec détection automatique du séparateur, export complet)
- Nettoyage (détection d'orphelins, fusion de doublons, archivage, purge différée)

**Mission 3 — Développement du frontend React**

J'ai développé une interface utilisateur complète avec React + Vite, structurée en deux espaces :

- *Espace administrateur* : tableau de bord avec KPI et graphiques, annuaire filtrable, gestion des promotions, import/export Excel, gestion des questionnaires, traitement des demandes RGPD.
- *Espace alumni* : inscription multi-étapes, vérification OTP, édition de profil, parcours professionnel (expériences et certifications, gérées par ajout/suppression — la modification directe d'une expérience existante n'est pas disponible à ce jour, limite assumée du prototype ; une route de mise à jour reste à créer), consentement RGPD, questionnaire annuel.

Le frontend comprend **14 routes principales** et des composants partagés (thème clair/sombre, indicateurs, protection de routes par rôle). La couche de tests compte 14 fichiers (Vitest + Testing Library, dossier `src/__tests__`).

**Mission 4 — Conformité RGPD et audit de sécurité**

J'ai intégré la conformité RGPD à toutes les étapes du système :

- 4 types de consentement gérés indépendamment via des toggles : prise de contact, partage de données, enquêtes, newsletter.
- Workflow de traitement des demandes RGPD : statut `envoyée → en cours de traitement → traitée/rejetée`, avec verrou anti-double-traitement.
- Exports de données (droit d'accès et portabilité) téléchargeables aux formats JSON, Excel (.xlsx) ou CSV : auto-service côté alumni (`GET /rgpd/export`), unitaire et groupé côté admin, avec une section « Erreurs » dans l'export groupé pour les comptes introuvables ou anonymisés.
- Distinction entre anonymisation (RGPD, réversible) et suppression définitive (hard delete, réservée aux doublons).
- Purge différée configurable (`PURGE_DELAY_MONTHS`, défaut 6 mois).
- Information de l'alumni dans l'interface de consentement : durée de conservation des données (suppression 6 mois après anonymisation) et contact DPO (`dpo@ionis-stm.com`).

Un audit de sécurité m'a permis de corriger des failles critiques :

- Ajout de `require_admin_api_key` sur les routes POST/DELETE de promotions et entreprises initialement non protégées.
- Suppression de la route morte `/upload-etudiants/` (router `automatisation.py`, resté sans appelant front, sans test ni générateur de fichier) : l'import alumni passe désormais exclusivement par l'import Excel, protégé par la dépendance `require_admin_api_key` posée au niveau du router.
- Correction d'une faille d'ownership : un alumni pouvait lire/modifier les réponses d'un autre alumni en modifiant un ID dans la requête → corrigé via `require_owner_or_admin`.
- Protection des routes permettant la modification de comptes déjà anonymisés via le garde `refuser_compte_anonymise` (12 points d'appel : PUT/PATCH étudiant, expériences, certifications, consentements, réponses questionnaire).
- `DELETE /promotions/{id}` renvoie désormais 409 si des étudiants sont rattachés (sauf `?force=true`).

> **Note :** La clé `ADMIN_API_KEY` a été exposée par erreur dans une capture d'écran pendant une session de travail. Elle doit être changée avant tout déploiement en production.

**Mission 5 — Indicateurs d'insertion et documentation**

J'ai défini et implémenté **8 indicateurs d'insertion professionnelle** avec formule et source précise :

| Indicateur | Formule / Source |
|---|---|
| Taux d'emploi à 6 mois | Expériences actives à la date de référence ÷ total alumni |
| Taux d'emploi global brut | (Alumni avec expérience ÷ total alumni) × 100 |
| Adéquation formation/emploi | Réponses à la question taguée `adequation_formation` |
| Salaire moyen | Calculé sur `salary_annuel` (NUMERIC) avec repli sur le champ texte historique ; moyennes par promotion exposées |
| Alumni actifs | Alumni avec ≥ 1 expérience enregistrée |
| Taux de complétion | Alumni ayant complété profil + parcours |
| Alumni par promotion | Comptage par id_promotion |
| Répartition par secteur | Agrégation du champ secteur_activite |

Le calcul du taux d'emploi à 6 mois a nécessité une **fiabilisation** : l'ancien calcul comptait des expériences déjà terminées (surestimation), le nouveau ne retient que les expériences actives à la date de référence et exclut les cohortes trop récentes (valeur `null` plutôt que trompeuse).

### 2.3 Résultats obtenus et impact des actions menées

Le prototype résultant de ce stage couvre l'intégralité du périmètre fonctionnel défini dans le sujet officiel :

- **14 tables** de base de données, validées par introspection et rejeu complet des 13 migrations sur une base vide (0 différence structurelle constatée).
- **80 endpoints** API avec authentification OTP + JWT et protection admin, dont les 2 ajouts de fin de stage : `POST /newsletter/envoyer` (envoi de newsletter avec filtres de ciblage) et `POST /admin/questionnaires/notififier` (relance questionnaire : email générique aux non-répondants, filtre par promotion, sans lien direct vers le formulaire à ce jour).
- **14 routes** frontend couvrant les espaces admin et alumni.
- **8 indicateurs** d'insertion professionnelle, dont 6 exposés via des endpoints dédiés (`/admin/indicateurs`, `/admin/indicateurs/secteurs`, `/admin/indicateurs/types-contrat`, `/admin/indicateurs/kpi-tag`, `/admin/indicateurs/kpi-tags`, `/admin/indicateurs/kpi-tags-actifs`).
- **5 documents** de livraison complémentaires, couvrant les exigences « Management » du sujet : cartographie des données (exigence M1), charte RGPD (M2), analyse des indicateurs d'insertion (M4), stratégie de mise à jour des données — porteuse de l'exigence M3 (questionnaire annuel automatisé et newsletter) —, et guide des processus d'animation du réseau (livrable attendu du sujet).

Un élément que je souligne est le **système de tags KPI** : chaque question de questionnaire peut être étiquetée (ex. `adequation_formation`) pour alimenter automatiquement un indicateur de pilotage. Ce mécanisme est extensible — ajouter un tag à une question fait apparaître l'indicateur correspondant dans le tableau de bord administrateur sans modification du code backend.

### 2.4 Réponse à la problématique initiale

Le système répond aux quatre problèmes identifiés dans la section 1.3 :

| Problème | Solution apportée |
|---|---|
| Données dispersées | Base centralisée de 14 tables avec import Excel/CSV |
| Indicateurs non fiables | 8 indicateurs automatisés, fiabilisés par filtrage temporel |
| Réseau inanimé | Espace alumni avec inscription, profil, parcours, questionnaire annuel, newsletter |
| Conformité RGPD non formalisée | Consentements traçables, workflow de demandes, journal d'audit, durée de conservation, contact DPO |

### 2.5 Organisation du travail en équipe et ressources à disposition

J'ai réalisé ce stage **en solo** : il n'y avait pas d'équipe technique dédiée au projet. Le suivi régulier avec le tuteur pédagogique m'a fourni un cadre de validation des choix d'architecture et des priorités fonctionnelles.

Le projet était stocké en local sous OneDrive avec synchronisation active, **sans dépôt Git**. Cette organisation a provoqué un incident : un conflit de synchronisation concurrente a entraîné le retour à une version antérieure de plusieurs fichiers frontend en cours de développement, et j'ai dû reprendre le travail concerné. Cet incident a conduit à l'initialisation du dépôt Git décrite en section 3.2 (difficulté 6).

Les ressources techniques à disposition comprenaient : un poste de développement local, l'accès aux APIs (Resend pour l'envoi d'OTP email), et les polices système pour la mise en forme des documents.

### 2.6 Méthodes et stratégies mises en œuvre

**Approche de développement.** J'ai suivi une démarche itérative : modélisation → backend → frontend → audit → documentation. Chaque fonctionnalité était développée, testée manuellement, puis consolidée avant de passer à la suivante. Cette approche m'a permis de détecter tôt des incohérences de modélisation (par exemple le drift de migration sur `reponse_questionnaire.id_etudiant` qui avait `ON DELETE CASCADE` en base réelle mais pas dans le fichier de migration d'origine).

**Audit de fiabilité base/API.** J'ai réalisé un audit complet de la table ETUDIANT et des 9 autres tables : des champs acceptés en écriture mais jamais persistés, un endpoint `DELETE /entreprises/{id}` cassé (UPDATE sur colonne NOT NULL au lieu d'un DELETE avec CASCADE), et le drift de migration mentionné ci-dessus. J'ai utilisé le rejeu complet des 13 migrations sur une base vide comme test de validation. Cet audit relève aussi quelques points secondaires laissés ouverts et assumés comme tels : statut des consentements libre (ni `Literal` ni CHECK), date d'obtention des certifications non validée (une date future passe), messages trompeurs sur les associations étudiant/certification, filtres invalides ignorés silencieusement dans la liste admin des demandes RGPD, réponses de questionnaire stockées en JSONB sans vérification des clés, absence de purge des tables `otp_codes` et `AUDIT_LOG`. Tout est consigné dans `AUDIT_COHERENCE_TABLES.txt` pour guider la reprise du projet.

**Modélisation par introspection.** J'ai régénéré le schéma MCD/MLD par introspection réelle de la base (14 tables) plutôt qu'à partir du fichier de conception initial. Cette approche m'a permis de détecter un ancien fichier `mcd_corrige.md` dans le frontend qui s'est révélé obsolète (11 tables au lieu de 14, tables manquantes : DEMANDE_RGPD, OTP_CODES, SCHEMA_MIGRATIONS) ; il a été supprimé depuis.

**Dashboard refondu.** J'ai repensé le tableau de bord administrateur (bento grid, ombres à deux couches, micro-interactions, tooltips CSS) avec de nouveaux indicateurs visuels (jauge salaire, donut de couverture, barres de types de contrat, timeline de maturité des cohortes) — le tout en CSS/SVG pur, sans nouvelle dépendance.

---

## 3. Bilan de l'expérience professionnelle

### 3.1 Compétences acquises lors du stage

**Compétences techniques.**

- *Développement web full-stack* : conception et implémentation d'une application complète avec FastAPI (Python) côté backend et React/Vite côté frontend, communication via API REST JSON. Patterns CRUD, pagination, validation Pydantic et gestion d'état côté client appliqués sur l'ensemble des modules métier.
- *Migrations de base de données* : mise en place d'un système maison de migrations versionnées (`run_migrations.py`, table `schema_migrations`). La principale leçon tient en une règle : une migration déjà appliquée ne se modifie jamais, on corrige par une nouvelle migration. C'est ainsi qu'a été traité le drift de la migration 003, par une migration corrective idempotente (011) qui interroge `pg_constraint` avant d'agir.
- *Sécurité applicative* : correction de failles d'ownership (IDOR), remplacement des vérifications « SELECT puis INSERT » par la gestion des `IntegrityError` (fin des race conditions TOCTOU), sanitisation des messages d'erreur renvoyés aux clients, protection des routes admin par clé API. Mise en place d'un garde centralisé (`refuser_compte_anonymise`) branché sur les 12 points d'écriture capables de réécrire un compte anonymisé, avec une doctrine explicite des routes où il ne doit pas s'appliquer.
- *Gestion des sessions et des rôles* : séparation stricte des sessions admin et alumni côté navigateur (clés distinctes `admin_role` / `alumni_id`), vérification du rôle contenu dans le JWT avant chaque appel sensible, purge d'un token orphelin à la réception d'un 401. Ce dispositif fait suite à un bug concret (section 3.2) et est couvert par les tests.
- *Conception de workflows concurrents* : statut intermédiaire `en_traitement` et verrou `prise_en_charge_par` dans le traitement des demandes RGPD, pour empêcher deux administrateurs de travailler en même temps sur la même demande.
- *Indicateurs statistiques honnêtes* : exposition des hypothèses de calcul dans l'API elle-même (champ `hypothese`) et refus d'afficher un chiffre trompeur — les cohortes dont la fenêtre de six mois n'est pas écoulée renvoient `null` avec un statut `en_attente`.
- *Tests automatisés* : suite Vitest côté frontend (14 fichiers / 117 tests : authentification OTP, consentements, import Excel, routes protégées). Une démarche de test E2E sans mocks (parcours alumni et parcours admin contre le vrai backend) a été conçue et documentée dans le README ; son script n'est en revanche plus présent dans le dépôt — le reconstituer fait partie des suites à donner au projet.

**Compétences transversales.**

- *Autonomie et prise de décision* : travail en solo sans équipe technique, choix d'architecture assumés et documentés.
- *Documentation traitée comme du code* : livrables PDF et DOCX générés par des scripts (fpdf2, python-docx), donc régénérables et maintenables au même titre que l'application.
- *Rigueur méthodologique* : audit de cohérence entre le modèle et l'implémentation réelle mené par introspection SQL (`information_schema`, `pg_constraint`), écrit et daté avant tout correctif (`AUDIT_COHERENCE_TABLES.txt`).

### 3.2 Difficultés rencontrées et solutions apportées

**Difficulté 1 — Bug d'authentification croisée entre les espaces admin et alumni**

Le token admin et le token alumni partageaient la même clé de stockage dans le navigateur : un JWT administrateur pouvait partir sur les routes `/rgpd/*` réservées aux alumni, avec des erreurs 403 difficiles à comprendre.

*Solution* : clés de stockage distinctes (`admin_role` / `alumni_id` avec nettoyage mutuel), vérification du rôle présent dans le payload du JWT avant chaque appel sensible (`ensureAlumniToken`), purge automatique du token en cas de session orpheline (intercepteur sur les réponses 401). Le correctif est couvert par des tests unitaires.

**Difficulté 2 — Le modèle de données et la base réelle avaient divergé**

Un audit d'introspection mené le 16 août a révélé plusieurs écarts. La clé étrangère `reponse_questionnaire.id_etudiant` était en `ON DELETE CASCADE` en base live mais pas dans le fichier de migration 003 : une base reconstruite aurait échoué au premier hard-delete d'un étudiant ayant répondu à un questionnaire. La route `DELETE /entreprises/{id}` renvoyait systématiquement une erreur dès qu'une expérience référençait l'entreprise (mise à jour vers NULL sur une colonne NOT NULL, alors que la clé étrangère est déjà en cascade). Des doublons de consentements s'étaient enfin accumulés faute de contrainte d'unicité.

*Solution* : migration corrective idempotente dédiée au drift (011), suppression directe pour les entreprises (la cascade fait le reste), migration 006 qui dédoublonne puis pose `UNIQUE (id_etudiant, type_consentement)` pour permettre un upsert propre côté API. Le script de rejeu complet des 13 migrations sur base vide est devenu mon test de validation de référence — cette démarche aurait évité un échec de déploiement basé sur un rejeu des migrations. Pratique retenue depuis : rejouer les migrations sur base vide à chaque évolution du schéma, le drift 003 étant resté quatre semaines indétecté. Deux leçons générales tirées de ces épisodes : introduire des tests backend automatisés — principal chantier technique restant avant une mise en production, quelques tests d'intégration auraient intercepté la route `DELETE /entreprises` cassée comme les endpoints renvoyant 200 OK avec un corps d'erreur —, et poser les contraintes de validation à la source (type contraint `Literal` côté API, CHECK côté base dès la création des colonnes énumérables — le statut des consentements reste libre à ce jour).

**Difficulté 3 — Deux administrateurs pouvaient traiter la même demande RGPD**

Le cycle initial (`en_attente → traitée/rejetée`) ne laissait aucune trace d'une prise en charge en cours : deux admins pouvaient décider simultanément de la même demande.

*Solution* : refonte du cycle en `envoyée → en traitement → traitée/rejetée` (migration 009, avec contrainte CHECK) et verrou applicatif `prise_en_charge_par` : toute décision sur une demande déjà prise en charge par un autre administrateur est refusée.

**Difficulté 4 — Un indicateur d'insertion trompeur**

Le calcul initial du taux d'emploi à 6 mois comptait des expériences déjà terminées, et produisait pour les promotions récentes un instantané sans valeur.

*Solution* : filtrage sur les expériences actives à la date de référence (1er décembre de l'année de diplôme, hypothèse explicitée dans la réponse API via le champ `hypothese`), exclusion explicite des cohortes immatures (`null` + statut `en_attente`).

**Difficulté 5 — Gestion de la conformité RGPD en contexte éducatif**

Le RGPD impose des contraintes fortes sur la collecte et le traitement des données personnelles, mais les outils disponibles (tutoriels, documentation) traitent majoritairement le cas des entreprises commerciales. Le contexte éducatif pose des questions spécifiques : durée de conservation des données d'anciens élèves, base légale du traitement (intérêt légitime vs consentement), distinction entre anonymisation et suppression.

*Solution* : j'ai modélisé un workflow de consentement à 4 niveaux avec traçabilité native (table CONSENTEMENT_RGPD), et documenté explicitement les limites assumées (pas de DPO identifié, pas de mécanisme de chiffrement spécifique, pas de notification de violation de données).

**Difficulté 6 — Absence de versionning Git et incident de synchronisation**

Le projet était stocké sous OneDrive sans dépôt Git. Un conflit de synchronisation concurrente a entraîné le retour à une version antérieure de plusieurs fichiers frontend en cours de développement ; j'ai repris ce travail à la main. Faute d'historique, je ne peux d'ailleurs pas dire précisément quand le script de test E2E documenté dans le README a disparu du dépôt.

*Solution* : récupération manuelle des fichiers perdus, puis initialisation d'un dépôt Git avec `.gitignore` racine consolidé (couvrant `.env`, `node_modules/`, `venv/`). La leçon tient en une phrase : le versionnement doit précéder la première ligne de code, pas suivre le premier incident. Pratique retenue : commits réguliers, et rien d'important qui n'existe qu'en un seul exemplaire sur disque.

**Difficulté 7 — Exposition d'une clé d'accès administrateur**

La valeur de `ADMIN_API_KEY` est apparue dans une capture d'écran pendant une session de travail.

*Solution* : rotation immédiate de la clé (l'ancienne valeur est obsolète) et note persistante dans ce rapport tant que l'environnement n'a pas été redéployé proprement. Depuis, règle personnelle : jamais de fichier de secrets ouvert à l'écran pendant un partage.

**Difficulté 8 — Salaire moyen : un indicateur d'abord non automatisable**

Le champ `salary_range` était saisi en texte libre (ex. `"35k-45k EUR"`), ce qui rendait impossible le calcul automatisé du salaire moyen par filière — indicateur pourtant demandé par les organismes de tutelle.

*Solution* : ajout du champ numérique `salary_annuel` (NUMERIC, migration `012_salary_annuel.sql`), alimenté côté frontend par un select de 11 tranches chiffrées (+ option « Non renseigné »). Le backend calcule désormais moyenne, minimum et maximum sur les expériences en cours (`salary_annuel > 0`), avec repli sur l'ancien champ texte pour les données historiques et des moyennes exposées par promotion. Le calcul du salaire moyen par secteur d'activité reste ouvert.

Viennent enfin des perspectives sans épisode vécu associé, documentées dans le guide des processus mais issues d'aucun dysfonctionnement : calendrier automatique d'envoi du questionnaire annuel (cron job), module de mentorat (mise en relation alumni/étudiants actuels), application mobile pour mettre à jour son profil depuis un smartphone, et chiffrement applicatif au repos des données sensibles — ce dernier restant délégué à l'infrastructure PostgreSQL.

---

## Références bibliographiques

1. Règlement (UE) 2016/679 du Parlement européen et du Conseil du 27 avril 2016 relatif à la protection des personnes physiques à l'égard du traitement des données à caractère personnel et à la libre circulation de ces données (RGPD).
2. FastAPI — Documentation officielle : https://fastapi.tiangolo.com/
3. React — Documentation officielle : https://react.dev/
4. PostgreSQL — Documentation : https://www.postgresql.org/docs/
5. Vite — Documentation officielle : https://vitejs.dev/
6. IONIS Education Group — Site officiel : https://www.ionis-group.com/
7. Commission des Titres d'Ingénieur (CTI) — Référentiel d'accréditation.
8. Haute Autorité pour l'Évaluation de la Recherche et l'Enseignement Supérieur (HCERES) — Référentiel d'évaluation.
9. Resend — API email : https://resend.com/

---

## Annexes

### Annexe A — Schéma MCD/MLD complet

Le schéma ci-dessous a été **régénéré par introspection directe de la base PostgreSQL** (14 tables), et non à partir des fichiers de conception initiaux. Les fichiers sources figurent dans le dépôt :

- `alumni_crm_api/docs/erd_alumni_crm.mmd` — définition Mermaid du schéma relationnel (MLD) ;
- `alumni_crm_api/docs/erd_alumni_crm.docx` — version documentée du MLD ;
- `MCD_MLD V2.loo` (racine du dépôt) — modèle Looping (MCD + MLD) issu de la phase de conception.

**Vue d'ensemble des 14 tables et de leurs relations :**

| Domaine | Tables | Relations principales |
|---|---|---|
| Données étudiantes | ETUDIANT, PROMOTION | ETUDIANT.id_promotion → PROMOTION (N:1) |
| Parcours professionnel | ENTREPRISE, EXPERIENCE_PRO, CERTIFICATION, OBTIENT | EXPERIENCE_PRO → ETUDIANT et ENTREPRISE (N:1, avec `salary_annuel NUMERIC`) ; OBTIENT = association N:M ETUDIANT ↔ CERTIFICATION |
| RGPD | CONSENTEMENT_RGPD, DEMANDE_RGPD, AUDIT_LOG | CONSENTEMENT_RGPD → ETUDIANT ; DEMANDE_RGPD → ETUDIANT en SET NULL pour préserver l'historique après anonymisation ; AUDIT_LOG journalise anonymisations, purges et nettoyages |
| Questionnaires | QUESTIONNAIRE, QUESTION, REPONSE_QUESTIONNAIRE | QUESTION → QUESTIONNAIRE (N:1, avec tags KPI) ; REPONSE_QUESTIONNAIRE → ETUDIANT + QUESTIONNAIRE (réponses stockées en JSON) |
| Infrastructure | otp_codes, schema_migrations | otp_codes : codes OTP hachés identifiés par l'email ; schema_migrations : suivi des 13 migrations versionnées |

**Règles d'intégrité** : clés étrangères avec CASCADE sur les données dépendant d'un étudiant (expériences, certifications obtenues, consentements, réponses), SET NULL sur les demandes RGPD, contraintes d'unicité (ex. email étudiant), contraintes CHECK sur les énumérations (statuts de demande RGPD, types de consentement).

[Insérer ici le rendu graphique du schéma Mermaid (`erd_alumni_crm.mmd`) ou l'export du fichier Looping.]

### Annexe B — Dashboard administrateur (captures d'écran)

[À COMPLÉTER : insérer les captures d'écran du dashboard bento grid avec indicateurs]

### Annexe C — Espace alumni (captures d'écran)

[À COMPLÉTER : insérer les captures d'écran de l'inscription multi-étapes, du profil, du parcours, du questionnaire]

### Annexe D — Guide des processus d'animation du réseau (extrait)

[À COMPLÉTER : insérer un extrait ou la version complète du guide généré séparément]

### Annexe E — Liste des endpoints API

[À COMPLÉTER : liste complète des 80 endpoints avec méthode HTTP, chemin et description]

### Annexe F — Différentiel de migration et audit de conformité

[À COMPLÉTER : tableau du drift de migration corrigé et résultats du rejeu des 13 migrations]
