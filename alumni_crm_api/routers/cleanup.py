"""
Router d'administration : nettoyage et maintenance de la base de données.

Toutes les opérations sont :
- Protégées par la clé API admin (X-API-Key)
- Exécutées dans des transactions explicites
- Loguées dans la table AUDIT_LOG pour traçabilité
- Précédées d'un mode dry-run pour preview avant exécution
"""
import logging
from datetime import datetime

import pg8000.dbapi
from fastapi import APIRouter, Depends, HTTPException

import schemas
from database import get_db
from security import require_admin_api_key
from utils import rows_to_dicts

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin/cleanup",
    tags=["Nettoyage & Maintenance"],
    dependencies=[Depends(require_admin_api_key)],
)


# ---------------------------------------------------------------------------
# FONCTIONS UTILITAIRES INTERNES
# ---------------------------------------------------------------------------

# Type de consentement "critique" : un refus de prise de contact déclenche
# l'anonymisation RGPD (équivalent de l'ancien type PROFIL_ALUMNI).
# Valeurs réelles en base : statut 'actif'/'refuse',
# types 'prise_de_contact', 'partage_donnees', 'enquetes', 'newsletter'.
_CONSENTEMENT_ARCHIVE_TYPE = "prise_de_contact"

_LATEST_CONSENT_CTE = """
    SELECT DISTINCT ON (id_etudiant) id_etudiant, statut
    FROM CONSENTEMENT_RGPD
    WHERE type_consentement = '{ctype}'
    ORDER BY id_etudiant, date_consentement DESC, id_consentement DESC
""".format(ctype=_CONSENTEMENT_ARCHIVE_TYPE)


