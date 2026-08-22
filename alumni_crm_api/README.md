# CRM Alumni API — version corrigée

## Installation

```bash
pip install -r requirements.txt
cp .env.example .env
# éditer .env avec les vrais identifiants et une vraie clé admin
uvicorn main:app --reload
```

## Structure

```
config.py            # variables d'environnement (identifiants, clé admin)
database.py           # pool de connexions pg8000
security.py           # dépendances d'authentification (clé API, JWT admin/alumni)
schemas.py             # modèles Pydantic (validation incluse)
utils.py               # helper de sérialisation cursor -> dict
main.py                 # assemble les routers + CORS
run_migrations.py      # exécute les migrations SQL numérotées avec tracking (schema_migrations)
purge.py               # CLI : purge définitive différée des comptes anonymisés RGPD (--dry-run)
migrations/            # migrations SQL numérotées 001 → 012
routers/
  promotions.py         # /promotions          : CRUD des promotions
  etudiants.py          # /etudiants           : CRUD étudiants + profil alumni
  entreprises.py        # /entreprises         : CRUD des entreprises
  experiences.py        # /etudiants/{id}/experiences, /experiences : parcours professionnel (postes, salaires)
  certifications.py     # /certifications      : certifications + obtentions par étudiant
  rgpd.py               # /consentements       : choix RGPD (prise_de_contact, newsletter, etc.)
  otp.py                # /auth/otp            : connexion alumni par code à 6 chiffres (rate-limiting)
  admin_auth.py         # /auth/admin/login    : connexion admin par code d'accès (hash SHA-256)
   demandes_rgpd.py      # /rgpd/demandes + /admin/demandes-rgpd : demandes export/suppression, anonymisation
   questionnaires.py     # /questionnaires + /admin/questionnaires : questionnaires annuels d'insertion
   newsletter.py         # /newsletter/envoyer    : envoi de newsletter aux alumni consentants (X-API-Key)
   admin.py              # /admin               : annuaire filtré, indicateurs dashboard (X-API-Key)
   cleanup.py            # /admin/cleanup       : orphelins, doublons, archivage RGPD, audit log
   automatisation.py     # /upload-etudiants/   : import CSV/Excel
   import_export.py      # /import              : template Excel, import, export alumni
```

## Corrections apportées, classées selon les 4 axes de la revue

**1. Robustesse et sécurité**
- Identifiants PostgreSQL déplacés dans des variables d'environnement (`config.py`, `.env.example`) au lieu d'être en dur dans le code.
- Routes `/admin/*` protégées par une clé API (header `X-API-Key`), car elles exposent des données personnelles et salariales (enjeu RGPD).
- Les messages d'erreur renvoyés au client ne contiennent plus le détail brut des exceptions (`str(e)`) ; le détail est loggé côté serveur, un message générique est renvoyé au client.
- Suppression des vérifications d'existence en deux temps (`SELECT` puis `INSERT`/`UPDATE`), remplacées par la gestion de `pg8000.dbapi.IntegrityError` ou par `cursor.rowcount` : élimine le risque de race condition (TOCTOU) et réduit le nombre d'allers-retours DB.
- `ajouter_experience` et `calculer_indicateurs` renvoyaient un `200 OK` avec `{"erreur": ...}` en cas de problème : ils lèvent maintenant une `HTTPException` correcte.
- Upload de fichier : vérification de l'extension, limite de taille (5 Mo par défaut), et validation de chaque ligne via `schemas.EtudiantCreate` avant insertion (au lieu d'insérer les valeurs brutes du fichier).

**2. Performance**
- `database.py` maintient un pool de connexions au lieu d'ouvrir/fermer une connexion PostgreSQL à chaque requête HTTP.
- Pagination (`skip`/`limit`) ajoutée sur tous les endpoints de listing (promotions, étudiants, entreprises, filtrage admin).
- Import de fichier : les entreprises existantes sont préchargées en une seule requête (`SELECT ... FROM ENTREPRISE`) au lieu d'un `SELECT` par ligne du fichier.

