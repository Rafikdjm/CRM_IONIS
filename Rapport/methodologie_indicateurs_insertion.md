# Méthodologie — Indicateurs d'Insertion du Dashboard Alumni CRM (IONIS STM)

> **Fiche de référence complète et fidèle au code source.**
> Liens vers le code : `alumni_crm_api/routers/admin.py` (backend) et
> `alumni_crm_front/src/components/admin/AdminDashboard.jsx` (frontend).
>
> Les exemples chiffrés ci-dessous sont **fictifs** mais calculés exactement comme
> le font les requêtes SQL du backend. Chaque exemple reprend la formule réelle
> appliquée à un petit jeu de données.

---

## 1. Principes généraux

1. **Comptes anonymisés exclus** : toute ligne `ETUDIANT.date_anonymisation IS NOT NULL`
   est exclue de **tous** les indicateurs (RGPD). Seuls les comptes non anonymisés
   sont comptabilisés.
2. **Source de vérité de l'emploi** : `EXPERIENCE_PRO` (table structurée des
   expériences), **pas** le champ déclaratif `ETUDIANT.availability_status`.
   Un alumni est « en emploi » aujourd'hui si il possède une expérience :
   ```
   (date_fin IS NULL OR date_fin >= CURRENT_DATE)
   AND (poste_actuel = TRUE OR date_debut <= CURRENT_DATE)
   ```
   Une date de fin **déjà passée exclut toujours** l'expérience, même si
   `poste_actuel = TRUE` (saisie obsolète). Les dates structurelles priment.
3. **Salaire** : `salary_annuel` (numérique) est prioritaire ; sinon repli sur le
   champ texte `salaire`. Les salaires **nuls** sont exclus.
4. **Thresholds affichage** : secteur avec « Non renseigné » regroupé ; types de
   contrat vides → « Non renseigné » ; ≥ 6 catégories de secteur → « Autres ».

---

## 2. Les 10 indicateurs, avec exemples chiffrés

### 2.1 Total Alumni actifs
| Champ | Valeur |
|---|---|
| **Formule** | `COUNT(*) FROM ETUDIANT WHERE date_anonymisation IS NULL` |
| **Tables / colonnes** | `ETUDIANT.date_anonymisation` |
| **Exclusions / limites** | Comptes anonymisés exclus. |

**Exemple chiffré** — la base contient 3 alumni : `Rafik` (actif), `Alice` (actif),
`Anonyme` (anonymisé le 10/01/2026).
```
COUNT(*) WHERE date_anonymisation IS NULL  →  2
```
Le dashboard affiche **Total Alumni = 2** (jamais 3).

---

### 2.2 Alumni actifs (≥ 1 expérience)
| Champ | Valeur |
|---|---|
| **Formule** | `COUNT(DISTINCT id_etudiant)` depuis `EXPERIENCE_PRO` JOIN `ETUDIANT` (non anonymisés) |
| **Tables / colonnes** | `EXPERIENCE_PRO.id_etudiant`, `ETUDIANT.date_anonymisation` |
| **Exclusions / limites** | `DISTINCT` (un alumni compté une seule fois, même avec 3 expériences). Aucune condition de date. |

**Exemple chiffré** — `Rafik` a 2 expériences, `Alice` en a 1, `Anonyme` en a 5 (mais est anonymisé).
```
DISTINCT id_etudiant (non anonymisés)  →  Rafik, Alice  →  2
```
Même si `Anonyme` a 5 expériences, il est exclu → **Alumni actifs = 2**.

---

### 2.3 Taux de complétion / couverture
| Champ | Valeur |
|---|---|
| **Formule** | `(alumni avec ≥ 1 expérience / total alumni) × 100` |
| **Tables / colonnes** | `EXPERIENCE_PRO.id_etudiant`, `ETUDIANT.date_anonymisation` |
| **Exclusions / limites** | Un profil sans expérience est considéré « incomplet ». |

**Exemple chiffré** — 2 alumni non anonymisés, dont 1 avec expérience.
```
(1 / 2) × 100  →  50 %
```
Le dashboard affiche **Taux de complétion = 50 %**. Ce taux est aussi renvoyé
par `GET /admin/indicateurs` sous le nom `taux_reponse`.

---

### 2.4 Taux d'emploi à 6 mois
| Champ | Valeur |
|---|---|
| **Formule** | `date_reference = annee_diplome || '-12-01'` (diplomation supposée en juin, +6 mois) — expérience active si `date_debut ≤ référence AND (date_fin IS NULL OR date_fin ≥ référence)` — taux = `SUM(emplois_6_mois)/SUM(total_diplomes) × 100` sur les **promotions matures** |
| **Tables / colonnes** | `PROMOTION.annee_diplome`, `ETUDIANT.id_promotion`, `EXPERIENCE_PRO.date_debut/date_fin` |
| **Exclusions / limites** | Promotions non matures (fenêtre 6 mois non écoulée) → exclues du global, statut `en_attente`, taux `null`. |

**Exemple chiffré** — Aujourd'hui : **30 mai 2026**.