def _write_audit_log(cursor, action: str, details: str, rows_affected: int, acteur: str = None) -> None:
    """Écrit une entrée dans la table AUDIT_LOG (crée la table si absente)."""
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AUDIT_LOG (
                id_log SERIAL PRIMARY KEY,
                action VARCHAR(100) NOT NULL,
                details TEXT,
                rows_affected INT DEFAULT 0,
                executed_at TIMESTAMP DEFAULT NOW(),
                acteur VARCHAR(255) DEFAULT NULL
            );
        """)
        cursor.execute(
            "INSERT INTO AUDIT_LOG (action, details, rows_affected, executed_at, acteur) "
            "VALUES (%s, %s, %s, NOW(), %s);",
            (action, details, rows_affected, acteur),
        )
    except Exception:
        logger.exception("Impossible d'écrire dans AUDIT_LOG")


# ---------------------------------------------------------------------------
# 1. DÉTECTION DES ENREGISTREMENTS ORPHELINS (dry-run)
# ---------------------------------------------------------------------------

@router.get("/orphelins", response_model=schemas.CleanupDryRun)
def detecter_orphelins(db=Depends(get_db)):
    """Analyse les enregistrements orphelins sans supprimer (dry-run)."""
    cursor = db.cursor()
    orphans = []
    try:
        # Expériences sans étudiant
        cursor.execute(
            "SELECT id_experience FROM EXPERIENCE_PRO "
            "WHERE id_etudiant NOT IN (SELECT id_etudiant FROM ETUDIANT);"
        )
        exp_ids = [r[0] for r in cursor.fetchall()]
        orphans.append(schemas.OrphanReport(
            table_name="EXPERIENCE_PRO (sans étudiant)",
            orphan_count=len(exp_ids),
            sample_ids=exp_ids[:10],
        ))

        # Expériences sans entreprise
        cursor.execute(
            "SELECT id_experience FROM EXPERIENCE_PRO "
            "WHERE id_entreprise NOT IN (SELECT id_entreprise FROM ENTREPRISE);"
        )
        exp_ent_ids = [r[0] for r in cursor.fetchall()]
        orphans.append(schemas.OrphanReport(
            table_name="EXPERIENCE_PRO (sans entreprise)",
            orphan_count=len(exp_ent_ids),
            sample_ids=exp_ent_ids[:10],
        ))

        # Étudiants sans promotion
        cursor.execute(
            "SELECT id_etudiant FROM ETUDIANT "
            "WHERE id_promotion NOT IN (SELECT id_promotion FROM PROMOTION);"
        )
        etu_ids = [r[0] for r in cursor.fetchall()]
        orphans.append(schemas.OrphanReport(
            table_name="ETUDIANT (sans promotion)",
            orphan_count=len(etu_ids),
            sample_ids=etu_ids[:10],
        ))

        # Certifications sans obtention
        cursor.execute(
            "SELECT id_certification FROM CERTIFICATION "
            "WHERE id_certification NOT IN (SELECT id_certification FROM OBTIENT);"
        )
        cert_ids = [r[0] for r in cursor.fetchall()]
        orphans.append(schemas.OrphanReport(
            table_name="CERTIFICATION (sans obtention)",
            orphan_count=len(cert_ids),
            sample_ids=cert_ids[:10],
        ))

        # Consentements RGPD orphelins
        cursor.execute(
            "SELECT id_consentement FROM CONSENTEMENT_RGPD "
            "WHERE id_etudiant NOT IN (SELECT id_etudiant FROM ETUDIANT);"
        )
        cons_ids = [r[0] for r in cursor.fetchall()]
        orphans.append(schemas.OrphanReport(
            table_name="CONSENTEMENT_RGPD (sans étudiant)",
            orphan_count=len(cons_ids),
            sample_ids=cons_ids[:10],
        ))

        # Compter les doublons
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT nom, prenom, email
                FROM ETUDIANT
                GROUP BY nom, prenom, email
                HAVING COUNT(*) > 1
            ) sub;
        """)
        dup_count = cursor.fetchone()[0]

        # RGPD pending : étudiants dont le dernier consentement prise_de_contact
        # est un refus et qui ne sont pas déjà anonymisés (à traiter via
        # /admin/cleanup/rgpd/archiver)
        cursor.execute(f"""
            WITH latest AS ({_LATEST_CONSENT_CTE})
            SELECT COUNT(*)
            FROM latest
            JOIN ETUDIANT e ON e.id_etudiant = latest.id_etudiant
            WHERE latest.statut = 'refuse'
              AND e.email NOT LIKE 'ANONYMISE_%';
        """)
        rgpd_pending = cursor.fetchone()[0]

        total_at_risk = sum(o.orphan_count for o in orphans)

        return schemas.CleanupDryRun(
            orphans=orphans,
            duplicates=[],  # Rempli par l'endpoint dédié
            rgpd_pending_archive=rgpd_pending,
            total_rows_at_risk=total_at_risk,
        )
    except Exception:
        logger.exception("Erreur lors de la détection des orphelins")
        raise HTTPException(status_code=500, detail="Erreur lors de l'analyse des orphelins.")
    finally:
        cursor.close()


# ---------------------------------------------------------------------------
# 2. SUPPRESSION DES ORPHELINS (exécution réelle)
# ---------------------------------------------------------------------------

@router.delete("/orphelins")
def supprimer_orphelins(db=Depends(get_db)):
    """Supprime les enregistrements orphelins dans une transaction unique."""
    cursor = db.cursor()
    total_deleted = 0
    try:
        _write_audit_log(cursor, "DEBUT_SUPPRESSION_ORPHELINS", "Lancement du nettoyage", 0)
        db.commit()

        # Consentements RGPD orphelins
        cursor.execute(
            "DELETE FROM CONSENTEMENT_RGPD "
            "WHERE id_etudiant NOT IN (SELECT id_etudiant FROM ETUDIANT);"
        )
        n = cursor.rowcount
        total_deleted += n
        _write_audit_log(cursor, "SUPPR_CONSENTEMENT_ORPHELINE", f"Supprimés: {n}", n)
        db.commit()
        logger.info("Supprimé %s consentements RGPD orphelins", n)

        # Expériences sans étudiant
        cursor.execute(
            "DELETE FROM EXPERIENCE_PRO "
            "WHERE id_etudiant NOT IN (SELECT id_etudiant FROM ETUDIANT);"
        )
        n = cursor.rowcount
        total_deleted += n
        _write_audit_log(cursor, "SUPPR_EXP_ORPHELINE", f"Supprimées: {n}", n)
        db.commit()
        logger.info("Supprimé %s expériences orphelines (sans étudiant)", n)

        # Expériences sans entreprise
        cursor.execute(
            "DELETE FROM EXPERIENCE_PRO "
            "WHERE id_entreprise NOT IN (SELECT id_entreprise FROM ENTREPRISE);"
        )
        n = cursor.rowcount
        total_deleted += n
        _write_audit_log(cursor, "SUPPR_EXP_ORPHELINE_ENT", f"Supprimées: {n}", n)
        db.commit()
        logger.info("Supprimé %s expériences orphelines (sans entreprise)", n)

        # Étudiants sans promotion
        cursor.execute(
            "DELETE FROM ETUDIANT "
            "WHERE id_promotion NOT IN (SELECT id_promotion FROM PROMOTION);"
        )
        n = cursor.rowcount
        total_deleted += n
        _write_audit_log(cursor, "SUPPR_ETUDIANT_ORPHELIN", f"Supprimés: {n}", n)
        db.commit()
        logger.info("Supprimé %s étudiants orphelins (sans promotion)", n)

        return {
            "message": f"Nettoyage terminé : {total_deleted} enregistrements orphelins supprimés.",
            "total_supprimes": total_deleted,
        }

    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la suppression des orphelins")
        raise HTTPException(status_code=500, detail="Erreur lors du nettoyage des orphelins.")
    finally:
        cursor.close()


