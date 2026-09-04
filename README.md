# Alumni CRM — IONIS-STM

**Conception et développement d'un système de suivi du parcours étudiant et de valorisation du réseau des anciens diplômés.**

Projet réalisé dans le cadre du stage Pré-MSc 2026 (IONIS-STM) — Rafik Djemadi.

---

## Présentation

Alumni CRM est une application web 3-tiers qui permet à un établissement d'enseignement supérieur de gérer le cycle de vie complet de ses étudiants : inscription administrative, parcours professionnel post-diplôme et animation du réseau alumni — avec la conformité RGPD intégrée dès la conception.

| Couche | Technologie |
|---|---|
| Backend | Python / FastAPI (16 routeurs montés dans 14 fichiers, 83 endpoints REST documentés via Swagger) |
| Frontend | React + Vite (espace admin + espace alumni) |
| Base de données | PostgreSQL (14 tables, 16 migrations versionnées) |
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
  docs/             erd_alumni_crm.mmd / .docx (MLD régénéré par introspection)
  migrations/       Migrations SQL numérotées 000 → 015
alumni_crm_front/   Frontend React/Vite (espace admin + espace alumni)
Rapport/            Rapport de stage (LaTeX) + livrables — voir ci-dessous
image/              Captures d'écran du rapport (26 fichiers PNG)
MCD_MLD V3.loo      Modèle Looping (conception MCD/MLD)
```

## Rapport de stage et livrables

- **`Rapport/rapport.tex`** — rapport de stage en **LaTeX** (source unique de
  vérité) ; à compiler sur Overleaf sous le nom `main.tex` avec le dossier
  `image/` (captures d'écran). Un miroir Markdown (`Rapport/rapport.md`) est
  maintenu à jour.
- **`Rapport/`** — autres livrables PDF/DOCX générés (cartographie des données,
  charte RGPD, stratégie de mise à jour, indicateurs d'insertion, guide
  d'animation du réseau) par `generate_reports.py` / `generate_methodologie.py`.
- **`Rapport/Soutenance - Alumni CRM - PreMSc 2026.pptx`** — support de soutenance
  (généré par `generate_soutenance.py`).

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
npm run dev      # http://localhost:3000
npm run lint     # oxlint
```

## Documentation complémentaire

- [`alumni_crm_api/README.md`](alumni_crm_api/README.md) — architecture backend, liste des routers, test E2E, limites connues.
- [`AUDIT_COHERENCE_TABLES.txt`](alumni_crm_api/AUDIT_COHERENCE_TABLES.txt) — audit base/API par introspection SQL.
- [`Rapport/`](Rapport/) — rapport de stage (LaTeX) et livrables PDF/DOCX du sujet de stage.