| Promotion | Année | Date référence | Fenêtre écoulée ? | Total | Emplois à 6 mois |
|---|---|---|---|---|---|
| IONIS STM 2024 | 2024 | 2024-12-01 | ✅ mature | 10 | 7 |
| IONIS STM 2025 | 2025 | 2025-12-01 | ✅ mature | 12 | 9 |
| IONIS STM 2026 | 2026 | 2026-12-01 | ❌ en_attente | 15 | — |

```
Taux global = (7 + 9) / (10 + 12) × 100 = 16/22 ≈ 72,7 %
Promo 2026 : taux null, statut 'en_attente' (fenêtre pas fermée)
```
Le dashboard affiche **72,7 %** et la promo 2026 est grisée / marquée « en cours ».

---

### 2.5 Taux d'emploi global (brut)
| Champ | Valeur |
|---|---|
| **Formule** | `(étudiants en poste / total étudiants) × 100`, calculé par promotion puis agrégé |
| **Tables / colonnes** | `EXPERIENCE_PRO.poste_actuel`, `ETUDIANT.id_promotion` |
| **Exclusions / limites** | Un seul comptage par étudiant (`DISTINCT`). `availability_status` non utilisé. |

**Exemple chiffré** — Promotion IONIS STM 2024 : 10 alumni, 8 en poste aujourd'hui.
```
(8 / 10) × 100  →  80 %
```

---

### 2.6 Adéquation formation/emploi
| Champ | Valeur |
|---|---|
| **Formule** | `(réponses 'Oui' / réponses exploitables) × 100` — question retenue : `tag = 'adequation_formation'` + **questionnaire actif le plus récent** |
| **Tables / colonnes** | `QUESTION.tag`, `QUESTIONNAIRE.actif`, `REPONSE_QUESTIONNAIRE.reponses` (JSON) |
| **Exclusions / limites** | Réponses « non applicable » / « n/a » exclues du dénominateur. Si aucune question taguée → état « Aucune donnée ». |

**Exemple chiffré** — 5 alumni ont répondu à la question taguée `adequation_formation`
(dont 1 « Non applicable ») : `Oui, Oui, Oui, Non`.
```
Réponses exploitables = 4 (les 5 moins la "Non applicable")
(Valeur selon type de question) → 3 Oui / 4 exploitables × 100 = 75 %
```
Le dashboard affiche **75 %**. *(Pour une question de type `rating`, le KPI
affiche une note moyenne `/5` plutôt qu'un pourcentage ; pour un `choice`, la
distribution par choix et le % du choix majoritaire.)*

---

### 2.7 Répartition par secteur
| Champ | Valeur |
|---|---|
| **Formule** | Pour chaque secteur : `COUNT(DISTINCT id_etudiant)` ayant `poste_actuel = TRUE` ; pourcentage = `count / total alumni actifs × 100` |
| **Tables / colonnes** | `ENTREPRISE.secteur_activite`, `EXPERIENCE_PRO.poste_actuel` |
| **Exclusions / limites** | Secteur vide exclu ; un alumni avec plusieurs postes peut apparaître dans plusieurs secteurs. |

**Exemple chiffré** — 6 alumni actifs : 3 Info, 2 Finance, 1 Santé, 1 (vide).
```
Informatique 3 → 50 %   Finance 2 → 33 %   Santé 1 → 17 %
```
Le donut montre **Info 50 %, Finance 33 %, Santé 17 %**. Avec plus de 5 catégories,
les plus petites sont regroupées sous « Autres ».

---

### 2.8 Alumni par promotion
| Champ | Valeur |
|---|---|
| **Formule** | Par promotion : effectif, % en poste, taux de couverture, salaire moyen. Les promotions sans alumni (non anonymisé) sont **exclues** (`HAVING COUNT > 0`). |
| **Tables / colonnes** | `PROMOTION`, `ETUDIANT.id_promotion`, `EXPERIENCE_PRO.poste_actuel/salaire` |
| **Exclusions / limites** | Salaire moyen calculé sur postes actuels uniquement. |

**Exemple chiffré** —
| Promotion | Effectif | En poste | Taux |
|---|---|---|---|
| IONIS STM 2024 | 10 | 8 | 80 % |
| IONIS STM 2025 | 12 | 9 | 75 % |
| IONIS STM 2026 | 15 | 11 | 73 % |

Les barres horizontales affichent ces 3 promotions avec leur %.

---

### 2.9 Salaire moyen
| Champ | Valeur |
|---|---|
| **Formule** | `AVG(CASE WHEN salary_annuel > 0 THEN salary_annuel ELSE salaire END)` — filtres `poste_actuel = TRUE`, salaire > 0, non anonymisés |
| **Tables / colonnes** | `EXPERIENCE_PRO.salary_annuel`, `salaire`, `poste_actuel` |
| **Fourchette jauge** | si ≥ 5 salaires → `[min × 0.9, max × 1.1]` ; sinon `[valeur × 0.7, valeur × 1.3]` + mention « Fourchette indicative — échantillon limité ». |
| **Exclusions / limites** | Salaires nuls exclus. Échantillon < 5 → fourchette élargie artificiellement. |

