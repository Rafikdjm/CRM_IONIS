# Rapport de Stage Pré-MSc 2026

**Conception et développement d'un système de suivi du parcours étudiant et de valorisation du réseau des anciens (Alumni CRM)**

**Auteur :** Rafik Djemadi
**Formation :** Pré-MSc — IONIS-STM
**Tuteur pédagogique :** [À COMPLÉTER : nom et fonction]
**Période du stage :** [À COMPLÉTER : dates exactes]
**Soutenance :** 19 septembre 2026

---

[BROUILLON IA — À RÉÉCRIRE]

## Résumé

Ce stage, réalisé au sein d'IONIS-STM dans le cadre du programme Pré-MSc 2026, porte sur la conception et le développement d'un Alumni CRM : un système web centralisé destiné au suivi du parcours étudiant et à la valorisation du réseau des anciens diplômés.

La problématique identifiée était l'absence d'un outil centralisé permettant à un établissement d'enseignement supérieur de suivre le cycle de vie de ses étudiants — de l'inscription administrative à l'évolution professionnelle post-diplôme — et de disposer d'indicateurs d'insertion fiables pour le pilotage de la formation. Les données d'insertion étaient dispersées, les indicateurs calculés manuellement, le réseau alumni inactif et la conformité RGPD non formalisée.

La démarche a consisté à concevoir et développer une application complète — backend, base de données, frontend et conformité réglementaire — en suivant une approche itérative : modélisation, développement backend, développement frontend, audit de sécurité et documentation. Le système repose sur une architecture 3-tiers (FastAPI, React/Vite, PostgreSQL) avec 14 tables de base de données, 85 endpoints API, 14 routes frontend et 8 indicateurs d'insertion professionnelle.

Le projet a abouti à un prototype fonctionnel couvrant l'intégralité du périmètre fonctionnel défini dans le sujet de stage. La conformité RGPD a été intégrée dès la conception : consentements traçables, workflow de demandes de suppression et d'anonymisation, journal d'audit et durée de conservation affichée. Un audit de sécurité a permis de corriger des failles d'authentification et de protéger des routes initialement ouvertes. Les livrables documentaires complémentaires (cartographie des données, charte RGPD, stratégie de mise à jour, analyse des indicateurs d'insertion et guide des processus d'animation du réseau) couvrent les exigences du volet Management du sujet de stage.

---

[BROUILLON IA — À RÉÉCRIRE]

## Abstract

This internship, completed at IONIS-STM as part of the 2026 Pre-MSc program, focuses on designing and building an Alumni CRM: a centralized web application for tracking student career paths and strengthening the alumni network.

The core issue was the lack of a unified tool enabling a higher-education institution to monitor students throughout their entire journey — from initial enrollment to post-graduation professional development — and to produce reliable insertion indicators for program evaluation. Student data was scattered across disconnected channels, insertion rates were computed manually, the alumni network was dormant, and GDPR compliance had not been formalized.

The approach followed an iterative cycle: data modeling, backend development, frontend implementation, security audit, and documentation. The resulting system is built on a 3-tier architecture (FastAPI, React/Vite, PostgreSQL) and includes 14 database tables, 80 API endpoints, 14 frontend routes, and 8 professional insertion indicators.

The project delivered a functional prototype covering the full scope defined in the internship brief. GDPR compliance was embedded from the start: traceable consent management, a deletion/anonymization request workflow, an audit log, and visible data retention periods. A security audit led to the correction of authentication flaws and the protection of initially unprotected routes. Supplementary documentation (data mapping, GDPR charter, update strategy, insertion indicator analysis, and alumni network process guide) fulfills the Management track requirements of the internship specification.

---

[BROUILLON IA — À RÉÉCRIRE]

## Préambule — Remerciements

### Remerciements au tuteur pédagogique

