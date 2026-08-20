"""Petits utilitaires partagés entre les routers."""
import re
import unicodedata
from typing import Any, Dict, List, Sequence

from fastapi import HTTPException


def refuser_compte_anonymise(cursor, id_etudiant: int) -> None:
    """Refuse toute écriture sur un compte déjà anonymisé (RGPD).

    Le frontend désactive déjà les boutons d'édition pour ces comptes ; ce
    garde-fou côté API empêche une réécriture accidentelle des données
    personnelles sur un compte anonymisé (PUT/PATCH /etudiants/{id}, ajout
    d'expérience/certification/consentement, réponses questionnaire, …), qui
    déferait l'anonymisation RGPD.

    À ne PAS appliquer aux routes du workflow d'anonymisation lui-même
    (POST /etudiants/{id}/anonymiser, traitement des demandes RGPD,
    archiver_consentement_refuse) : celles-ci passent par `_anonymiser_compte`
    en SQL direct et vérifient elles-mêmes le non-double anonymisation.
    """
    cursor.execute(
        "SELECT date_anonymisation FROM ETUDIANT WHERE id_etudiant = %s;",
        (id_etudiant,),
    )
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Étudiant introuvable.")
    if row[0] is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                "Ce compte est déjà anonymisé (RGPD) : toute modification est "
                "impossible. La suppression définitive différée est gérée par "
                "le workflow RGPD."
            ),
        )


def rows_to_dicts(cursor, rows: Sequence[Sequence[Any]]) -> List[Dict[str, Any]]:
    """Transforme un résultat de cursor (tuples positionnels) en liste de dicts,
    en s'appuyant sur les noms de colonnes réels de la requête.

    Remplace le pattern répété manuellement dans chaque route
    (`{"id_x": r[0], "nom": r[1], ...}`), fragile car il dépend de l'ordre
    exact des colonnes du SELECT.
    """
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def normalize_academic_slug(value: str | None) -> str:
    """Normalise un prénom ou nom en slug pour l'email académique.

    Règles appliquées (dans l'ordre) :
    - tout en minuscules ;
    - retrait des accents (é -> e, à -> a, ç -> c, …) ;
    - suppression des espaces et apostrophes (« O'Brien » -> « obrien ») ;
    - conservation des tirets existants (« Jean-Paul » -> « jean-paul ») ;
    - suppression de tout caractère non alphanumérique restant, avec
      normalisation des tirets multiples (pas de tiret en début/fin).
    """
    if not value:
        return ""
    decomposed = unicodedata.normalize("NFKD", str(value))
    ascii_value = decomposed.encode("ascii", "ignore").decode("ascii")
    slug = ascii_value.lower()
    slug = slug.replace(" ", "").replace("'", "").replace("\u2019", "")
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug
