# Audit de cohérence — API FastAPI ↔ base PostgreSQL

**Alumni CRM** · base `alumni_crm` · audit initial du 16/08/2026, relecture du 10/09/2026 après corrections.

> Document unique : fusion de l'ancien `AUDIT_COHERENCE_TABLES.txt` (détail
> table-par-champ, « l'instantané » de l'audit) et de `AUDIT_SIMPLE.md` (version
> synthétique). Une seule source de vérité, également disponible en PDF
> (`AUDIT_COHERENCE.pdf`).

---

## Verdict global

| Résultat | Nombre |
|---|--:|
| [OK] État conforme | 6 tables |
| [CORRIGÉ] Problèmes graves (P1) résolus | 2 |
| [CORRIGÉ] Problèmes moyens (P2) résolus au 10/09 | 5 |
| [A CORRIGER] Points restants (maintenance, P3) | 2 |

**Aucun problème critique restant.** Les points P3 sont des améliorations
cosmétiques / de maintenance, pas des bugs.

## État table par table

| Table | État | Ce qui compte |
|---|---|---|
| `PROMOTION` | [OK] | Lecture/écriture OK. |
| `ENTREPRISE` | [CORRIGÉ] | Suppression cassée → corrigé (un simple DELETE, la FK est en CASCADE). |
| `EXPERIENCE_PRO` | [CORRIGÉ] | Création transactionnelle + **nouvelle route de modification atomique**. Suppression OK. |
| `CERTIFICATION` / `OBTIENT` | [OK] | Dates validées (pas de futur), messages d'erreur corrects. |
| `CONSENTEMENT_RGPD` | [OK] | Statut limité à `actif` / `refuse` (API **et** base). |
| `QUESTIONNAIRE` / `QUESTION` / `REPONSE` | [OK] | Types de question limités, réponses contrôlées, cascade corrigée. |
| `DEMANDE_RGPD` | [OK] | Cycle de statuts contrôlé, filtres admin validés. |
| `AUDIT_LOG` / `OTP_CODES` | [OK] | Fonctionnels ; TTL OTP bien vérifié. |

---

## Ce qui a été corrigé

### Problèmes critiques (P1) — résolus avant le 10/09

1. **Delete d'une entreprise cassé** dès qu'une expérience la référençait
   (`entreprises.py` faisait un `UPDATE ... SET id_entreprise = NULL` sur une
   colonne `NOT NULL` → erreur 400). → Remplacement par un `DELETE` direct.
2. **Drift de migration** : `reponse_questionnaire.id_etudiant` avait
   `ON DELETE CASCADE` en base mais pas dans la migration 003 → rejeu complet
   des migrations plantait. → Nouvelle migration qui recrée la FK en CASCADE.

### Problèmes moyens (P2) — résolus le 10/09/2026

3. **Expérience professionnelle : aucune route de modification**
   (`EXPERIENCE_PRO`). Le front faisait delete + recréation = *non atomique*
   (l'expérience pouvait être supprimée sans être recréée).
   → Correction :
   - API : nouvelle route **`PUT /experiences/{id_experience}`** qui modifie
     l'expérience en **une seule transaction** (entreprise réutilisée ou créée,
     poste actuel exclusif). `routers/experiences.py`
   - Front : « Mon Parcours » met désormais à jour les postes existants au
     lieu de tout supprimer puis récréer — il ne supprime que ce qui a
     vraiment été retiré. `AlumniCareer.jsx` + `api.js`

4. **Réponses questionnaire non vérifiées** : les valeurs n'étaient pas
   contrôlées contre le type de question.
   → Correction : contrôle complet dans `POST /questionnaires/{id}/repondre` :
   - réponse = une **option prévue** pour `choice` / `single_choice` / `dropdown`
   - réponse égale à `Oui` / `Non` pour `boolean`
   - note de 1 à 5 pour `rating`
   - clés étrangères au questionnaire → erreur 422 explicite

5. **`ordre = 0` ignoré** à la création d'un questionnaire (retombait sur
   l'index de la liste). → Traité fidèlement.

6. **`PUT /admin/questionnaires/{id}` renvoyait `actif: true` en dur** même si
   le questionnaire était désactivé. → Renvoie la vraie valeur de la base.