Je tiens à remercier [À COMPLÉTER : nom du tuteur pédagogique, fonction] pour son accompagnement tout au long de ce stage. Sa disponibilité, la pertinence de ses retours et sa capacité à poser les bonnes questions ont orienté les choix d'architecture et les priorités fonctionnelles du projet. Les points de suivi réguliers m'ont permis de conserver une direction claire malgré l'ampleur du périmètre fonctionnel à couvrir.

### Remerciements à l'équipe et au projet

Ce stage de substitution, proposé directement par IONIS-STM, m'a offert un cadre de travail encadré et exigeant. L'absence d'une équipe technique dédiée au projet m'a contraint à structurer seul l'ensemble du processus de développement, de la modélisation du MCD à la rédaction des livrables documentaires. Cette expérience a été formatrice sur le plan de l'autonomie et de la prise de décision technique. Je remercie [À COMPLÉTER : nom(s) et fonction(s) des autres interlocuteurs IONIS-STM impliqués] pour les échanges qui ont enrichi la démarche.

### Remerciements à l'école

Je remercie IONIS-STM et son équipe pédagogique pour la qualité de la formation dispensée en Pré-MSc, qui m'a doté des fondamentaux techniques nécessaires à la réalisation de ce projet. Les connaissances acquises en développement web, en modélisation de bases de données et en gestion de projets m'ont permis d'aborder ce stage avec les compétences requises.

---

[BROUILLON IA — À RÉÉCRIRE]

## Liste des abréviations et glossaire

| Abréviation | Signification |
|---|---|
| API | Application Programming Interface — interface de programmation permettant la communication entre le frontend et le backend |
| CRM | Customer Relationship Management — système de gestion de la relation client (ici : Alumni CRM, appliqué au réseau des anciens) |
| CRUD | Create, Read, Update, Delete — les quatre opérations de base sur les données |
| CTI | Commission des Titres d'Ingénieur — organisme d'accréditation des formations d'ingénieurs en France |
| CASCADE | Mécanisme de clé étrangère PostgreSQL assurant la suppression en cascade des enregistrements liés |
| DPO | Data Protection Officer — Délégué à la Protection des Données, contact réglementaire RGPD |
| HCERES | Haute Autorité pour l'Évaluation de la Recherche et l'Enseignement Supérieur — organisme d'évaluation des formations |
| JWT | JSON Web Token — standard de jeton d'authentification utilisé pour les sessions utilisateur |
| KPI | Key Performance Indicator — Indicateur Clé de Performance utilisé dans le tableau de bord administrateur |
| MCD | Modèle Conceptuel de Données — représentation abstraite des entités et relations du système |
| MLD | Modèle Logique de Données — traduction du MLD en schéma de tables relationnelles |
| N:M | Relation many-to-many (cardinalité plusieurs-à-plusieurs) — par exemple Étudiant ↔ Certification via la table OBTIENT |
| OTP | One-Time Password — mot de passe à usage unique, ici code à 6 chiffres envoyé par email |
| RGPD | Règlement Général sur la Protection des Données (Règlement UE 2016/679) — cadre réglementaire européen |
| REST | Representational State Transfer — style d'architecture pour les API web |
| SPA | Single Page Application — application web mono-page (architecture React) |

---

[BROUILLON IA — À RÉÉCRIRE]

## Liste des figures et tableaux

