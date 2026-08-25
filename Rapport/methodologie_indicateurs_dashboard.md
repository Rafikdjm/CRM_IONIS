# Methodologie — Indicateurs du Dashboard Alumni CRM

## Objectif

Transformer les donnees collectees par le CRM en indicateurs de pilotage pour les organismes de tutelle (CTI, HCERES) et le service des relations entreprises.

---

## Indicateurs cles

| Indicateur | Formule | Source |
|---|---|---|
| **Taux d'emploi a 6 mois** | Alumni avec experience debutant <= 6 mois apres diplomation / total promotion | EXPERIENCE_PRO (date_debut) |
| **Taux d'emploi global** | (Alumni avec experience / total alumni) x 100 | EXPERIENCE_PRO |
| **Adequation formation/emploi** | Reponses a la question taggee `adequation_formation` | REPONSE_QUESTIONNAIRE (tag KPI) |
| **Salaire moyen** | AVG/MIN/MAX sur `salary_annuel` (> 0) des experiences en cours | EXPERIENCE_PRO |
| **Alumni actifs** | Alumni avec >= 1 experience enregistree | EXPERIENCE_PRO |
| **Taux de completion** | Alumni ayant complete profil + parcours | ETUDIANT + EXPERIENCE_PRO |
| **Alumni par promotion** | Comptage par id_promotion | ETUDIANT + PROMOTION |
| **Repartition par secteur** | Agrégation du champ secteur_activite | ENTREPRISE |

### Regles de calcul

- **Taux d'emploi a 6 mois** : hypothese de diplomation en juin ; date de reference = 1er decembre de l'annee de diplome. Les cohortes dont la fenetre de 6 mois n'est pas ecoulee renvoient `null` (statut `en_attente`).
- **Salaire moyen** : repli sur le champ texte `salaire` pour les donnees historiques sans `salary_annuel`. Salaires a zero exclus.
- **Tags KPI** : chaque question de questionnaire peut porter un tag (ex: `adequation_formation`). L'ajout d'un tag fait apparaitre l'indicateur dans le dashboard sans modification du code backend.

---

## Endpoints API

| Endpoint | Description |
|---|---|
| `GET /admin/indicateurs` | Indicateurs principaux (taux d'emploi, salaire, completion) |
| `GET /admin/indicateurs/secteurs` | Repartition par secteur d'activite |
| `GET /admin/indicateurs/types-contrat` | Repartition par type de contrat |
| `GET /admin/indicateurs/kpi-tag?tag=X` | Valeur d'un indicateur KPI specifique |
| `GET /admin/indicateurs/kpi-tags` | Tous les tags KPI calcules automatiquement |
| `GET /admin/indicateurs/kpi-tags-actifs` | Liste des tags DISTINCT des questionnaires actifs |

---

## Visualisation (AdminDashboard.jsx)

- **KPI cards** : Total Alumni actifs, Taux d'emploi 6 mois, Taux d'emploi global
- **KPI secondaires** : Taux de completion, Adequation formation/emploi, Salaire moyen (jauge dynamique)
- **Donut** : Repartition par secteur (max 5 categories + "Autres")
- **Barres horizontales** : Alumni par promotion avec timeline de maturite
- **Barres** : Repartition des types de contrat

---

## Modele de rapport ministeriel

| Indicateur | Calcul |
|---|---|
| Effectif de la promotion | `COUNT(etudiants WHERE id_promotion = X)` |
| Taux d'emploi a 6 mois | Alumni avec experience debutant <= 6 mois / total promotion |
| Taux d'emploi a 12 mois | Alumni avec experience debutant <= 12 mois / total promotion |
| Adequation formation-emploi | Reponses KPI tag / total repondants |
| Salaire moyen par filiere | AVG/MIN/MAX sur salary_annuel (> 0) |
| Repartition par secteur | COUNT(experiences WHERE secteur = X) / total |
