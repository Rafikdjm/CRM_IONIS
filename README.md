# Alumni CRM — IONIS-STM

**Conception et développement d'un système de suivi du parcours étudiant et de valorisation du réseau des anciens diplômés.**

Projet réalisé dans le cadre du stage Pré-MSc 2026 (IONIS-STM) — Rafik Djemadi.

---

## Présentation

Alumni CRM est une application web 3-tiers qui permet à un établissement d'enseignement supérieur de gérer le cycle de vie complet de ses étudiants : inscription administrative, parcours professionnel post-diplôme et animation du réseau alumni — avec la conformité RGPD intégrée dès la conception.

| Couche | Technologie |
|---|---|
| Backend | Python / FastAPI (16 routeurs montés dans 14 fichiers, 80 endpoints REST documentés via Swagger) |
| Frontend | React + Vite (espace admin + espace alumni) |
| Base de données | PostgreSQL (14 tables, 13 migrations versionnées) |
| Emails | Resend (OTP + newsletter), mode console en développement |

## Fonctionnalités

- **Espace alumni** : inscription multi-étapes avec vérification OTP par code à 6 chiffres, édition de profil, parcours professionnel (expériences + certifications), consentements RGPD, questionnaire annuel.
- **Espace administrateur** : tableau de bord avec KPI et graphiques, annuaire filtrable (promotion, secteur, entreprise, statut de contact), gestion des promotions, questionnaires d'insertion avec tags KPI (`adequation_formation`...), traitement des demandes RGPD.
- **Indicateurs d'insertion** : taux d'emploi à 6 mois (expériences actives à la date de référence), salaire moyen/min/max sur `salary_annuel`, adéquation formation/emploi via tags KPI extensibles sans modification du backend.
- **RGPD** : 4 types de consentement traçables, workflow de demandes export/suppression avec verrou anti-traitement parallèle, anonymisation vs suppression définitive, journal d'audit, purge différée configurable (`purge.py --dry-run`).
- **Import/Export** : template Excel, import d'alumni, export complet, upload CSV/Excel en masse protégé par clé API.

## Structure du dépôt

```
alumni_crm_api/     Backend FastAPI (+ README détaillé : routes, sécurité, corrections)
alumni_crm_front/   Frontend React/Vite (tests Vitest dans src/__tests__)
Rapport/            Livrables PDF générés par generate_reports.py
                    (rapport de stage, cartographie des données, charte RGPD,
                     stratégie de mise à jour, indicateurs d'insertion,
                     guide d'animation du réseau)
MCD_MLD V2.loo      Modèle Looping (conception MCD/MLD initiale)
alumni_crm_api/
  docs/             erd_alumni_crm.mmd / .docx (MLD régénéré par introspection),
                    methodologie_indicateurs_dashboard.docx
  migrations/       Migrations SQL numérotées 001 → 013
```

## Démarrage rapide

### 1. Base de données

Créer une base PostgreSQL vide, puis appliquer les migrations :

```bash
cd alumni_crm_api
python run_migrations.py
```

Le script ne rejoue jamais une migration déjà appliquée (table de suivi `schema_migrations`).

### 2. Backend

```bash
cd alumni_crm_api
python -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\uvicorn main:app --reload
```

Variables d'environnement attendues (fichier `.env`) :

| Variable | Rôle |
|---|---|
| `DB_HOST` / `DB_PORT` / `DB_NAME` / `DB_USER` / `DB_PASSWORD` | Connexion PostgreSQL |
| `ADMIN_API_KEY` | Clé admin (header `X-API-Key` sur toutes les routes `/admin/*`, import, newsletter) |
| `ADMIN_ACCESS_CODE` | Code de connexion administrateur |
| `JWT_SECRET` | Signature des sessions JWT |
| `OTP_MODE` | `console` (dev) ou `resend` (prod) |
| `RESEND_API_KEY` / `EMAIL_FROM` | Envoi réel des emails |
| `PURGE_DELAY_MONTHS` | Délai de purge des comptes anonymisés (défaut 6) |

### 3. Frontend

```bash
cd alumni_crm_front
npm install
npm run dev      # http://localhost:5173
npm test         # suite Vitest
```

## Documentation complémentaire

- [`alumni_crm_api/README.md`](alumni_crm_api/README.md) — architecture backend, liste des routers, test E2E, limites connues.
- [`AUDIT_COHERENCE_TABLES.txt`](alumni_crm_api/AUDIT_COHERENCE_TABLES.txt) — audit base/API par introspection SQL.
- [`Rapport/`](Rapport/) — livrables PDF du sujet de stage.