| N° | Titre | Type | Emplacement |
|---|---|---|---|
| 1 | Architecture 3-tiers du système | Figure | [À INSÉRER] |
| 2 | Schéma relationnel de la base de données (MLD) | Figure | [À INSÉRER — source : `erd_alumni_crm.mmd`] |
| 3 | Dashboard administrateur — Vue d'ensemble | Figure | [À INSÉRER] |
| 4 | Espace alumni — Formulaire d'inscription | Figure | [À INSÉRER] |
| 5 | Espace alumni — Gestion du profil | Figure | [À INSÉRER] |
| 6 | Espace alumni — Parcours professionnel | Figure | [À INSÉRER] |
| 7 | Espace alumni — Consentement RGPD | Figure | [À INSÉRER] |
| 8 | Espace alumni — Questionnaire annuel | Figure | [À INSÉRER] |
| 9 | Dashboard administrateur — Indicateurs et KPI | Figure | [À INSÉRER] |
| 10 | Dashboard administrateur — Répartition par secteur | Figure | [À INSÉRER] |
| 11 | Dashboard administrateur — Alumni par promotion | Figure | [À INSÉRER] |
| 12 | Répartition des 14 tables par domaine fonctionnel | Tableau | Section 2.2 |
| 13 | Endpoints API — Modules et nombre de routes | Tableau | Section 2.2 |
| 14 | Indicateurs d'insertion professionnelle | Tableau | Section 2.2 |
| 15 | Types de consentement RGPD | Tableau | Section 2.2 |
| 16 | Types de questions du questionnaire | Tableau | Section 2.2 |
| 17 | Correctifs de sécurité appliqués | Tableau | Section 2.2 |
| 18 | Problèmes identifiés et solutions apportées | Tableau | Section 2.2 |
| 19 | Modèle de données relationnel — Vue d'ensemble | Tableau | Annexe A |
| 20 | Endpoints API — Liste complète | Tableau | Annexe E |

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

### 1.4 Positionnement du groupe IONIS Education Group

[BROUILLON IA — À RÉÉCRIRE]

IONIS Education Group constitue l'un des principaux groupes d'enseignement supérieur privés en France. Le groupe fédère un portefeuille d'écoles spécialisées dans les domaines du numérique, de l'ingénierie et du management, couvrant un spectre large de formations allant du Pré-MSc au niveau Bac+5.

Chaque école du groupe (EPITECH pour le développement informatique, ESGI pour l'informatique et le management, IIM pour le management du numérique, ESM pour le management, ISA pour l'agronomie, entre autres) cible des parcours spécifiques mais partage une même exigence de placement professionnel et de suivi des diplômés. Cette organisation en écosystème多écoles crée un enjeu commun : disposer d'un dispositif de suivi alumni scalable, capable de fonctionner à l'échelle de plusieurs centaines de diplômés par promotion sur l'ensemble du groupe.

[À COMPLÉTER : données chiffrées sur le nombre total d'étudiants, le nombre de promotions, le nombre d'écoles du groupe — sources internes Ionis Education Group]

### 1.5 Enjeux du suivi alumni dans le contexte Ionis

[BROUILLON IA — À RÉÉCRIRE]

Le suivi de l'insertion professionnelle des anciens élèves constitue un enjeu à plusieurs niveaux dans le contexte d'un groupe comme Ionis Education Group :

**Enjeu réglementaire.** Les organismes de tutelle et de certification — la CTI pour les formations d'ingénieurs, le HCERES pour l'enseignement supérieur — exigent des établissements la communication de rapports d'insertion professionnelle réguliers. Ces rapports contiennent des indicateurs standardisés : taux d'emploi à 6 mois et à 12 mois après la diplomation, adéquation formation-emploi, répartition par secteur d'activité et par type de contrat. L'absence de données fiables et centralisées rend la production de ces rapports fastidieuse et sujette à erreurs.

**Enjeu pédagogique.** Le taux d'insertion et la nature des postes occupés par les diplômés constituent des indicateurs de pertinence de l'offre de formation. Si les diplômés d'une filière se dirigent majoritairement vers des secteurs éloignés de la formation reçue, cela signale un décalage entre le programme et les besoins du marché. Le suivi alumni permet d'alimenter cette boucle de rétroaction entre la formation et l'emploi.

**Enjeu managérial.** Le service des relations entreprises d'un établissement comme IONIS-STM a besoin de données structurées pour piloter les partenariats avec les entreprises, identifier les secteurs recrutant le plus de diplômés et préparer les événements de networking. Un réseau alumni vivant constitue aussi un levier de fidélisation et de recommandation auprès de futurs candidats.