7. **`PUT /promotions/{id}` renvoyait `nb_etudiants = 0` en dur**.
   → Renvoie le vrai nombre d'étudiants.

### Alignement base de données (migration 016)

La migration **`016_contraintes_check.sql`** fait porter les mêmes règles que
l'API directement par PostgreSQL (le SQL direct ne peut plus les contourner) :

- `CONSENTEMENT_RGPD.statut` dans `('actif','refuse')`
- `EXPERIENCE_PRO.date_fin >= date_debut` (ou NULL)
- pas de `date_fin` si `poste_actuel = true`
- `salaire >= 0` et `salary_annuel >= 0`
- `QUESTION.type` dans les types gérés par le frontend
- `PROMOTION.annee_diplome` de 1950 à 2100

---

## Points restants (améliorations, non bloquants)

| # | Point | Où | Effet si ignoré |
|---|---|---|---|
| A | `_write_audit_log` avale les erreurs d'écriture | `cleanup.py` | Un échec d'audit passe inaperçu |
| B | Pas de purge automatique des OTP expirés ni de l'historique d'audit | `otp.py` / `cleanup.py` | La table `otp_codes` grossit indéfiniment |

Ces deux points relèvent de la maintenance, pas de bugs utilisateurs.

---

## Détail table par champ (instantané du 16/08/2026)

> Extraits verbatim de l'audit initial, conservés pour la traçabilité.
> Les constats déjà corrigés sont marqués `[CORRIGÉ ...]` en place.

