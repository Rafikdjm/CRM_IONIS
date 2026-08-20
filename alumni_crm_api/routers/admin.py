import json
import logging
from collections import Counter
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from database import get_db
from security import require_admin_api_key
from utils import rows_to_dicts

logger = logging.getLogger(__name__)

# Toutes les routes de ce router exposent des donnees personnelles et/ou
# salariales : elles sont protegees par une cle API (header X-API-Key).
router = APIRouter(prefix="/admin", dependencies=[Depends(require_admin_api_key)])

# Statuts "en emploi" de availability_status (a maintenir en coherence avec
# _VALID_AVAILABILITY_STATUS dans routers/etudiants.py). Ils n'entrent pas
# dans le calcul des taux (EXPERIENCE_PRO fait foi : poste_actuel ou
# experience en cours, voir _condition_emploi_en_cours), mais servent
# a mesurer la coherence entre le statut declaratif et la source structuree.
_AVAILABILITY_EMPLOYED = {"en_poste", "a_lecoute"}

# Libelles affichables des tags KPI connus du questionnaire. Tout tag non liste
# ici est formate generiquement (underscores -> espaces, premiere lettre en
# majuscule) via _formater_libelle_tag.
_KPI_TAG_LIBELLES = {
    "adequation_formation": "Adéquation formation/emploi",
    "taux_recommandation": "Taux de recommandation",
    "statut_professionnel": "Statut professionnel",
}


def _formater_libelle_tag(tag: str) -> str:
    """Transforme un tag technique en libelle lisible pour le Dashboard."""
    libelle = _KPI_TAG_LIBELLES.get(tag)
    if libelle:
        return libelle
    return tag.replace("_", " ").capitalize()


def _condition_emploi_en_cours(alias: str = "exp") -> str:
    """Condition SQL définissant un alumni "en emploi" aujourd'hui.

    Un poste compte comme emploi en cours si :
      - il est explicitement marqué actuel (EXPERIENCE_PRO.poste_actuel = TRUE),
        OU
      - il est structurellement en cours aujourd'hui : début passé ou en cours
        (date_debut <= CURRENT_DATE) et pas de date de fin, ou une date de fin
        pas encore atteinte (date_fin >= CURRENT_DATE).

    La clause de dates rend le calcul robuste quand le flag poste_actuel n'a
    pas été renseigné (ex. expérience saisie sans cocher "Poste actuel" ou
    importée sans la colonne) alors que l'expérience est manifestement le
    poste actuel de l'alumni. Elle reste cohérente avec la logique du taux à
    6 mois, qui compte une expérience "active" à la date de référence.
    """
    return (
        f"({alias}.poste_actuel = TRUE "
        f"OR ({alias}.date_debut <= CURRENT_DATE "
        f"AND ({alias}.date_fin IS NULL OR {alias}.date_fin >= CURRENT_DATE)))"
    )