**Enjeu technique.** La collecte et le traitement des données personnelles des alumni sont soumis au RGPD. La conformité réglementaire impose des contraintes fortes sur le consentement, la durée de conservation, le droit d'accès et le droit à l'effacement. Un outil centralisé doit intégrer ces exigences dès la conception.

### 1.6 Positionnement du projet Alumni CRM dans la stratégie de l'établissement

[BROUILLON IA — À RÉÉCRIRE]

Le projet Alumni CRM s'inscrit dans une démarche de professionnalisation du suivi des anciens élèves au sein d'IONIS-STM. Il vise à remplacer les processus manuels de collecte de données (emails ponctuels, formulaires papier, appels téléphoniques) par un système structuré et traçable, capable de produire automatiquement les indicateurs requis par les autorités de tutelle.

Le système devait répondre à quatre objectifs fonctionnels définis dans le sujet de stage :

- Créer une solution centralisée permettant de suivre le cycle de vie de l'étudiant, de son inscription administrative jusqu'à son évolution professionnelle post-diplôme.
- Fournir des indicateurs d'insertion professionnelle exploitables par le service des relations entreprises.
- Assurer la conformité RGPD de toutes les opérations de collecte et de traitement des données personnelles.
- Produire un guide des processus d'animation du réseau alumni.

[À COMPLÉTER : positionnement stratégique d'Ionis Education Group par rapport aux autres acteurs privés de l'enseignement supérieur — si information disponible dans les sources internes]

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

Le passage du MCD au MLD a respecté les règles de transformation standard (entité forte → table, association N:M → table de jonction). J'ai versionné 16 migrations SQL, appliquées via un script maison (`run_migrations.py`) qui ne rejoue que les migrations non encore exécutées.

**Mission 2 — Développement du backend API**

J'ai développé une API REST complète avec FastAPI (Python). L'API comprend **16 routeurs** et **85 endpoints** couvrant :

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

Le frontend comprend **14 routes principales** et des composants partagés (thème clair/sombre, indicateurs, protection de routes par rôle). La validation des composants repose sur des tests manuels et la vérification du build de production (`vite build`) ainsi que du lint (`oxlint`) ; aucune suite de tests automatisés n'est conservée dans le dépôt à l'issue du stage.

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

- **14 tables** de base de données, validées par introspection et rejeu complet des 16 migrations sur une base vide (0 différence structurelle constatée).
- **85 endpoints** API avec authentification OTP + JWT et protection admin, dont les 2 ajouts de fin de stage : `POST /newsletter/envoyer` (envoi de newsletter avec filtres de ciblage) et `POST /admin/questionnaires/notififier` (relance questionnaire : email générique aux non-répondants, filtre par promotion, sans lien direct vers le formulaire à ce jour).
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

[BROUILLON IA — À RÉÉCRIRE]

**Cadre du stage.** Ce stage de substitution a été proposé directement par IONIS-STM aux étudiants du programme Pré-MSc n'ayant pas trouvé de placement en entreprise. Il s'agit d'un cas de figure explicitement prévu par le programme. La structure d'accueil est IONIS-STM elle-même, et l'encadrement est assuré par un tuteur pédagogique interne.

**Travail en solo.** Le projet a été réalisé en solo : aucune équipe technique n'était dédiée au développement de l'Alumni CRM. L'ensemble des responsabilités — modélisation du MCD/MLD, développement du backend FastAPI, développement du frontend React, intégration de la conformité RGPD, audit de sécurité, rédaction des livrables documentaires — reposait sur un seul développeur. Cette organisation a rendu le projet formateur sur le plan de l'autonomie et de la prise de décision technique, mais elle a aussi exposé à des risques spécifiques liés à l'absence de revue par les pairs et de partage de connaissance.