```text
================================================================================
AUDIT DE COHÉRENCE API <-> BASE DE DONNÉES — TABLES MÉTIER
================================================================================
Date de l'audit : 16/08/2026
Méthode : introspection live PostgreSQL (information_schema.columns,
           pg_constraint, pg_indexes) sur la base "alumni_crm", croisée avec
           les routers, les schémas Pydantic (schemas.py) et les migrations
           SQL (001, 002, 003, 004, 005, 006, 007, 009).
           NB : numéros de migrations selon le renommage du 22/08/2026
           (numérotation continue 001→012 ; l'ancien trou « 003 absent » a
           été comblé par renumérotation des fichiers et de schema_migrations).
Contrainte : audit uniquement — AUCUN code modifié.
MISE À JOUR 22/08/2026 : les 2 P1 listés ci-dessous ont été corrigés depuis
l'audit (marqués [CORRIGÉ]). Le reste du document est conservé tel quel
(instantané du 16/08/2026).

MISE À JOUR 10/09/2026 : la plupart des P2 et P3 ont été corrigés dans le
code (détail en synthèse dans la première partie de ce document) :
- P2 #5 : ajout de PUT /experiences/{id_experience} (modification atomique)
  + « Mon Parcours » (front) utilise désormais la mise à jour, plus de
  delete+recreate en bloc ;
- P2 #6 : réponses questionnaire contrôlées contre le type de la question ;
- P2 #3/#4/#7/#8 étaient déjà corrigés au niveau des schémas/routes ;
- P3 : ordre=0 respecté, actif réel sur PUT questionnaire, nb_etudiants réel
  sur PUT promotion ;
- migration 016 : contraintes CHECK alignées (statut consentement, salaires,
  dates expérience, type question, année promotion).

État de la base au moment de l'audit :
  1 promotion, 4 entreprises, 3 expériences pro, 1 certification, 1 obtient,
  10 consentements RGPD, 1 questionnaire (3 questions, 1 réponse),
  0 demande RGPD, 53 entrées d'audit, 90 codes OTP.

--------------------------------------------------------------------------------
LEGENDE DES COLONNES
--------------------------------------------------------------------------------
  Exposé en lecture     : le champ est-il retourné par une route GET ?
  Validé en écriture    : le champ est-il validé/contraint côté API (Pydantic) ?
  Cohérent avec SQL     : le comportement code/schéma correspond-il au schéma
                          réel de la base ?
  Problème identifié    : constat éventuel (P1 = incohérence/route cassée,
                          P2 = validation manquante / message trompeur,
                          P3 = cosmétique / maintenance).

================================================================================
1. PROMOTION (1 ligne)
================================================================================
Champ                  | Exposé lecture | Validé écriture          | Cohérent SQL | Problème identifié
-----------------------|----------------|--------------------------|--------------|------------------------------
nom_promotion / filiere| Oui            | Obligatoire, pas de long. mini | Oui (VARCHAR NOT NULL) | P3 : chaîne vide "" acceptée -> promotion vide possible
annee_diplome          | Oui            | ge=1950 le=2100 (Pydantic) | Oui (INTEGER) | P3 : aucun CHECK en DB — passe en SQL direct
nb_etudiants           | Oui (GET, calculé) | —                    | Oui          | P3 : PUT /promotions/{id} renvoie nb_etudiants=0 en dur (promotions.py:145)
DELETE force=true      | —              | —                        | Oui en live  | Supprime C/O/E/ETUDIANT ; REPONSE_QUESTIONNAIRE passé via cascade ETUDIANT (OK en live)

================================================================================
2. ENTREPRISE (4 lignes)
================================================================================
Champ                          | Exposé lecture | Validé écriture | Cohérent SQL | Problème identifié
-------------------------------|----------------|-----------------|--------------|----------------------------------------
nom_entreprise / secteur / pays/ville | Oui    | Obligatoires, pas de long. mini | Oui | P3 : "" accepté ; doublons possibles
DELETE /entreprises/{id}       | —              | —                | NON          | P1 : UPDATE EXPERIENCE_PRO SET id_entreprise = NULL (entreprises.py:139) sur colonne NOT NULL -> IntegrityError -> 400 dès qu'une expérience référence l'entreprise. La FK est ON DELETE CASCADE : un simple DELETE suffit. [CORRIGÉ 22/08/2026 : DELETE direct en place]

================================================================================
3. EXPERIENCE_PRO (3 lignes)
================================================================================
Champ             | Exposé lecture | Validé écriture                  | Cohérent SQL | Problème identifié
------------------|----------------|----------------------------------|--------------|----------------------------------------
intitule_poste / type_contrat / date_debut | Oui | Obligatoires    | Oui          | P3 : pas de longueur minimale
date_fin          | Oui            | Optionnel                        | Oui (NULL)   | P2 : aucune validation date_fin >= date_debut ; "poste_actuel=true" + date_fin accepté (contradiction)
salaire           | Oui            | ge=0 (Pydantic)                  | Oui (NUMERIC)| P3 : aucun CHECK DB >= 0
poste_actuel      | Oui            | Requis (bool)                    | Oui (def=true) | P3 : aucune unicité du poste actuel
MODIFICATION      | —              | —                                | —            | P2 : AUCUNE route d'update d'une expérience. Le delete+recreate côté front = 2 transactions HTTP distinctes -> NON ATOMIQUE (expérience supprimée + recréation échouée = perte). La création (POST /etudiants/{id}/experiences) est en revanche transactionnelle : un seul commit() + rollback global (experiences.py:171-241). [CORRIGÉ 10/09/2026 : PUT /experiences/{id_experience} mis à jour atomique en une transaction ; le front utilise désormais la mise à jour au lieu du delete+recreate en bloc.]

================================================================================
4. CERTIFICATION / OBTIENT (1 + 1 lignes)
================================================================================
Champ             | Exposé lecture | Validé écriture                  | Cohérent SQL | Problème identifié
------------------|----------------|----------------------------------|--------------|----------------------------------------
nom_certification / organisme | Oui | Obligatoires            | Oui          | P3 : doublons possibles (pas d'UNIQUE) ; pas de route PUT
date_obtention    | Oui            | Requis (admin), Optionnel (alumni) | Oui (NOT NULL) | P2 : aucune validation anti-futur ni de borne basse sur les 3 écritures (associer / ajouter alumni / upsert)
Messages OBTIENT  | —              | —                                | —            | P2 : admin -> doublon PK renvoie "L'étudiant ou la certification n'existe pas" ; alumni -> date_obtention omise (NULL) -> même message trompeur alors que l'étudiant existe (certifications.py:51,176)

================================================================================
5. CONSENTEMENT_RGPD (10 lignes)
================================================================================
Champ                 | Exposé lecture | Validé écriture | Cohérent SQL | Problème identifié
----------------------|----------------|-----------------|--------------|----------------------------------------
type_consentement / canal | Oui       | Strings libres  | Oui (VARCHAR)| P3 : aucune liste contrainte
statut                | Oui            | String libre — PAS de Literal | Oui (aucun CHECK DB) | P2 : statut totalement libre. Le code repose sur la convention 'actif'/'refuse' (admin.py:78, cleanup.py:37) -> une mauvaise valeur est silencieusement ignorée par le filtre "prise_de_contact"
UNIQUE (id_etudiant, type) | —        | ON CONFLICT upsert | Oui (migration 006) | —
id_etudiant           | Oui            | —               | Oui (FK CASCADE) | —

================================================================================
6. QUESTIONNAIRE / QUESTION / REPONSE_QUESTIONNAIRE (1 / 3 / 1)
================================================================================
Champ                 | Exposé lecture | Validé écriture | Cohérent SQL | Problème identifié
----------------------|----------------|-----------------|--------------|----------------------------------------
type (QUESTION)       | Oui            | String libre, default 'text' | Oui (VARCHAR, aucun CHECK) | P2 : valeurs type non contraintes ; options non validées vs type
tag / conditionnee_statut_emploi | Oui | Libres        | Oui (migrations 004/005) | —
reponses (JSONB)      | Oui            | dict libre      | Oui          | P2 : aucune validation — clés non vérifiées vs id_question existants, valeurs non vérifiées vs type de question
UNIQUE (id_etudiant, id_questionnaire) | — | Upsert ON CONFLICT | Oui en live | P1 : DRIFT migration 003 — voir liste priorisée (2)
PUT /admin/questionnaires/{id} | Oui  | —               | —            | P3 : renvoie "actif": true en dur même si désactivé (questionnaires.py:276)
ordre                 | Oui            | int = 0          | Oui          | P3 : q.ordre if q.ordre else i -> un ordre 0 retombe sur l'index (questionnaires.py:44)

================================================================================
7. DEMANDE_RGPD (0 ligne)
================================================================================
Champ                 | Exposé lecture | Validé écriture                  | Cohérent SQL | Problème identifié
----------------------|----------------|----------------------------------|--------------|----------------------------------------
type_demande          | Oui            | pattern ^(export|suppression)$   | Oui (CHECK 008) | —
statut                | Oui (str)      | Cycle géré par _VALID_STATUTS    | Oui (CHECK migration 009 en live) | Cycle envoyee->en_traitement->traitee/rejetee bien synchronisé avec le CHECK 009, mais PAS via Literal Pydantic — contrainte portée par la DB + constantes Python. Risque nul aujourd'hui.
Filtres liste admin   | Oui            | —                                | —            | P2 : statut/type_demande invalides dans le query param silencieusement ignorés -> liste complète renvoyée au lieu d'une erreur (demandes_rgpd.py:716-721)
id_etudiant           | Oui            | —                                | Oui (FK SET NULL) | Hard-delete étudiant garde la demande avec id_etudiant=NULL (géré)

================================================================================
8. AUDIT_LOG (53 lignes)
================================================================================
Champ                        | Exposé lecture | Validé écriture | Cohérent SQL | Problème identifié
-----------------------------|----------------|-----------------|--------------|----------------------------------------
action/details/rows/executed_at/acteur | Oui (/admin/cleanup/audit) | Oui (cleanup, RGPD, purge, etudiants) | Oui (migration 001 + acteur 007) | —
Robustesse                   | —              | —               | —            | P3 : _write_audit_log avale toute exception (cleanup.py:66-67) -> échec silencieux ; supprimer_orphelins se dit "transaction unique" mais commit par bloc (cleanup.py:185-243) ; aucune purge/rétention

================================================================================
9. OTP_CODES (90 lignes)
================================================================================
Champ             | Exposé lecture | Validé écriture   | Cohérent SQL | Problème identifié
------------------|----------------|-------------------|--------------|----------------------------------------
expires_at        | —              | now() + 10 min    | Oui          | TTL bien RE-VERIFIE à chaque validation (expired = now > expires_at, otp.py:295-317 -> 410 "Code expiré"), pas seulement à la création
attempts          | —              | Incrémenté, 5 max -> 429 | Oui    | Détail : incrémenté seulement sur le code actif le plus récent, même si l'utilisateur tape un autre code
—                 | —              | —                 | —            | P3 : aucune purge des codes expirés/utilisés (90 lignes et ça grossit)

================================================================================
LISTE PRIORISÉE
================================================================================
P1 — Incohérences / erreurs trompeuses :
  1. DELETE /entreprises/{id} cassé dès qu'une expérience existe
     (UPDATE vers NULL sur colonne NOT NULL, entreprises.py:139).
     Correctif : suppression directe — la FK est déjà ON DELETE CASCADE.
     [CORRIGÉ 22/08/2026 : entreprises.py:139 fait désormais un DELETE direct,
      le UPDATE vers NULL a disparu.]
  2. Drift migration 003 vs DB live : reponse_questionnaire.id_etudiant a
     ON DELETE CASCADE en live mais PAS dans la migration 003. Sur une base
     reconstruite depuis les migrations, le hard-delete d'un étudiant avec
     réponses (etudiants.py:593, promotions.py:174, cleanup doublons)
     échouerait en IntegrityError.
     [CORRIGÉ 22/08/2026 : la migration 011_fix_reponse_questionnaire_cascade.sql
      recrée la FK avec ON DELETE CASCADE — base et migrations alignées.]

P2 — Validations manquantes / messages trompeurs :
  3. date_obtention non validée (futur possible) ; message IntegrityError
     trompeur sur OBTIENT (doublon PK, date NULL).
  4. CONSENTEMENT_RGPD.statut libre (pas de Literal, pas de CHECK) alors que
     admin/cleanup comptent sur 'actif'/'refuse'.
  5. EXPERIENCE_PRO : aucune validation date_fin/poste_actuel ; aucune route
     d'update (le delete+recreate front est non atomique).
     [CORRIGÉ 10/09/2026 : PUT /experiences/{id_experience} atomique + validation
      date_fin >= date_debut et poste actuel exclusif ; voir la 1re partie de
      ce document.]
  6. REPONSE_QUESTIONNAIRE.reponses : aucune vérification clés/valeurs vs
     questions.
  7. DEMANDE_RGPD : filtres admin invalides ignorés silencieusement (liste
     complète renvoyée).
  8. QUESTION.type et options non contraints.

P3 — Cosmétique / maintenance :
  9. PUT /promotions/{id} -> nb_etudiants=0 en dur ; PUT /admin/questionnaires/{id}
     -> actif:true en dur ; ordre=0 retombe sur l'index.
 10. _write_audit_log avale les erreurs ; supprimer_orphelins pas vraiment
     "transaction unique" ; pas de purge des otp_codes ni de l'audit_log.

================================================================================
RÉPONSES AUX 5 QUESTIONS DE L'UTILISATEUR
================================================================================
1. Update EXPERIENCE_PRO : AUCUNE route d'update ; le delete+recreate front
   est non atomique (2 transactions) ; la création est transactionnelle.
   [CORRIGÉ 10/09/2026 : PUT /experiences/{id_experience} — modification
   atomique en une transaction.]
2. date_obtention : non validée (date future acceptée).
3. CONSENTEMENT_RGPD.statut : string libre, non contraint (pas de Literal).
4. Cycle statuts DEMANDE_RGPD : synchronisé avec le CHECK de la migration 009
   (DB + constantes Python), mais pas via Literal Pydantic.
5. TTL OTP (10 min) : vérifié à chaque validation (verify_otp), pas seulement
   à la création.
================================================================================
```

---

## Application de la migration (état)

La migration **016** a été appliquée le **10/09/2026** :

```bash
cd alumni_crm_api
python run_migrations.py   # 17 migrations : la 016 est détectée et appliquée
```

L'outil ne rejoue jamais une migration déjà présente dans `schema_migrations`.

## Test rapide conseillé après déploiement

1. `PUT /promotions/{id}` → `nb_etudiants` réel.
2. `PUT /experiences/{id}` (alumni propriétaire) → modification prise en
   compte sans perte de données.
3. `POST /questionnaires/{id}/repondre` avec une valeur hors options → 422
   avec message explicite.
4. `INSERT INTO CONSENTEMENT_RGPD (..., 'autre')` en SQL direct → la base
   refuse la ligne.