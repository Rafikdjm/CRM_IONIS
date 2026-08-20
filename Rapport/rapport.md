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

Le projet a abouti à un prototype fonctionnel reposant sur une architecture 3-tiers (FastAPI, React/Vite, PostgreSQL), avec 14 tables de base de données, plus de 50 endpoints API, un tableau de bord administrateur et un espace alumni complet. J'ai intégré la conformité RGPD dès la conception : consentements traçables, workflow de demandes de suppression/anonymisation, journal d'audit. Un audit de sécurité m'a permis de corriger des failles d'authentification et de protéger des routes initialement ouvertes.

Ce stage m'a permis de développer des compétences en développement web full-stack, en modélisation de bases de données relationnelles et en ingénierie des données personnelles. J'ai aussi identifié des axes d'amélioration concrets pour la pérennité du système.

---

## Abstract

This internship, completed at IONIS-STM as part of the 2026 Pre-MSc program, focuses on designing and building an Alumni CRM: a centralized web application for tracking student paths and strengthening the alumni network.

The main objective was to develop a full-stack application — backend, database, frontend and regulatory compliance — enabling a higher education institution to manage the complete student lifecycle, from administrative enrollment to post-graduation career progression. The system also needed to provide professional insertion indicators for the corporate relations department.

The project delivered a functional prototype based on a 3-tier architecture (FastAPI, React/Vite, PostgreSQL), featuring 14 database tables, over 50 API endpoints, an admin dashboard and a complete alumni portal. GDPR compliance was built in from the start: auditable consent management, a workflow for deletion/anonymization requests, and an audit log. A security audit led to the correction of authentication flaws and the protection of initially unprotected routes.

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
| 11 | Limites identifiées du projet | Tableau |

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

Le passage du MCD au MLD a respecté les règles de transformation standard (entité forte → table, association N:M → table de jonction). J'ai versionné 12 migrations SQL, appliquées via un script maison (`run_migrations.py`) qui ne rejoue que les migrations non encore exécutées.

**Mission 2 — Développement du backend API**

J'ai développé une API REST complète avec FastAPI (Python), documentée automatiquement via Swagger (`/docs`). L'API comprend **14 routeurs** et **plus de 50 endpoints** couvrant :