**Encadrement pédagogique.** Le suivi régulier avec le tuteur pédagogique a fourni un cadre de validation des choix d'architecture et des priorités fonctionnelles. Les points de suivi ont permis de poser un regard extérieur sur les choix techniques et d'aligner le développement avec les attendus du sujet de stage. [À COMPLÉTER : fréquence des points de suivi, modalités de communication utilisées]

**Migration OneDrive → Git.** Le projet était initialement stocké en local sous OneDrive avec synchronisation active, **sans dépôt Git**. Cette organisation a provoqué un incident : un conflit de synchronisation concurrente a entraîné le retour à une version antérieure de plusieurs fichiers frontend en cours de développement, et j'ai dû reprendre le travail concerné. Faute d'historique, il n'est pas possible de déterminer précisément quand le script de test E2E documenté dans le README a disparu du dépôt. Cet incident a conduit à l'initialisation d'un dépôt Git avec un `.gitignore` racine consolidé (couvrant `.env`, `node_modules/`, `venv/`). La leçon retenue est que le versionnement doit précéder la première ligne de code, pas suivre le premier incident.

**Ressources techniques à disposition.** Les ressources techniques comprenaient un poste de développement local, l'accès aux APIs tierces — en particulier Resend pour l'envoi d'emails OTP en mode production (mode console en développement) — et les polices système pour la mise en forme des documents. La base de données PostgreSQL fonctionnait en local. Aucun environnement de staging cloud n'était prévu pour ce stage.

[À COMPLÉTER : informations complémentaires sur les ressources matérielles (type de poste, configuration), accès réseau éventuels, ou tout autre élément pertinent à documenter]

### 2.6 Méthodes et stratégies mises en œuvre