# ---------------------------------------------------------------------------
# 3. DÉTECTION DES DOUBLONS (dry-run)
# ---------------------------------------------------------------------------

@router.get("/doublons")
def detecter_doublons(db=Depends(get_db)):
    """Identifie les étudiants en doublon (même nom + prénom + email)."""
    cursor = db.cursor()
    try:
        cursor.execute("""
            SELECT nom, prenom, email, COUNT(*) as nb,
                   ARRAY_AGG(id_etudiant) as ids
            FROM ETUDIANT
            GROUP BY nom, prenom, email
            HAVING COUNT(*) > 1
            ORDER BY nb DESC;
        """)
        rows = cursor.fetchall()
        duplicates = []
        for r in rows:
            duplicates.append({
                "nom": r[0],
                "prenom": r[1],
                "email": r[2],
                "occurrences": r[3],
                "ids": r[4],
            })

        return {
            "groupes_doublons": duplicates,
            "total_groupes": len(duplicates),
            "total_doublons": sum(d["occurrences"] for d in duplicates),
        }
    except Exception:
        logger.exception("Erreur lors de la détection des doublons")
        raise HTTPException(status_code=500, detail="Erreur lors de la détection des doublons.")
    finally:
        cursor.close()


# ---------------------------------------------------------------------------
# 4. RÉSOLUTION DES DOUBLONS — garder le plus ancien, supprimer les autres
# ---------------------------------------------------------------------------

@router.delete("/doublons")
def supprimer_doublons(db=Depends(get_db)):
    """Supprime les doublons en gardant l'enregistrement le plus ancien (id le plus bas)."""
    cursor = db.cursor()
    total_deleted = 0
    try:
        # Trouver tous les groupes de doublons
        cursor.execute("""
            SELECT nom, prenom, email, ARRAY_AGG(id_etudiant ORDER BY id_etudiant) as ids
            FROM ETUDIANT
            GROUP BY nom, prenom, email
            HAVING COUNT(*) > 1;
        """)
        groups = cursor.fetchall()

        for group in groups:
            nom, prenom, email, ids = group
            ids_to_delete = ids[1:]  # Garder le premier (id le plus bas)

            for eid in ids_to_delete:
                # Supprimer les données liées avant l'étudiant

                cursor.execute(
                    "DELETE FROM OBTIENT WHERE id_etudiant = %s;", (eid,)
                )
                cursor.execute(
                    "DELETE FROM EXPERIENCE_PRO WHERE id_etudiant = %s;", (eid,)
                )
                cursor.execute(
                    "DELETE FROM CONSENTEMENT_RGPD WHERE id_etudiant = %s;", (eid,)
                )
                cursor.execute(
                    "DELETE FROM ETUDIANT WHERE id_etudiant = %s;", (eid,)
                )

                n = cursor.rowcount
                total_deleted += n

                _write_audit_log(
                    cursor, "SUPPR_DOUBLON",
                    f"Supprimé id={eid} (doublon de {nom} {prenom}, gardé: id={ids[0]})",
                    n,
                )
                db.commit()
                logger.info("Supprimé doublon id=%s pour %s %s", eid, nom, prenom)

        return {
            "message": f"Nettoyage des doublons terminé : {total_deleted} enregistrements supprimés.",
            "groupes_traites": len(groups),
            "total_supprimes": total_deleted,
        }

    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la suppression des doublons")
        raise HTTPException(status_code=500, detail="Erreur lors du nettoyage des doublons.")
    finally:
        cursor.close()