- Authentification (OTP email + code à 6 chiffres, clé d'accès API admin, sessions JWT)
- Gestion des promotions et des étudiants/alumni (CRUD complet)
- Entreprises et expériences professionnelles (CRUD avec création automatique de l'entreprise si inexistante)
- Certifications (catalogue + association N:M)
- RGPD (consentement, demandes de suppression/anonymisation, journal d'audit)
- Questionnaires (CRUD admin + soumission alumni avec validation des clés)
- Dashboard administrateur (indicateurs, statistiques, filtrage, évolution temporelle)
- Import/export (template Excel, import alumni, export complet)
- Nettoyage (détection d'orphelins, fusion de doublons, archivage, purge différée)

**Mission 3 — Développement du frontend React**

J'ai développé une interface utilisateur complète avec React + Vite, structurée en deux espaces :

- *Espace administrateur* : tableau de bord avec KPI et graphiques, annuaire filtrable, gestion des promotions, import/export Excel, gestion des questionnaires, traitement des demandes RGPD.
- *Espace alumni* : inscription multi-étapes, vérification OTP, édition de profil, parcours professionnel (expériences + certifications), consentement RGPD, questionnaire annuel.

Le frontend comprend **14 routes principales** et des composants partagés (thème clair/sombre, indicateurs, protection de routes par rôle).

**Mission 4 — Conformité RGPD et audit de sécurité**

J'ai intégré la conformité RGPD à toutes les étapes du système :

- 4 types de consentement gérés indépendamment via des toggles : prise de contact, partage de données, enquêtes, newsletter.
- Workflow de traitement des demandes RGPD : statut `envoyée → en cours de traitement → traitée/rejetée`, avec verrou anti-double-traitement.
- Distinction entre anonymisation (RGPD, réversible) et suppression définitive (hard delete, réservée aux doublons).
- Purge différée configurable (`PURGE_DELAY_MONTHS`, défaut 6 mois).

Un audit de sécurité m'a permis de corriger des failles critiques :

- Ajout de `require_admin_api_key` sur les routes POST/DELETE de promotions et entreprises initialement non protégées.
- Retrait d'un router mort (`automatisation.py`) avec upload pandas non protégé.
- Correction d'une faille d'ownership : un alumni pouvait lire/modifier les réponses d'un autre alumni en modifiant un ID dans la requête → corrigé via `require_owner_or_admin`.
- Protection des 9 routes permettant la modification de comptes déjà anonymisés.
- `DELETE /promotions/{id}` renvoie désormais 409 si des étudiants sont rattachés (sauf `?force=true`).

> **Note :** La clé `ADMIN_API_KEY` a été exposée par erreur dans une capture d'écran pendant une session de travail. Elle doit être changée avant tout déploiement en production.

**Mission 5 — Indicateurs d'insertion et documentation**

J'ai défini et implémenté **8 indicateurs d'insertion professionnelle** avec formule et source précise :

| Indicateur | Formule / Source |
|---|---|
| Taux d'emploi à 6 mois | Expériences actives à la date de référence ÷ total alumni |
| Taux d'emploi global brut | (Alumni avec expérience ÷ total alumni) × 100 |
| Adéquation formation/emploi | Réponses à la question taguée `adequation_formation` |
| Salaire moyen | *Point critique* : saisie texte libre, non automatisable |
| Alumni actifs | Alumni avec ≥ 1 expérience enregistrée |
| Taux de complétion | Alumni ayant completé profil + parcours |
| Alumni par promotion | Comptage par id_promotion |
| Répartition par secteur | Agrégation du champ secteur_activite |

Le calcul du taux d'emploi à 6 mois a nécessité une **fiabilisation** : l'ancien calcul comptait des expériences déjà terminées (surestimation), le nouveau ne retient que les expériences actives à la date de référence et exclut les cohortes trop récentes (valeur `null` plutôt que trompeuse).

### 2.3 Résultats obtenus et impact des actions menées

Le prototype résultant de ce stage couvre l'intégralité du périmètre fonctionnel défini dans le sujet officiel :

- **14 tables** de base de données, validées par introspection et rejeu complet des 12 migrations sur une base vide (0 différence structurelle constatée).
- **50+ endpoints** API documentés via Swagger, avec authentification OTP + JWT et protection admin.
- **14 routes** frontend couvrant les espaces admin et alumni.
- **8 indicateurs** d'insertion professionnelle, dont 3 exposés via des endpoints dédiés (`/admin/indicateurs`, `/admin/indicateurs/secteurs`, `/admin/indicateurs/kpi-tag`).
- **4 documents** de livraison complémentaires : cartographie des données, charte RGPD, stratégie de mise à jour des données, et guide des processus d'animation du réseau.

Un élément que je souligne est le **système de tags KPI** : chaque question de questionnaire peut être étiquetée (ex. `adequation_formation`) pour alimenter automatiquement un indicateur de pilotage. Ce mécanisme est extensible — ajouter un tag à une question fait apparaître l'indicateur correspondant dans le tableau de bord administrateur sans modification du code backend. C'est une innovation par rapport à la conception initiale.

### 2.4 Réponse à la problématique initiale

Le système répond aux quatre problèmes identifiés dans la section 1.3 :

| Problème | Solution apportée |
|---|---|
| Données dispersées | Base centralisée de 14 tables avec import Excel/CSV |
| Indicateurs non fiables | 8 indicateurs automatisés, fiabilisés par filtrage temporel |
| Réseau inanimé | Espace alumni avec inscription, profil, parcours, questionnaire annuel |
| Conformité RGPD non formalisée | Consentements traçables, workflow de demandes, journal d'audit |

La réponse est toutefois partielle sur un point : le mécanisme de **relance des alumni** (newsletter, sollicitation pour mise à jour du profil) n'est pas implémenté techniquement. Le guide des processus documente le processus détaillé (ciblage par consentement, fréquence, contenu, CTA), mais l'endpoint `POST /newsletter/envoyer` reste à développer. C'est le principal manque identifié.

### 2.5 Organisation du travail en équipe et ressources à disposition

J'ai réalisé ce stage **en solo** : il n'y avait pas d'équipe technique dédiée au projet. Le suivi régulier avec le tuteur pédagogique m'a fourni un cadre de validation des choix d'architecture et des priorités fonctionnelles.

Le projet était stocké en local sous OneDrive avec synchronisation active, **sans dépôt Git**. Cette organisation a provoqué un incident : un conflit de synchronisation concurrente a entraîné le retour à une version antérieure de plusieurs fichiers frontend en cours de développement, et j'ai dû reprendre le travail concerné. Cet incident est un axe d'amélioration prioritaire (voir section 4.3).

Les ressources techniques à disposition comprenaient : un poste de développement local, l'accès aux APIs (Resend pour l'envoi d'OTP email), et les polices/se fontes système pour la mise en forme des documents.

### 2.6 Méthodes et stratégies mises en œuvre

**Approche de développement.** J'ai suivi une démarche itérative : modélisation → backend → frontend → audit → documentation. Chaque fonctionnalité était développée, testée manuellement, puis consolidée avant de passer à la suivante. Cette approche m'a permis de détecter tôt des incohérences de modélisation (par exemple le drift de migration sur `reponse_questionnaire.id_etudiant` qui avait `ON DELETE CASCADE` en base réelle mais pas dans le fichier de migration d'origine).

**Audit de fiabilité base/API.** J'ai réalisé un audit complet de la table ETUDIANT et des 9 autres tables : des champs acceptés en écriture mais jamais persistés, un endpoint `DELETE /entreprises/{id}` cassé (UPDATE sur colonne NOT NULL au lieu d'un DELETE avec CASCADE), et le drift de migration mentionné ci-dessus. J'ai utilisé le rejeu complet des 12 migrations sur une base vide comme test de validation.

**Modélisation par introspection.** J'ai régénéré le schéma MCD/MLD par introspection réelle de la base (14 tables) plutôt qu'à partir du fichier de conception initial. Cette approche m'a permis de détecter un ancien fichier `mcd_corrige.md` dans le frontend qui s'est révélé obsolète (11 tables au lieu de 14, tables manquantes : DEMANDE_RGPD, OTP_CODES, SCHEMA_MIGRATIONS).

**Dashboard refondu.** J'ai repensé le tableau de bord administrateur (bento grid, ombres à deux couches, micro-interactions, tooltips CSS) avec de nouveaux indicateurs visuels (jauge salaire, donut de couverture, barres de types de contrat, timeline de maturité des cohortes) — le tout en CSS/SVG pur, sans nouvelle dépendance.

---

## 3. Bilan de l'expérience professionnelle

### 3.1 Compétences acquises lors du stage

**Compétences techniques.**

- *Développement web full-stack* : conception et implémentation d'une application complète avec FastAPI (Python) côté backend et React/Vite côté frontend, communication via API REST JSON. Maîtrise des patterns CRUD, de l'authentification OTP + JWT, et de la gestion d'état côté client.
- *Modélisation de bases de données relationnelles* : passage du MCD au MLD, conception de 14 tables avec règles d'intégrité referentielle (clés étrangères, CASCADE, SET NULL, contraintes UNIQUE). Application des migrations versionnées et détection de drift entre le modèle théorique et la base réelle.
- *Sécurité applicative* : audit de routes non protégées, correction de failles d'ownership (IDOR), protection de comptes anonymisés, gestion de clés API. Compréhension concrète des risques liés à l'exposition accidentelle de secrets.
- *Conformité RGPD* : implémentation opérationnelle des principes de consentement, de traçabilité, de minimisation des données et de droit à l'effacement. Distinction entre anonymisation et suppression, workflow de demandes avec verrou anti-double-traitement.
- *Indicateurs et pilotage* : définition formelle d'indicateurs d'insertion professionnelle (formule, source, périmètre), implémentation côté backend et visualisation côté frontend. Fiabilisation d'un calcul erroné (surestimation du taux d'emploi).

**Compétences transversales.**

- *Autonomie et prise de décision* : travail en solo sans équipe technique, choix d'architecture assumés et documentés.
- *Documentation technique* : production de livrables structurés (cartographie des données, charte RGPD, guide des processus) en parallèle du développement.
- *Rigueur methodologique* : audit de conformité entre le modèle de conception et l'implémentation réelle, détection et correction de drifts de migration.

### 3.2 Difficultés rencontrées et solutions apportées

**Difficulté 1 — Gestion de la conformité RGPD en contexte éducatif**

Le RGPD impose des contraintes fortes sur la collecte et le traitement des données personnelles, mais les outils disponibles (tutoriels, documentation) traitent majoritairement le cas des entreprises commerciales. Le contexte éducatif pose des questions spécifiques : durée de conservation des données d'anciens élèves, base légale du traitement (intérêt légitime vs consentement), distinction entre anonymisation et suppression.

*Solution* : j'ai modélisé un workflow de consentement à 4 niveaux avec traçabilité native (table CONSENTEMENT_RGPD), et documenté explicitement les limites assumées (pas de DPO identifié, pas de mécanisme de chiffrement spécifique, pas de notification de violation de données).

**Difficulté 2 — Fiabilisation de la base de données**

L'audit a révélé plusieurs incohérences entre le modèle de conception et l'implémentation réelle : des champs acceptés en écriture mais jamais persistés, un endpoint `DELETE` cassé, et un drift de migration critique (`reponse_questionnaire.id_etudiant` avec `ON DELETE CASCADE` en base mais pas dans le fichier de migration).

*Solution* : j'ai écrit un script de rejeu complet des 12 migrations sur une base vide, comparé structurellement chaque table, et créé une migration corrective dédiée pour le drift identifié. Cette démarche aurait évité un échec de déploiement basé sur un rejeu des migrations.

**Difficulté 3 — Absence de versionning Git**

Le projet était stocké sous OneDrive sans dépôt Git. Un conflit de synchronisation concurrente a entraîné la perte de travail frontend (retour à une version antérieure de plusieurs fichiers).

*Solution* : récupération manuelle des fichiers perdus, puis prise de conscience de la nécessité critique d'un système de versionnement. J'ai documenté l'incident comme axe d'amélioration prioritaire.

**Difficulté 4 — Salaire moyen : un indicateur non automatisable**

Le champ `salary_range` est saisi en texte libre (ex. `"35k-45k EUR"`), ce qui rend impossible le calcul automatisé du salaire moyen par filière — indicateur pourtant demandé par les organismes de tutelle.

*Solution* : j'ai documenté le problème et recommandé de remplacer la saisie par une tranche sélectionnable ou d'ajouter un champ numérique dédié. Le problème est signalé dans le guide des processus comme prioritaire pour la phase de mise en production.

### 3.3 Proposition d'axes d'amélioration

**Axe 1 — Implémentation de la newsletter et des relances**

Le mécanisme de relance des alumni est le principal manque identifié. La clé Resend est configurée mais utilisée uniquement pour l'envoi de codes OTP. L'endpoint `POST /newsletter/envoyer` avec filtre de ciblage (promotion, secteur, consentement) est conçu et documenté, mais son implémentation frontend et backend reste à faire. Sans relance, la base de données risque de devenir obsolète dès la première génération de données.

**Axe 2 — Structuration du champ salaire**

Remplacer la saisie texte `salary_range` par une tranche numérique sélectionnable (ou ajouter un champ `salaire_annuel` numérique en plus du champ texte) pour permettre le calcul du salaire moyen par filière — indicateur obligatoire pour les rapports ministeriels.

**Axe 3 — Mise en place d'un dépôt Git**

Créer un dépôt Git (GitHub, GitLab ou Gitea) avec branches `main`/`develop`, politique de commit et éventuellement CI/CD. C'est une nécessité absolue pour tout travail en équipe ou tout déploiement partagé. L'incident de synchronisation OneDrive démontre le risque concret de l'absence de versionnement.

**Axe 4 — Chiffrement et durée de conservation**

Ajouter un mécanisme de chiffrement des données sensibles (salaire, données de consentement) et afficher dans le frontend la durée de conservation des données, conformément aux principes RGPD de minimisation et de limitation de conservation.

**Axe 5 — Module de mentorat et application mobile**

Extensions fonctionnelles documentées dans le guide des processus mais non implémentées : mise en relation alumni/étudiants actuels (mentorat), et application mobile pour faciliter la mise à jour des profils depuis un smartphone.

### 3.4 Limites identifiées du projet

| # | Limite | Impact | Section du rapport |
|---|---|---|---|
| L1 | **Newsletter et relances non implémentées** — la clé Resend est configurée mais utilisée uniquement pour les OTP. L'endpoint `POST /newsletter/envoyer` reste à développer. | Sans relance, les alumni ne sont jamais sollicités pour mettre à jour leur profil. La base de données risque de devenir obsolète dès la première génération de données. | §2.4, §3.3 axe 1 |
| L2 | **Salaire en texte libre** — le champ `salary_range` accepte des saisies comme `"35k-45k EUR"` sans structure numérique. | Le calcul automatisé du salaire moyen par filière — indicateur obligatoire pour les rapports ministeriels — est impossible. | §2.2 (tableau indicateurs), §3.2 difficulté 4, §3.3 axe 2 |
| L3 | **Absence de dépôt Git** — le projet est stocké sous OneDrive sans versionnement. Un conflit de synchronisation a provoqué la perte de fichiers frontend. | Aucun historique de modification, impossible de revenir à une version antérieure, risque de perte de travail en cas de défaillance. | §2.5, §3.3 axe 3 |
| L4 | **RGPD : pas de DPO, pas de chiffrement, pas de notification de violation** — la conformité est partielle. Le consentement est traçable, mais la durée de conservation et les mécanismes de sécurité avancés ne sont pas en place. | Non-conformité potentielle si un audit réglementaire est réalisé. Le frontend n'affiche pas la durée de conservation. | §3.2 difficulté 1, §3.3 axe 4 |
| L5 | **Pas de mécanisme de relance automatique pour le questionnaire annuel** — l'activation est manuelle, aucune notification n'est envoyée aux alumni. | Taux de réponse potentiellement faible, données d'insertion incomplètes. | §3.3 axe 1 |
| L6 | **Fichier MCD/MLD frontend obsolète** — `mcd_corrige.md` listait 11 tables au lieu de 14 (DEMANDE_RGPD, OTP_CODES, SCHEMA_MIGRATIONS manquantes). | Risque de confusion si le fichier est utilisé comme référence par un nouveau développeur. | §2.6 |
| L7 | **Clé `ADMIN_API_KEY` exposée** — une capture d'écran a involontairement révélé la clé. | Accès non autorisé possible si la clé n'est pas changée avant déploiement. | §2.2 (note) |

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

[À COMPLÉTER : insérer le schéma MCD/MLD régénéré par introspection de la base de données]

### Annexe B — Dashboard administrateur (captures d'écran)

[À COMPLÉTER : insérer les captures d'écran du dashboard bento grid avec indicateurs]

### Annexe C — Espace alumni (captures d'écran)

[À COMPLÉTER : insérer les captures d'écran de l'inscription multi-étapes, du profil, du parcours, du questionnaire]

### Annexe D — Guide des processus d'animation du réseau (extrait)

[À COMPLÉTER : insérer un extrait ou la version complète du guide généré séparément]

### Annexe E — Liste des endpoints API

[À COMPLÉTER : liste complète des 50+ endpoints avec méthode HTTP, chemin et description]

### Annexe F — Différentiel de migration et audit de conformité

[À COMPLÉTER : tableau du drift de migration corrigé et résultats du rejeu des 12 migrations]