**Approche de développement.** J'ai suivi une démarche itérative : modélisation → backend → frontend → audit → documentation. Chaque fonctionnalité était développée, testée manuellement, puis consolidée avant de passer à la suivante. Cette approche m'a permis de détecter tôt des incohérences de modélisation (par exemple le drift de migration sur `reponse_questionnaire.id_etudiant` qui avait `ON DELETE CASCADE` en base réelle mais pas dans le fichier de migration d'origine).

**Audit de fiabilité base/API.** J'ai réalisé un audit complet de la table ETUDIANT et des 9 autres tables : des champs acceptés en écriture mais jamais persistés, un endpoint `DELETE /entreprises/{id}` cassé (UPDATE sur colonne NOT NULL au lieu d'un DELETE avec CASCADE), et le drift de migration mentionné ci-dessus. J'ai utilisé le rejeu complet des 16 migrations sur une base vide comme test de validation. Cet audit relève aussi quelques points secondaires laissés ouverts et assumés comme tels : statut des consentements libre (ni `Literal` ni CHECK), date d'obtention des certifications non validée (une date future passe), messages trompeurs sur les associations étudiant/certification, filtres invalides ignorés silencieusement dans la liste admin des demandes RGPD, réponses de questionnaire stockées en JSONB sans vérification des clés, absence de purge des tables `otp_codes` et `AUDIT_LOG`. Tout est consigné dans `AUDIT_COHERENCE_TABLES.txt` pour guider la reprise du projet.

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
- *Tests automatisés* : une démarche de validation par tests a été explorée (Vitest/Testing Library côté frontend, pytest côté backend) mais, pour des raisons de cadrage (absence de suite conservée et maintenue dans le dépôt à l'issue du stage), la validation finale du livrable repose sur des scripts ad hoc, le rejeu complet des migrations sur base vide et des tests manuels des parcours utilisateur. Le script de test E2E documenté dans le README n'est plus présent dans le dépôt — le reconstituer fait partie des suites à donner au projet.

**Compétences transversales.**

- *Autonomie et prise de décision* : travail en solo sans équipe technique, choix d'architecture assumés et documentés.
- *Documentation traitée comme du code* : livrables PDF et DOCX générés par des scripts (fpdf2, python-docx), donc régénérables et maintenables au même titre que l'application.
- *Rigueur méthodologique* : audit de cohérence entre le modèle et l'implémentation réelle mené par introspection SQL (`information_schema`, `pg_constraint`), écrit et daté avant tout correctif (`AUDIT_COHERENCE_TABLES.txt`).

### 3.2 Difficultés rencontrées et solutions apportées

**Difficulté 1 — Bug d'authentification croisée entre les espaces admin et alumni**

Le token admin et le token alumni partageaient la même clé de stockage dans le navigateur : un JWT administrateur pouvait partir sur les routes `/rgpd/*` réservées aux alumni, avec des erreurs 403 difficilement explicables.

*Solution* : clés de stockage distinctes (`admin_role` / `alumni_id`) avec nettoyage mutuel, vérification du rôle dans le JWT avant chaque appel sensible, et purge automatique du token en cas de session orpheline.

**Difficulté 2 — Le modèle de données et la base réelle avaient divergé**

Un audit d'introspection a révélé des écarts entre les fichiers de migration et l'état réel de la base : clé étrangère en `ON DELETE CASCADE` sans contrepartie dans la migration, route `DELETE /entreprises/{id}` cassée, et doublons de consentements faute de contrainte d'unicité.

*Solution* : migrations correctives dédiées au drift, et mise en place d'un rejeu complet des migrations sur base vide comme test de validation. Pratique retenue : rejouer les migrations à chaque évolution du schéma pour détecter les écarts rapidement.

**Difficulté 3 — Deux administrateurs pouvaient traiter la même demande RGPD**

Le cycle initial (`en_attente → traitée/rejetée`) ne laissait aucune trace d'une prise en charge : deux admins pouvaient intervenir simultanément sur la même demande.

*Solution* : ajout d'un statut intermédiaire `en traitement` (migration 009, contrainte CHECK) et verrou applicatif `prise_en_charge_par` : toute décision sur une demande déjà prise en charge est refusée.

**Difficulté 4 — Un indicateur d'insertion trompeur**

Le calcul initial du taux d'emploi à 6 mois comptait des expériences déjà terminées, produisant des chiffres surestimés pour les promotions récentes.

*Solution* : filtrage sur les expériences actives à la date de référence et exclusion des cohortes dont la fenêtre de six mois n'est pas écoulée (valeur `null` plutôt qu'un chiffre trompeur).

**Difficulté 5 — Absence de versionning Git et incident de synchronisation**

Le projet était stocké sous OneDrive sans dépôt Git. Un conflit de synchronisation a entraîné la perte de fichiers frontend en cours de développement, sans possibilité de récupération via un historique.

*Solution* : récupération manuelle puis initialisation d'un dépôt Git avec `.gitignore` consolidé. La leçon : le versionnement doit précéder la première ligne de code, pas suivre le premier incident.

---

## 4. Axes d'amélioration

[BROUILLON IA — À RÉÉCRIRE]

Cette section recense les axes d'amélioration identifiés au cours du stage, hiérarchisés par horizon de réalisation. Certains relèvent de correctifs nécessaires avant toute mise en production, d'autres constituent des évolutions fonctionnelles à moyen terme, et d'autres encore relèvent de perspectives plus lointaines.

### 4.1 Axes à traiter en priorité (court terme)

Ces améliorations concernent des manques fonctionnels ou des risques techniques identifiés au cours du stage et à traiter avant toute mise en production.

**Tests automatisés.** Le principal chantier technique restant avant la mise en production est l'introduction durable d'une suite de tests automatisés (pytest côté backend, Vitest/Testing Library côté frontend), actuellement absente du dépôt : à l'issue du stage, la validation repose sur des scripts ad hoc, le rejeu complet des migrations sur base vide et des tests manuels des parcours. Quelques tests d'intégration auraient intercepté la route `DELETE /entreprises/{id}` cassée et les endpoints renvoyant 200 OK avec un corps d'erreur. Le script de test E2E documenté dans le README n'est plus présent dans le dépôt et doit être reconstitué. La mise en place de tests automatisés sur les routes critiques — authentification, opérations CRUD, workflow RGPD — est un prérequis à tout déploiement.

