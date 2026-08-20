"""
Service de purge définitive différée des comptes anonymisés (RGPD).

Utilisation CLI :
    python purge.py            # exécute la purge réelle
    python purge.py --dry-run  # prévisualisation sans suppression

Le service supprime définitivement les comptes ETUDIANT anonymisés depuis
plus de PURGE_DELAY_MONTHS mois (variable d'environnement, défaut 6).

Effets de la suppression d'un compte anonymisé :
  - CASCADE  : EXPERIENCE_PRO, OBTIENT, CONSENTEMENT_RGPD,
               REPONSE_QUESTIONNAIRE (données personnelles)
  - SET NULL : DEMANDE_RGPD (la demande reste pour l'historique, sans FK)
  - AUDIT_LOG reçoit une entrée récapitulative (aucune donnée personnelle)
"""
import argparse
import logging
from datetime import datetime

from config import settings
from database import get_db_connection
from routers.cleanup import _write_audit_log

logger = logging.getLogger(__name__)


def comptes_purgeables(cursor, delay_months=None):
    """Retourne les comptes anonymisés depuis plus de `delay_months` mois.

    Règles :
      - email au format ANONYMISE_<id>@anonymise.io (compte anonymisé)
      - date_anonymisation non nulle et plus ancienne que le seuil
      - aucune demande RGPD active (envoyee/en_traitement) rattachée au compte
    """
    if delay_months is None:
        delay_months = settings.purge_delay_months
    cursor.execute(
        """
        SELECT e.id_etudiant, e.date_anonymisation
        FROM ETUDIANT e
        WHERE e.email LIKE 'ANONYMISE_%@anonymise.io'
          AND e.date_anonymisation IS NOT NULL
          AND e.date_anonymisation <= NOW() - (%s * INTERVAL '1 month')
          AND NOT EXISTS (
              SELECT 1 FROM DEMANDE_RGPD d
              WHERE d.id_etudiant = e.id_etudiant
                AND d.statut IN ('envoyee', 'en_traitement')
          )
        ORDER BY e.date_anonymisation;
        """,
        (delay_months,),
    )
    return [{"id_etudiant": r[0], "date_anonymisation": r[1]} for r in cursor.fetchall()]


def purge_comptes_anonymises(cursor, delay_months=None, acteur="system", commit=True):
    """Supprime définitivement les comptes anonymisés éligibles.

    Ne touche jamais :
      - les comptes non anonymisés (email réel)
      - les comptes anonymisés depuis moins de delay_months
      - les comptes ayant encore une demande RGPD active (envoyee/en_traitement)
    """
    if delay_months is None:
        delay_months = settings.purge_delay_months

    eligible = comptes_purgeables(cursor, delay_months)
    ids = [c["id_etudiant"] for c in eligible]

    if ids:
        placeholders = ",".join(["%s"] * len(ids))
        cursor.execute(
            f"DELETE FROM ETUDIANT WHERE id_etudiant IN ({placeholders});",
            tuple(ids),
        )
        nb_supprimes = cursor.rowcount
    else:
        nb_supprimes = 0

    details = (
        f"Purge définitive de {nb_supprimes} compte(s) anonymisé(s) "
        f"(délai {delay_months} mois, date_exécution={datetime.now().isoformat(timespec='seconds')}, "
        f"ids={ids})"
    )
    _write_audit_log(cursor, "PURGE_COMPTES_ANONYMISES", details, nb_supprimes, acteur=acteur)

    if commit:
        cursor.connection.commit()
    else:
        cursor.connection.rollback()

    return {
        "delay_months": delay_months,
        "candidats": len(eligible),
        "purges": nb_supprimes,
        "ids": ids,
    }


def _main():
    parser = argparse.ArgumentParser(description="Purge définitive des comptes anonymisés")
    parser.add_argument("--dry-run", action="store_true", help="Prévisualisation sans suppression")
    args = parser.parse_args()

    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            candidats = comptes_purgeables(cursor)
            print(f"{len(candidats)} compte(s) éligible(s) à la purge (délai {settings.purge_delay_months} mois) :")
            for c in candidats:
                print(f"  - id={c['id_etudiant']}  anonymisé le {c['date_anonymisation']}")

            if args.dry_run:
                print("Mode dry-run : aucune suppression effectuée.")
                return

            if not candidats:
                print("Rien à purger.")
                return

            resultat = purge_comptes_anonymises(cursor, acteur="cli")
            print(f"Purge terminée : {resultat['purges']} compte(s) supprimé(s).")
        finally:
            cursor.close()


if __name__ == "__main__":
    _main()