@router.get("/etudiants/filtrer", tags=["Interface Administration"])
def filtrer_anciens(
    promotion: str = Query(None, description="Filtrer par nom de promotion"),
    secteur: str = Query(None, description="Filtrer par secteur d'activite"),
    entreprise: str = Query(None, description="Filtrer par nom d'entreprise"),
    contact_autorise: str = Query(None, description="Filtrer par consentement prise_de_contact (actif/refuse)"),
    anonymise: str = Query(None, description="Filtrer par anonymisation RGPD (actifs/exclus / anonymises)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    db=Depends(get_db),
):
    cursor = db.cursor()
    try:
        query = """
            SELECT e.id_etudiant, e.nom, e.prenom, e.email, p.nom_promotion,
                   exp.intitule_poste, ent.nom_entreprise, ent.secteur_activite,
                   e.availability_status, e.date_anonymisation,
                   COALESCE((
                       SELECT c.statut FROM CONSENTEMENT_RGPD c
                       WHERE c.id_etudiant = e.id_etudiant
                         AND c.type_consentement = 'prise_de_contact'
                       ORDER BY c.date_consentement DESC, c.id_consentement DESC
                       LIMIT 1
                   ), 'inconnu') AS contact_autorise
            FROM ETUDIANT e
            JOIN PROMOTION p ON e.id_promotion = p.id_promotion
            LEFT JOIN EXPERIENCE_PRO exp ON e.id_etudiant = exp.id_etudiant AND exp.poste_actuel = TRUE
            LEFT JOIN ENTREPRISE ent ON exp.id_entreprise = ent.id_entreprise
            WHERE 1=1
        """
        params = []

        if anonymise == "actifs":
            query += " AND e.date_anonymisation IS NULL"
        elif anonymise == "anonymises":
            query += " AND e.date_anonymisation IS NOT NULL"
        elif anonymise:
            raise HTTPException(
                status_code=422,
                detail="Parametre 'anonymise' invalide. Valeurs attendues : actifs, anonymises.",
            )

        if promotion:
            query += " AND p.nom_promotion = %s"
            params.append(promotion)

        if secteur:
            query += " AND ent.secteur_activite = %s"
            params.append(secteur)

        if entreprise:
            query += " AND ent.nom_entreprise = %s"
            params.append(entreprise)

        if contact_autorise in ("actif", "refuse"):
            query += """
                AND COALESCE((
                    SELECT c2.statut FROM CONSENTEMENT_RGPD c2
                    WHERE c2.id_etudiant = e.id_etudiant
                      AND c2.type_consentement = 'prise_de_contact'
                    ORDER BY c2.date_consentement DESC, c2.id_consentement DESC
                    LIMIT 1
                ), 'inconnu') = %s
            """
            params.append(contact_autorise)

        query += " ORDER BY e.nom, e.prenom LIMIT %s OFFSET %s"
        params.extend([limit, skip])

        cursor.execute(query, tuple(params))
        return {"anciens_eleves": rows_to_dicts(cursor, cursor.fetchall())}
    except Exception:
        logger.exception("Erreur lors du filtrage des anciens")
        raise HTTPException(status_code=400, detail="Impossible de filtrer les anciens eleves.")
    finally:
        cursor.close()


@router.get("/indicateurs", tags=["Analyse des indicateurs d'insertion"])
def calculer_indicateurs(db=Depends(get_db)):
    cursor = db.cursor()
    try:
        # ── 1. Indicateurs par promotion ────────────────────────────────
        # Source de verite du taux d'emploi : EXPERIENCE_PRO. Un alumni est
        # compté en emploi si une de ses expériences est son poste actuel
        # (flag poste_actuel) OU une expérience en cours aujourd'hui (dates) ;
        # voir _condition_emploi_en_cours. Le champ declaratif
        # ETUDIANT.availability_status n'entre PAS dans le calcul (il peut
        # etre obsolet) ; l'ecart eventuel est mesure et expose en point 3
        # plutot qu'ignore silencieusement.
        emploi_en_cours = _condition_emploi_en_cours("exp")
        promo_query = f"""
            SELECT
                p.nom_promotion,
                p.annee_diplome,
                COUNT(DISTINCT e.id_etudiant) AS total_etudiants,
                COUNT(DISTINCT CASE WHEN {emploi_en_cours} THEN e.id_etudiant END) AS etudiants_en_poste,
                COUNT(DISTINCT CASE WHEN exp.id_experience IS NOT NULL THEN e.id_etudiant END) AS etudiants_avec_experience,
                ROUND(AVG(CASE WHEN {emploi_en_cours} THEN exp.salaire END), 2) AS salaire_moyen
            FROM PROMOTION p
            LEFT JOIN ETUDIANT e ON p.id_promotion = e.id_promotion AND e.date_anonymisation IS NULL
            LEFT JOIN EXPERIENCE_PRO exp ON e.id_etudiant = exp.id_etudiant
            GROUP BY p.nom_promotion, p.annee_diplome
            ORDER BY p.annee_diplome DESC;
        """
        cursor.execute(promo_query)
        promo_results = rows_to_dicts(cursor, cursor.fetchall())

        for row in promo_results:
            total = row["total_etudiants"]
            en_poste = row["etudiants_en_poste"]
            couverts = row["etudiants_avec_experience"]
            row["taux_emploi_pourcentage"] = round(
                (en_poste / total * 100) if total > 0 else 0, 2
            )
            # Taux de couverture : % d'alumni de la promotion avec au moins
            # une experience renseignee. Contextualise le taux d'emploi, qui
            # est sous-estime si beaucoup d'alumni n'ont aucune experience.
            row["taux_couverture"] = round(
                (couverts / total * 100) if total > 0 else 0, 2
            )

        # ── 2. Taux d'emploi a 6 mois apres le diplome, PAR PROMOTION ──
        # Hypothese (faute d'une vraie date de diplome en base) : diplomation
        # en juin de l'annee de diplome, donc la reference "+6 mois" est le
        # 1er decembre de cette meme annee. Limitation connue, exposee dans la
        # reponse API (champ "hypothese").
        # Une experience compte si elle ETAIT ACTIVE a la date de reference :
        #   date_debut <= reference AND (date_fin IS NULL OR date_fin >= reference)
        # (une experience deja terminee avant le 1er decembre n'est pas un
        # emploi "a 6 mois").
        # Figeage de cohorte : une promotion dont la fenetre de 6 mois n'est
        # pas encore ecoulee (date du jour < date_reference) est EXCLUE du
        # taux global et marquee "en_attente" : la compter produirait un
        # instantane trompeur pour les promos recentes.
        taux_6m_query = """
            SELECT
                p.id_promotion,
                p.nom_promotion,
                p.annee_diplome,
                (p.annee_diplome || '-12-01')::date AS date_reference,
                COUNT(DISTINCT e.id_etudiant) AS total_diplomes,
                COUNT(DISTINCT CASE
                    WHEN EXISTS (
                        SELECT 1 FROM EXPERIENCE_PRO exp2
                        WHERE exp2.id_etudiant = e.id_etudiant
                          AND exp2.date_debut <= (p.annee_diplome || '-12-01')::date
                          AND (exp2.date_fin IS NULL OR exp2.date_fin >= (p.annee_diplome || '-12-01')::date)
                    ) THEN e.id_etudiant
                END) AS emplois_6_mois
            FROM ETUDIANT e
            JOIN PROMOTION p ON e.id_promotion = p.id_promotion
            WHERE e.date_anonymisation IS NULL
            GROUP BY p.id_promotion, p.nom_promotion, p.annee_diplome
            ORDER BY p.annee_diplome DESC;
        """
        cursor.execute(taux_6m_query)
        colonnes_6m = [d[0] for d in cursor.description]
        par_promotion_6m = []
        total_diplomes_matures = 0
        emplois_6m_matures = 0
        for row in cursor.fetchall():
            d = dict(zip(colonnes_6m, row))
            date_reference = d["date_reference"]
            mature = date_reference <= date.today()
            total = d["total_diplomes"]
            emplois = d["emplois_6_mois"]
            if mature and total > 0:
                total_diplomes_matures += total
                emplois_6m_matures += emplois
                taux_6m = round((emplois / total * 100), 2)
                statut_maturite = "mature"
            elif mature:
                taux_6m = 0.0
                statut_maturite = "mature"
            else:
                taux_6m = None
                statut_maturite = "en_attente"
            # Couverture deja calculee pour la meme promotion a l'etape 1.
            couverture = next(
                (
                    r["taux_couverture"]
                    for r in promo_results
                    if r["nom_promotion"] == d["nom_promotion"]
                    and r["annee_diplome"] == d["annee_diplome"]
                ),
                None,
            )
            par_promotion_6m.append(
                {
                    "nom_promotion": d["nom_promotion"],
                    "annee_diplome": d["annee_diplome"],
                    "date_reference": date_reference.isoformat(),
                    "statut_maturite": statut_maturite,
                    "total_diplomes": total,
                    "emplois_6_mois": emplois,
                    "taux_emploi_6mois_pourcentage": taux_6m,
                    "taux_couverture": couverture,
                }
            )

        # Taux global restreint aux cohortes matures (fenetre de 6 mois
        # refermee) : aucun resultat si aucune promotion n'est encore mature.
        if total_diplomes_matures > 0:
            taux_emploi_6mois = round(
                (emplois_6m_matures / total_diplomes_matures * 100), 2
            )
        else:
            taux_emploi_6mois = None

        # ── 3. Coherence availability_status / emploi en cours ──────────
        # La definition d'emploi est celle de l'etape 1 (poste_actuel OU
        # experience en cours aujourd'hui). On compte les etudiants dont le
        # statut DECLARATIF contredit la source structuree :
        #   - statut "en emploi" (en_poste / a_lecoute) mais aucun poste en cours ;
        #   - statut "en_recherche" mais un poste en cours.
        coherence_emploi = _condition_emploi_en_cours("expc")
        coherence_query = f"""
            SELECT e.id_etudiant, e.availability_status,
                   EXISTS (
                       SELECT 1 FROM EXPERIENCE_PRO expc
                       WHERE expc.id_etudiant = e.id_etudiant
                         AND {coherence_emploi}
                       ) AS a_poste_actuel
            FROM ETUDIANT e
            WHERE e.date_anonymisation IS NULL;
        """
        cursor.execute(coherence_query)
        etudiants_analysables = 0
        etudiants_incoherents = 0
        for _, statut, a_poste in cursor.fetchall():
            if statut in _AVAILABILITY_EMPLOYED:
                etudiants_analysables += 1
                if not a_poste:
                    etudiants_incoherents += 1
            elif statut == "en_recherche":
                etudiants_analysables += 1
                if a_poste:
                    etudiants_incoherents += 1
            # autres valeurs / champ vide : non analysables, ignorees.

        # ── 4. Couverture globale : alumni non-anonymises ayant au moins ──
        # une experience renseignee.
        active_query = """
            SELECT COUNT(DISTINCT exp.id_etudiant)
            FROM EXPERIENCE_PRO exp
            JOIN ETUDIANT e ON exp.id_etudiant = e.id_etudiant
                AND e.date_anonymisation IS NULL;
        """
        cursor.execute(active_query)
        active_count = cursor.fetchone()[0]

        total_query = "SELECT COUNT(*) FROM ETUDIANT WHERE date_anonymisation IS NULL;"
        cursor.execute(total_query)
        total_all = cursor.fetchone()[0]
        taux_reponse = round(
            (active_count / total_all * 100) if total_all > 0 else 0, 2
        )

        # ── 5. Salaire moyen global (et dispersion min/max) ─────────────
        # Moyenne calculee uniquement sur les experiences EN COURS
        # (definie par _condition_emploi_en_cours, comme le taux d'emploi)
        # et dont le salaire est strictement positif : un salaire a 0 est
        # un defaut de saisie, pas une donnee exploitable, et il tirerait
        # artificiellement la moyenne vers le bas.
        # Le MIN et le MAX des salaires du meme perimetre sont exposes pour
        # le frontend : ils servent a calculer DYNAMIQUEMENT la fourchette de
        # la jauge "Salaire moyen" du Dashboard. Cette fourchette est ainsi
        # entierement derivee des donnees internes du CRM (min/max reels des
        # salaires renseignes), sans aucune reference de marche externe,
        # conformement a l'exigence du sujet de stage : tous les indicateurs
        # d'insertion sont calcules a partir des donnees collectees par le CRM.
        salaire_query = f"""
            SELECT ROUND(AVG(CASE WHEN exp.salary_annuel > 0 THEN exp.salary_annuel ELSE exp.salaire END), 2) AS salaire_moyen,
                   COUNT(*) AS salaires_renseignes,
                   MIN(CASE WHEN exp.salary_annuel > 0 THEN exp.salary_annuel ELSE exp.salaire END) AS salaire_min,
                   MAX(CASE WHEN exp.salary_annuel > 0 THEN exp.salary_annuel ELSE exp.salaire END) AS salaire_max
            FROM EXPERIENCE_PRO exp
            JOIN ETUDIANT e ON exp.id_etudiant = e.id_etudiant
                AND e.date_anonymisation IS NULL
            WHERE {emploi_en_cours} AND (exp.salary_annuel > 0 OR exp.salaire > 0);
        """
        cursor.execute(salaire_query)
        sal_row = cursor.fetchone()
        salaire_moyen = float(sal_row[0]) if sal_row[0] is not None else None
        salaires_renseignes = int(sal_row[1] or 0)
        salaire_min = float(sal_row[2]) if sal_row[2] is not None else None
        salaire_max = float(sal_row[3]) if sal_row[3] is not None else None

        return {
            "hypothese": (
                "diplomation juin, delai approxime : date de reference = "
                "annee_diplome-12-01 (+6 mois), faute d'une date de diplome en base"
            ),
            "source_de_verite": (
                "EXPERIENCE_PRO : poste_actuel = TRUE OU experience en cours "
                "(date_debut <= aujourd'hui et pas de date de fin passee) ; "
                "availability_status est declaratif et n'entre pas dans les taux"
            ),
            "indicateurs_par_promotion": promo_results,
            "taux_emploi_6mois_par_promotion": par_promotion_6m,
            "taux_emploi_6mois": taux_emploi_6mois,
            "total_diplomes_matures": total_diplomes_matures,
            "emplois_6_mois_matures": emplois_6m_matures,
            "coherence_availability_poste_actuel": {
                "source_de_verite": "poste_actuel",
                "etudiants_analysables": etudiants_analysables,
                "etudiants_incoherents": etudiants_incoherents,
                "taux_incoherence_pourcentage": round(
                    (etudiants_incoherents / etudiants_analysables * 100)
                    if etudiants_analysables > 0
                    else 0,
                    2,
                ),
            },
            "alumni_actifs": active_count,
            "taux_reponse": taux_reponse,
            "total_alumni": total_all,
            "salaire_moyen": salaire_moyen,
            "salaires_renseignes": salaires_renseignes,
            "salaire_min": salaire_min,
            "salaire_max": salaire_max,
        }
    except Exception:
        logger.exception("Erreur lors du calcul des indicateurs d'insertion")
        raise HTTPException(status_code=400, detail="Impossible de calculer les indicateurs.")
    finally:
        cursor.close()


@router.get("/indicateurs/secteurs", tags=["Analyse des indicateurs d'insertion"])
def indicateurs_par_secteur(db=Depends(get_db)):
    cursor = db.cursor()
    try:
        # Chaque alumni actif (non anonymise) est affecte a EXACTEMENT un
        # segment : le secteur de l'entreprise de son experience professionnelle
        # la plus recente en cours (meme logique _condition_emploi_en_cours que
        # le taux d'emploi). Un alumni sans experience en cours, ou dont le
        # secteur de l'entreprise est inconnu/vide, tombe dans le segment
        # "Non renseigne" (secteur NULL). Ainsi la somme des segments du
        # camembert est toujours egale au total des alumni actifs affiche
        # cote frontend, sans segment manquant.
        emploi_en_cours = _condition_emploi_en_cours("exp")
        query = f"""
            WITH secteur_alumni AS (
                SELECT
                    e.id_etudiant,
                    (
                        SELECT ent.secteur_activite
                        FROM EXPERIENCE_PRO exp
                        JOIN ENTREPRISE ent ON exp.id_entreprise = ent.id_entreprise
                        WHERE exp.id_etudiant = e.id_etudiant
                          AND {emploi_en_cours}
                          AND ent.secteur_activite IS NOT NULL
                          AND ent.secteur_activite != ''
                        ORDER BY exp.date_debut DESC, exp.id_experience DESC
                        LIMIT 1
                    ) AS secteur
                FROM ETUDIANT e
                WHERE e.date_anonymisation IS NULL
            )
            SELECT secteur, COUNT(*) AS count
            FROM secteur_alumni
            GROUP BY secteur
            ORDER BY count DESC, secteur ASC NULLS LAST;
        """
        cursor.execute(query)
        secteurs = rows_to_dicts(cursor, cursor.fetchall())

        cursor.execute("SELECT COUNT(*) FROM ETUDIANT WHERE date_anonymisation IS NULL;")
        total_alumni = cursor.fetchone()[0]

        return {"secteurs": secteurs, "total_alumni": total_alumni}
    except Exception:
        logger.exception("Erreur lors du calcul des indicateurs sectoriels")
        raise HTTPException(status_code=400, detail="Impossible de calculer les indicateurs sectoriels.")
    finally:
        cursor.close()


@router.get("/indicateurs/types-contrat", tags=["Analyse des indicateurs d'insertion"])
def indicateurs_types_contrat(db=Depends(get_db)):
    """Repartition des experiences PROFESSIONNELLES EN COURS par type de contrat.

    Une experience est compte "en cours" selon la meme regle que le taux
    d'emploi (poste_actuel = TRUE OU experience structurellement active,
    voir _condition_emploi_en_cours). On compte les EXPERIENCES, pas les
    alumni : l'objectif est de voir la nature des contrats (CDI, CDD,
    Stage, Alternance...) occupes actuellement.

    Les types sont renvoyes tels que saisis (EXPERIENCE_PRO.type_contrat
    est une saisie libre) ; un type NULL ou vide est affiche sous le
    libelle "Non renseigne" pour ne pas perdre de valeur sans la melanger
    avec les autres.
    """
    cursor = db.cursor()
    try:
        emploi_en_cours = _condition_emploi_en_cours("exp")
        query = f"""
            SELECT NULLIF(TRIM(exp.type_contrat), '') AS type_contrat,
                   COUNT(*) AS count
            FROM EXPERIENCE_PRO exp
            JOIN ETUDIANT e ON exp.id_etudiant = e.id_etudiant
                AND e.date_anonymisation IS NULL
            WHERE {emploi_en_cours}
            GROUP BY type_contrat
            ORDER BY count DESC, type_contrat ASC NULLS LAST;
        """
        cursor.execute(query)
        types = rows_to_dicts(cursor, cursor.fetchall())
        return {"types_contrat": types}
    except Exception:
        logger.exception("Erreur lors du calcul des types de contrat")
        raise HTTPException(status_code=400, detail="Impossible de calculer les types de contrat.")
    finally:
        cursor.close()


def _est_absence_poste(answer: str) -> bool:
    """Reponses qui signifient explicitement "pas de poste" (exclues du calcul)."""
    return answer.lower() in ("non applicable", "non_applicable", "n/a", "na")


def _arrondir_pourcentage(valeur: float) -> float:
    """Arrondit un pourcentage a 1 decimale, sans suffixe ".0" inutile."""
    arrondi = round(valeur, 1)
    return float(int(arrondi)) if arrondi.is_integer() else arrondi


def _format_pourcentage(valeur: float) -> str:
    """Formatte un pourcentage pour un libelle : "100" au lieu de "100.0"."""
    arrondi = round(valeur, 1)
    return str(int(arrondi)) if arrondi.is_integer() else str(arrondi)


def _calculer_kpi_tag(db, tag: str) -> dict:
    """Calcule le KPI d'un tag, adapte au TYPE de question associee.

    - boolean (Oui/Non) : % de reponses "Oui".
    - choice (choix parmi une liste) : distribution en % par choix ; la
      valeur principale est le % du choix le plus frequent, avec son libelle.
    - rating (echelle numerique, ex. note 1-5) : moyenne (X/max) + % de notes
      au-dessus du seuil (80% de l'echelle), car un simple comptage de "oui"
      ne peut pas representer ce type de donnee.

    Logique partagee par GET /admin/indicateurs/kpi-tag et
    GET /admin/indicateurs/kpi-tags (aucune duplication).
    """
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT q.id_question, q.texte, q.type, q.options, q.id_questionnaire "
            "FROM QUESTION q "
            "JOIN QUESTIONNAIRE qn ON q.id_questionnaire = qn.id_questionnaire "
            "WHERE q.tag = %s AND qn.actif = TRUE "
            "ORDER BY qn.date_creation DESC LIMIT 1;",
            (tag,),
        )
        qrow = cursor.fetchone()
        if not qrow:
            return {
                "tag": tag,
                "question_texte": None,
                "question_type": None,
                "total_repondants": 0,
                "valeur": None,
                "unite": None,
                "libelle_valeur": None,
                "distribution": None,
                "detail": None,
            }

        q_id, q_texte, q_type, q_options, id_questionnaire = qrow
        q_id_str = str(q_id)

        options = []
        if isinstance(q_options, str):
            try:
                options = json.loads(q_options) or []
            except (json.JSONDecodeError, TypeError):
                options = []
        elif isinstance(q_options, list):
            options = q_options

        cursor.execute(
            "SELECT r.reponses FROM REPONSE_QUESTIONNAIRE r "
            "JOIN ETUDIANT e ON r.id_etudiant = e.id_etudiant "
            "WHERE r.id_questionnaire = %s AND e.date_anonymisation IS NULL;",
            (id_questionnaire,),
        )
        rows = cursor.fetchall()
        reponses = []
        for row in rows:
            raw = row[0]
            if isinstance(raw, str):
                try:
                    raw = json.loads(raw)
                except (json.JSONDecodeError, TypeError):
                    continue
            if raw and q_id_str in raw:
                answer = str(raw[q_id_str]).strip()
                # Exclure les reponses indiquant l'absence de poste
                if _est_absence_poste(answer):
                    continue
                reponses.append(answer)

        total_repondants = len(reponses)

        base = {
            "tag": tag,
            "question_texte": q_texte,
            "question_type": q_type,
            "total_repondants": total_repondants,
            "unite": "%",
            "distribution": None,
            "detail": None,
        }

        if total_repondants == 0:
            return {**base, "valeur": None, "libelle_valeur": None}

        def _distribution(compteur) -> list:
            items = [
                {
                    "label": label,
                    "nb": nb,
                    "pourcentage": _arrondir_pourcentage(nb / total_repondants * 100),
                }
                for label, nb in compteur.items()
            ]
            items.sort(key=lambda x: (-x["nb"], x["label"]))
            return items

        # --- Question Oui/Non : % de "oui" -------------------------------
        if q_type == "boolean":
            compteur = {"Oui": 0, "Non": 0}
            for answer in reponses:
                if answer.lower() in ("oui", "yes", "true", "1", "vrai"):
                    compteur["Oui"] += 1
                else:
                    compteur["Non"] += 1
            # libelle_valeur = choix majoritaire reel (jamais code en dur sur
            # "Oui") : le sous-titre du Dashboard doit rester coherent avec le
            # pourcentage principal affiche (ex. 0% "Oui" => majorite "Non").
            # En cas d'egalite, on retient "Oui", coherent avec la valeur
            # principale qui reste le % de reponses "Oui".
            dominant_label = "Oui" if compteur["Oui"] >= compteur["Non"] else "Non"
            return {
                **base,
                "valeur": _arrondir_pourcentage(compteur["Oui"] / total_repondants * 100),
                "libelle_valeur": dominant_label,
                "distribution": _distribution(compteur),
            }

        # --- Question a choix : distribution, + % du choix le plus frequent
        if q_type == "choice":
            compteur = Counter(reponses)
            dominant, dominant_nb = compteur.most_common(1)[0]
            return {
                **base,
                "valeur": _arrondir_pourcentage(dominant_nb / total_repondants * 100),
                "libelle_valeur": dominant,
                "distribution": _distribution(compteur),
            }

        # --- Question a echelle numerique : moyenne + % au-dessus d'un seuil
        if q_type == "rating":
            notes = []
            for answer in reponses:
                try:
                    notes.append(float(answer))
                except ValueError:
                    continue
            if not notes:
                return {**base, "valeur": None, "libelle_valeur": None, "unite": None}

            note_max = 5
            for o in options:
                try:
                    note_max = int(o)
                    break
                except (TypeError, ValueError):
                    continue

            moyenne = round(sum(notes) / len(notes), 1)
            seuil = max(1, int(round(note_max * 0.8)))
            notes_sur_seuil = sum(1 for n in notes if n >= seuil)
            compteur = {}
            for n in sorted(set(notes)):
                cle = str(int(n)) if n.is_integer() else str(n)
                compteur[cle] = sum(1 for v in notes if v == n)

            return {
                **base,
                "unite": "/%d" % note_max,
                "valeur": moyenne,
                "libelle_valeur": "Note moyenne",
                "distribution": _distribution(compteur),
                "detail": (
                    "%s%% de notes >= %d/%d"
                    % (_format_pourcentage(notes_sur_seuil / len(notes) * 100), seuil, note_max)
                ),
            }

        # --- Autre type (texte, etc.) : aucun KPI numerique calculable
        return {**base, "valeur": None, "libelle_valeur": None, "unite": None}
    except Exception:
        logger.exception("Erreur lors du calcul du KPI tag: %s", tag)
        raise
    finally:
        cursor.close()


@router.get("/indicateurs/kpi-tag", tags=["Analyse des indicateurs d'insertion"])
def calculer_kpi_tag(tag: str = Query("adequation_formation"), db=Depends(get_db)):
    try:
        return _calculer_kpi_tag(db, tag)
    except Exception:
        raise HTTPException(status_code=400, detail="Impossible de calculer le KPI.")


@router.get("/indicateurs/kpi-tags-actifs", tags=["Analyse des indicateurs d'insertion"])
def lister_kpi_tags_actifs(db=Depends(get_db)):
    """Liste les tags DISTINCT utilises par des questions de questionnaires actifs."""
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT DISTINCT q.tag "
            "FROM QUESTION q "
            "JOIN QUESTIONNAIRE qn ON q.id_questionnaire = qn.id_questionnaire "
            "WHERE qn.actif = TRUE AND q.tag IS NOT NULL AND q.tag != '' "
            "ORDER BY q.tag;"
        )
        return {"tags": [row[0] for row in cursor.fetchall()]}
    except Exception:
        logger.exception("Erreur lors du listing des tags KPI actifs")
        raise HTTPException(status_code=400, detail="Impossible de lister les tags KPI actifs.")
    finally:
        cursor.close()


@router.get("/indicateurs/kpi-tags", tags=["Analyse des indicateurs d'insertion"])
def calculer_kpi_tags(db=Depends(get_db)):
    """Tous les tags KPI des questionnaires actifs, calcules automatiquement.

    Retourne directement la liste : [{tag, libelle, pourcentage, nb_repondants,
    question_type, valeur, unite, libelle_valeur, distribution, detail}, ...].
    Un tag est toujours renvoye, meme sans reponse (pourcentage None, nb_repondants 0).
    """
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT DISTINCT q.tag "
            "FROM QUESTION q "
            "JOIN QUESTIONNAIRE qn ON q.id_questionnaire = qn.id_questionnaire "
            "WHERE qn.actif = TRUE AND q.tag IS NOT NULL AND q.tag != '' "
            "ORDER BY q.tag;"
        )
        tags = [row[0] for row in cursor.fetchall()]
    except Exception:
        logger.exception("Erreur lors du listing des tags KPI actifs")
        raise HTTPException(status_code=400, detail="Impossible de lister les tags KPI actifs.")
    finally:
        cursor.close()

    resultats = []
    for tag in tags:
        try:
            kpi = _calculer_kpi_tag(db, tag)
        except Exception:
            # Un echec de calcul sur un tag ne doit pas faire echouer la route :
            # on renvoie le tag avec des valeurs vides (et on restaure la
            # connexion en cas de transaction abandonee).
            db.rollback()
            kpi = {
                "tag": tag,
                "question_texte": None,
                "question_type": None,
                "total_repondants": 0,
                "valeur": None,
                "unite": None,
                "libelle_valeur": None,
                "distribution": None,
                "detail": None,
            }
        # "pourcentage" reste le % reel pour les questions Oui/Non et a choix ;
        # pour une echelle numerique (rating), la valeur principale est une
        # moyenne, pas un pourcentage : pourcentage est donc None.
        est_pourcentage = kpi.get("unite") == "%"
        resultats.append(
            {
                "tag": tag,
                "libelle": _formater_libelle_tag(tag),
                "pourcentage": kpi.get("valeur") if est_pourcentage else None,
                "nb_repondants": kpi.get("total_repondants", 0),
                "question_type": kpi.get("question_type"),
                "valeur": kpi.get("valeur"),
                "unite": kpi.get("unite"),
                "libelle_valeur": kpi.get("libelle_valeur"),
                "distribution": kpi.get("distribution"),
                "detail": kpi.get("detail"),
            }
        )
    return resultats