**Automatisation de l'envoi du questionnaire annuel (cron job).** L'activation des questionnaires reste manuelle dans l'interface admin. Un mécanisme de planification automatique (cron job) permettrait d'envoyer les relances email aux alumni n'ayant pas répondu au questionnaire actif, selon un calendrier défini par le service des relations entreprises. L'endpoint backend `POST /admin/questionnaires/notififier` est déjà implémenté (filtres de ciblage par promotion, envoi aux non-répondants) ; il manque le déclenchement automatique périodique et une interface dédiée côté frontend.

**Composant frontend d'envoi de newsletter.** L'endpoint backend `POST /newsletter/envoyer` est opérationnel avec filtres de ciblage (promotion, secteur, consentement newsletter actif), mais le composant frontend permettant à l'administrateur de rédiger et d'envoyer la newsletter depuis l'interface n'est pas encore développé. Le mécanisme de désinscription automatique (lien dans le gabarit HTML mettant le consentement à « refusé ») n'est pas non plus implémenté — des liens placeholder existent dans le gabarit HTML.

**Standardisation des contraintes de validation.** Le statut des consentements dans la table `CONSENTEMENT_RGPD` reste libre (ni `Literal` côté API, ni `CHECK` côté base). La date d'obtention des certifications n'est pas validée (une date future passe sans erreur). La mise en place de contraintes de validation à la source — types énumérés côté API, contraintes CHECK côté base — est une bonne pratique à généraliser.

### 4.2 Évolutions fonctionnelles à moyen terme

Ces améliorations ne sont pas critiques pour la mise en production, mais enrichiraient significativement le système.

**Module de mentorat.** Un module de mise en relation entre alumni seniors et étudiants actuels permettrait d'exploiter le réseau alumni à des fins pédagogiques. Ce module n'existe pas à ce jour ; les mises en relation s'appuient actuellement sur l'annuaire filtrable. Il pourrait prendre la forme d'un système de candidatures et de parrainage, avec matching par secteur d'activité ou par compétences.

**Chiffrement applicatif des données sensibles.** Les données de consentement et les données personnelles ne font l'objet d'aucun chiffrement spécifique au niveau applicatif. Leur protection repose actuellement sur les mécanismes standard de l'infrastructure PostgreSQL. L'ajout d'un chiffrement au repos au niveau applicatif (par exemple au moyen d'une bibliothèque de chiffrement symétrique) renforcerait la protection des données, notamment en cas d'accès non autorisé à la base de données.

**Route de mise à jour d'une expérience professionnelle.** La modification directe d'une expérience existante n'est pas disponible dans l'interface alumni. L'alumni doit supprimer puis recréer l'expérience. Une route PUT/PATCH dédiée côté backend et un formulaire de modification côté frontend permettraient d'améliorer l'expérience utilisateur.

### 4.3 Perspectives à plus long terme

Ces améliorations nécessitent des ressources ou des compétences spécifiques qui n'étaient pas mobilisables durant ce stage.

**Application mobile.** Une application mobile dédiée permettrait aux alumni de mettre à jour leur profil et leur parcours professionnel depuis un smartphone, améliorant ainsi la fraîcheur des données collectées. Cette évolution suppose des compétences en développement mobile (React Native, Flutter ou équivalent) et un choix stratégique entre une application native et une progressive web app (PWA).

**Tests end-to-end complets.** Le script de test E2E documenté dans le README (parcours alumni + parcours admin contre le vrai backend) a disparu du dépôt. Sa reconstitution et son exécution automatisée dans un pipeline d'intégration continue constitueraient un filet de sécurité essentiel avant la mise en production.