**Exemple chiffré** — 3 postes actuels avec salaires annuels : 38 000 €, 42 000 €, 50 000 €.
```
Moyenne = (38000 + 42000 + 50000) / 3 = 43 333 €
min réel = 38 000, max réel = 50 000
n = 3 < 5  →  fourchette amputée : [43333 × 0.7, 43333 × 1.3] ≈ [30 333, 56 333]
→ mention "échantillon limité" affichée
```
Avec 5 salaires ou plus, la fourchette serait `[min × 0.9, max × 1.1]`, sans mention.

---

### 2.10 Répartition par type de contrat
| Champ | Valeur |
|---|---|
| **Formule** | Pour chaque type : `COUNT(*)` des **expériences en cours** (`poste_actuel = TRUE` ou dates en cours) |
| **Tables / colonnes** | `EXPERIENCE_PRO.type_contrat`, `poste_actuel`, `date_debut/date_fin` |
| **Exclusions / limites** | On compte des **expériences**, pas des alumni. Valeurs vides → « Non renseigné ». |

**Exemple chiffré** — 11 expériences en cours : 6 CDI, 3 CDD, 1 Stage, 1 (vide).
```
CDI 6, CDD 3, Stage 1, Non renseigné 1
```
Le graphique barres les affiche ; le type vide devient « Non renseigné ».

---

## 3. Endpoints API

| Endpoint | Description |
|---|---|
| `GET /admin/indicateurs` | Indicateurs principaux (taux d'emploi 6 mois/global par promotion avec `statut_maturite`/`date_reference`, `taux_reponse`, `alumni_actifs`, `total_alumni`, `salaire_moyen/min/max`, `salaires_renseignes`, `coherence_availability_poste_actuel`, `hypothese`, `source_de_verite`) |
| `GET /admin/indicateurs/secteurs` | Répartition par secteur `{secteur, count}` + `total_alumni` |
| `GET /admin/indicateurs/types-contrat` | Répartition par type de contrat (valeurs vides → « Non renseigné ») |
| `GET /admin/indicateurs/kpi-tag?tag=X` | Valeur d'un KPI spécifique (valeur, unité `%` ou `/5`, distribution, détail) |
| `GET /admin/indicateurs/kpi-tags` | Tous les tags KPI des questionnaires actifs, calculés automatiquement (un échec sur un tag ne fait pas échouer la route) |
| `GET /admin/indicateurs/kpi-tags-actifs` | Liste des tags `DISTINCT` des questionnaires actifs |
| `GET /admin/indicateurs/partenaires` | Indicateurs agrégés/anonymisés restreints aux alumni ayant accepté le partage de données |

---

## 4. Trajet dans le code (où chaque indicateur est calculé et affiché)

| Indicateur | Calcul backend | Affichage frontend |
|---|---|---|
| Total Alumni | `admin.py` `calculer_indicateurs()` → `total_all` | `AdminDashboard.jsx` KPI card « Total Alumni » |
| Alumni actifs | `calculer_indicateurs()` → `active_count` | KPI card « Alumni actifs » |
| Taux de complétion | → `taux_reponse` | KPI secondaire |
| Taux d'emploi 6 mois | `calculer_indicateurs()` → `taux_emploi_6mois` (+ par promotion) | KPI card + barres promotions |
| Taux d'emploi global | `calculer_indicateurs()` → par promotion `taux_emploi_pourcentage`, agrégé côté front | KPI card |
| Adéquation | `_calculer_kpi_tag(tag)` → `kpi-tags` | Carte KPI + donut/section |
| Salaire moyen | `calculer_indicateurs()` → `salaire_moyen/min/max` | Jauge « compteur » (fourchette dynamique calculée dans `AdminDashboard.jsx` via `calculerFourchetteSalaire`) |
| Secteur | `indicateurs_par_secteur()` | Donut |
| Type de contrat | `indicateurs_types_contrat()` | Barres |
| Promotion | `calculer_indicateurs()` → `indicateurs_par_promotion` + `taux_emploi_6mois_par_promotion` | Barres horizontales + timeline maturité |

---

## 5. Cas limites & alertes

- **Promotion sans fenêtre 6 mois écoulée** → taux `null`, `statut_maturite = "en_attente"` (affiché « en cours », jamais compté dans le global).
- **Statut déclaratif vs poste réel** : l'indicateur `coherence_availability_poste_actuel` mesure l'écart entre `availability_status` et la présence d'un poste en cours (exposé, pas masqué).
- **Adéquation sans réponse** : le dashboard affiche un état vide avec des instructions pour taguer une question KPI.
- **Échantillon salaire < 5** : fourchette élargie + mention « échantillon limité ».
- **RGPD / anonymisation** : les comptes anonymisés disparaissent de tous les indicateurs ; le salaire des anciens postes est neutralisé (`salaire = 0`) pour ne pas polluer la moyenne.