**3. Bonnes pratiques**
- `.dict()` (déprécié en Pydantic v2) remplacé par `.model_dump()`.
- Le résultat des requêtes est transformé en dict via `utils.rows_to_dicts()` (basé sur `cursor.description`) plutôt qu'en indexant les tuples à la main (`r[0]`, `r[1]`...), plus fragile.
- `NouvelleExperience` déplacé de `main.py` vers `schemas.py`, avec tous les autres modèles.
- Ajout de contraintes de validation manquantes (`salaire >= 0`, `annee_diplome` dans une plage raisonnable).

**4. Maintenabilité**
- Le fichier unique de ~590 lignes a été découpé en un router `APIRouter` par domaine métier (Promotions, Étudiants, Entreprises, Expériences, Certifications, RGPD, Admin, Automatisation), `main.py` ne fait plus qu'assembler les routers.

## Tests

**Backend** : pas de framework de tests (pytest) pour l'instant — la validation
est faite par des scripts de contrôle ad hoc qui exercent les routes réelles
via l'API HTTP (voir « Test fonctionnel de bout en bout » ci-dessous).

**Frontend** : la suite Vitest se lance avec `npm test` dans `alumni_crm_front`
(14 fichiers de tests, 117 tests — auth OTP, consentements RGPD, import
Excel, indicateurs complémentaires, routes protégées).

### Test fonctionnel de bout en bout (E2E)

Le parcours complet de l'application est vérifié par un script Python qui
appelle le backend réel (`http://127.0.0.1:8000`) — pas de mocks. Il couvre
les deux profils :

**Parcours alumni** (connexion OTP réelle, code lu en base puis présenté à
`/auth/otp/verify`) :
1. `POST /auth/otp/request` puis `POST /auth/otp/verify` → token alumni
2. `GET /etudiants/{id}` → consultation du profil
3. `GET|POST /etudiants/{id}/experiences` → consultation / alimentation du Mon Parcours
4. `POST /consentements/` → sauvegarde d'un choix RGPD (`prise_de_contact`, `actif`)
5. `POST /rgpd/demandes` (`export`) puis `GET /rgpd/demandes/moi` → demande d'export
6. `POST /rgpd/demandes` (`suppression`) → demande de suppression

**Parcours admin** :
7. `POST /auth/admin/login` (code d'accès du `.env`) → token admin
8. `GET /admin/etudiants/filtrer?contact_autorise=actif` → annuaire filtré (tous actifs)
9. `GET /admin/indicateurs` → dashboard
10. `GET /admin/questionnaires/` et `GET /questionnaires/actif` → questionnaires
11. `GET /admin/demandes-rgpd?statut=envoyee` puis
    `POST /admin/demandes-rgpd/{id}/prendre-en-charge` (`{"traitee_par":...}`)
    puis `POST /admin/demandes-rgpd/{id}/traiter` (`{"decision":"traitee","traitee_par":...}`)

**Points de contrôle RGPD** (vérifiés directement en base après traitement) :
le compte est anonymisé (`nom`/`prenom` = `ANONYMISE`, email
`ANONYMISE_<id>@anonymise.io`), la demande passe à `traitee` avec
`traitee_par` renseigné, et l'opération est tracée dans `AUDIT_LOG`.

Le script utilise un étudiant jetable (email unique, promotion existante) et
le supprime à la fin (demandes RGPD + compte) pour ne pas polluer les données
de démonstration.

> **Note :** le script E2E lui-même n'est plus présent dans le dépôt ;
> le reconstituer à partir du déroulé ci-dessus fait partie des suites à
> donner au projet.

**Prérequis** : backend lancé (`uvicorn main:app`), `.env` renseigné
(`ADMIN_API_KEY`, `ADMIN_ACCESS_CODE`, accès PostgreSQL), `requests` et
`pg8000` installés (venv du backend).

## Limites connues, à garder en tête pour le rapport de stage

- L'authentification admin (`X-API-Key`) est volontairement simple : si l'application doit distinguer plusieurs profils utilisateurs (école vs alumni), il faudra passer à OAuth2/JWT.
- Le pool de connexions est artisanal (file d'attente simple) ; en production, un pool plus complet (SQLAlchemy, ou un vrai service de pooling comme PgBouncer) gérerait aussi la détection des connexions mortes.
- L'import de fichier reste ligne par ligne pour l'insertion des étudiants (nécessaire pour récupérer chaque `id_etudiant` généré) ; un vrai import de masse (COPY) serait à envisager si les fichiers dépassent plusieurs milliers de lignes.