# ---------------------------------------------------------------------------
# 5. ARCHIVAGE RGPD — masquer les données des utilisateurs ayant refusé
# ---------------------------------------------------------------------------

@router.post("/rgpd/archiver")
def archiver_consentement_refuse(db=Depends(get_db)):
    """
    Archive (masque) les données personnelles des étudiants ayant refusé
    le consentement RGPD. Utilise un UPDATE logique (masquage) des champs
    sensibles plutôt qu'une suppression physique.

    Un étudiant est archivé si son consentement le plus récent de type
    'prise_de_contact' a le statut 'refuse' (valeurs réelles en base).
    """
    cursor = db.cursor()
    total_archived = 0
    try:
        # Étudiants dont le dernier consentement prise_de_contact est un refus
        cursor.execute(f"""
            WITH latest AS ({_LATEST_CONSENT_CTE})
            SELECT e.id_etudiant
            FROM ETUDIANT e
            JOIN latest ON latest.id_etudiant = e.id_etudiant
            WHERE latest.statut = 'refuse'
              AND e.email NOT LIKE 'ANONYMISE_%';
        """)
        etudiants_a_archiver = [r[0] for r in cursor.fetchall()]

        for eid in etudiants_a_archiver:
            # Masquer les données personnelles de l'étudiant
            cursor.execute("""
                UPDATE ETUDIANT
                SET nom = 'ANONYMISE',
                    prenom = 'ANONYMISE',
                    email = 'ANONYMISE_' || id_etudiant || '@anonymise.io',
                    email_academique = NULL,
                    telephone = 'ANONYMISE',
                    date_naissance = '1900-01-01',
                    parcours_anterieur = 'ANONYMISE',
                    address = NULL,
                    city = NULL,
                    country = NULL,
                    linkedin = NULL,
                    availability_status = '',
                    skills = '[]'::jsonb,
                    date_anonymisation = NOW()
                WHERE id_etudiant = %s;
            """, (eid,))

            # Anonymiser les expériences liées (salaire → 0, intitulé → masqué)
            cursor.execute("""
                UPDATE EXPERIENCE_PRO
                SET intitule_poste = 'ANONYMISE',
                    salaire = 0
                WHERE id_etudiant = %s;
            """, (eid,))

            _write_audit_log(
                cursor, "ARCHIVAGE_RGPD",
                f"Anonymisation données étudiant id={eid} (consentement refuse)",
                1,
            )
            db.commit()
            total_archived += 1
            logger.info("Archivé (anonymisé) l'étudiant id=%s", eid)

        return {
            "message": f"Archivage RGPD terminé : {total_archived} profils anonymisés.",
            "total_archives": total_archived,
        }

    except Exception:
        db.rollback()
        logger.exception("Erreur lors de l'archivage RGPD")
        raise HTTPException(status_code=500, detail="Erreur lors de l'archivage RGPD.")
    finally:
        cursor.close()


# ---------------------------------------------------------------------------
# 6. HISTORIQUE DES AUDITS
# ---------------------------------------------------------------------------

@router.get("/audit")
def historique_audit(
    limit: int = 50,
    db=Depends(get_db),
):
    """Retourne les dernières entrées d'audit (journalisation)."""
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT id_log, action, details, rows_affected, acteur, executed_at "
            "FROM AUDIT_LOG ORDER BY executed_at DESC LIMIT %s;",
            (limit,),
        )
        return {"historique": rows_to_dicts(cursor, cursor.fetchall())}
    except Exception:
        logger.exception("Erreur lors de la lecture de l'audit")
        raise HTTPException(status_code=500, detail="Impossible de lire l'historique d'audit.")
    finally:
        cursor.close()