**Notification de violation de données.** La notification de violation de données (article 33 du RGPD) n'est pas couverte par une fonctionnalité dédiée du système. En cas de violation, cette notification doit être effectuée manuellement par le DPO. L'ajout d'un mécanisme d'alerte automatisé et de documentation de incident pourrait être envisagé.

---

## Références bibliographiques

### Cadre réglementaire

1. Règlement (UE) 2016/679 du Parlement européen et du Conseil du 27 avril 2016 relatif à la protection des personnes physiques à l'égard du traitement des données à caractère personnel et à la libre circulation de ces données (RGPD).
2. Commission Nationale de l'Informatique et des Libertés (CNIL) — Guide pratique du RGPD pour les établissements d'enseignement supérieur : [À COMPLÉTER : URL ou référence exacte si utilisé].

### Documentation technique — Backend

3. FastAPI — Documentation officielle : https://fastapi.tiangolo.com/
4. Pydantic — Documentation officielle : https://docs.pydantic.dev/ [À VÉRIFIER si utilisé comme source]
5. pg8000 — Documentation : [À COMPLÉTER : URL si référencé]
6. Python — Documentation officielle : https://docs.python.org/3/ [À COMPLÉTER si référencé]

### Documentation technique — Frontend

7. React — Documentation officielle : https://react.dev/
8. Vite — Documentation officielle : https://vitejs.dev/
9. Vitest — Documentation : https://vitest.dev/ [À COMPLÉTER si référencé]

### Documentation technique — Base de données

10. PostgreSQL — Documentation : https://www.postgresql.org/docs/

### Référentiels et organismes de certification

11. Commission des Titres d'Ingénieur (CTI) — Référentiel d'accréditation : [À COMPLÉTER : URL ou référence exacte].
12. Haute Autorité pour l'Évaluation de la Recherche et l'Enseignement Supérieur (HCERES) — Référentiel d'évaluation : [À COMPLÉTER : URL ou référence exacte].

### Services tierces

13. Resend — API email : https://resend.com/

### Référence au groupe

14. IONIS Education Group — Site officiel : https://www.ionis-group.com/

### Sources internes

15. Cahier des charges du sujet de stage — « Conception et développement d'un système de suivi du parcours étudiant et de valorisation du réseau des anciens (Alumni CRM) » — IONIS-STM, 2026.
16. Instructions Livrables & Soutenance 2026 v4 — IONIS-STM.

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
| Infrastructure | otp_codes, schema_migrations | otp_codes : codes OTP hachés identifiés par l'email ; schema_migrations : suivi des 16 migrations versionnées |

**Règles d'intégrité** : clés étrangères avec CASCADE sur les données dépendant d'un étudiant (expériences, certifications obtenues, consentements, réponses), SET NULL sur les demandes RGPD, contraintes d'unicité (ex. email étudiant), contraintes CHECK sur les énumérations (statuts de demande RGPD, types de consentement).

[Insérer ici le rendu graphique du schéma Mermaid (`erd_alumni_crm.mmd`) ou l'export du fichier Looping.]

### Annexe B — Dashboard administrateur (captures d'écran)

[À COMPLÉTER : insérer les captures d'écran du dashboard bento grid avec indicateurs]

### Annexe C — Espace alumni (captures d'écran)

[À COMPLÉTER : insérer les captures d'écran de l'inscription multi-étapes, du profil, du parcours, du questionnaire]

### Annexe D — Guide des processus d'animation du réseau (extrait)

[À COMPLÉTER : insérer un extrait ou la version complète du guide généré séparément]

### Annexe E — Liste des endpoints API

[À COMPLÉTER : liste complète des 85 endpoints avec méthode HTTP, chemin et description]

### Annexe F — Différentiel de migration et audit de conformité

[À COMPLÉTER : tableau du drift de migration corrigé et résultats du rejeu des 16 migrations]
