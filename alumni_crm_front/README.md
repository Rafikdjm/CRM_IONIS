# Alumni CRM — Frontend

Interface React + Vite de l'Alumni CRM (IONIS-STM) : espace administrateur
(dashboard KPI, annuaire filtrable, promotions, questionnaires, demandes RGPD,
import/export Excel) et espace alumni (inscription multi-étapes avec OTP,
profil, parcours professionnel, consentements RGPD, questionnaire annuel).

## Prérequis

- Node.js 18+
- Le backend FastAPI lancé en local (voir `alumni_crm_api/README.md`)

## Installation et démarrage

```bash
npm install
npm run dev
```

L'application tourne sur le port **3000** (`http://localhost:3000`).

## Proxy API en développement

En dev, Vite proxifie les appels vers `/api` vers le backend :

| Réglage | Valeur (vite.config.js) |
|---|---|
| Cible | `VITE_API_URL` (défaut `http://localhost:8000`) |
| Rewrite | le préfixe `/api` est retiré (`/api/admin/indicateurs` → `/admin/indicateurs`) |

Aucune configuration CORS n'est donc nécessaire en développement.

## Variables d'environnement

Copier `.env.example` vers `.env` puis ajuster :

| Variable | Rôle | Défaut |
|---|---|---|
| `VITE_API_URL` | URL de base de l'API backend (cible du proxy Vite, et base des appels axios hors dev). Laisser absente en dev : le proxy vise `http://localhost:8000`. | `http://localhost:8000` |
| `VITE_SHOW_DEV_PREVIEW` | Affiche l'aperçu du code OTP à l'écran (bloc « Code de connexion / Aperçu de l'e-mail reçu »). Mettre à `false` pour masquer ce bloc (démonstration/production). | affiché sauf si `false` |

## Scripts

| Script | Commande | Description |
|---|---|---|
| `dev` | `vite` | Serveur de développement (HMR, proxy API) |
| `build` | `vite build` | Build de production dans `dist/` |
| `preview` | `vite preview` | Sert le build de production localement |
| `test` | `vitest run` | Suite de tests (14 fichiers, 118 tests) |
| `test:watch` | `vitest` | Tests en mode watch |
| `lint` | `oxlint` | Lint du code |

## Structure

```
src/
  components/
    admin/     Dashboard, annuaire, promotions, questionnaires, RGPD, import Excel
    alumni/    Inscription multi-étapes, profil, parcours, consentement, survey
    shared/    ThemeToggle (clair/sombre), KPICard, LoadingSpinner, ProtectedRoute
  contexts/    Thème clair/sombre
  services/    api.js — client axios (baseURL '/api')
  utils/       Helpers (emails académiques, téléchargement blob)
  __tests__/   Suite Vitest + Testing Library (jsdom)
```

## Authentification

- **Alumni** : connexion par code OTP à 6 chiffres envoyé par email (session JWT).
- **Admin** : connexion par code d'accès (session JWT distincte, clé `admin_role`
  séparée de `alumni_id` côté navigateur pour éviter toute confusion de session).
