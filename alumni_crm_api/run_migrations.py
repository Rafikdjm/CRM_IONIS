#!/usr/bin/env python3
"""
run_migrations.py — Exécuteur de migrations SQL pour Alumni CRM
================================================================

Utilisation :
    python run_migrations.py

Le script lit tous les fichiers .sql du dossier migrations/ triés par
préfixe numérique (001_, 002_, …), vérifie lesquels ont déjà été appliqués
grâce à la table schema_migrations, et n'exécute que ceux qui manquent.

Créer une nouvelle migration :
    1. Créer un fichier 007_nom_descriptif.sql dans alumni_crm_api/migrations/
    2. Écrire le SQL (ALTER TABLE, CREATE TABLE, etc.) dans le fichier
    3. Lancer : python run_migrations.py
    4. Le script détecte le nouveau fichier et l'applique automatiquement

Convention de nommage : NNN_description_courte.sql (ex: 007_add_roles.sql)
Le numéro doit être unique et croissant.
"""

import os
import re
import sys
from datetime import datetime, timezone

import pg8000.dbapi


# ── Chargement de la configuration ──────────────────────
def load_env(path: str = ".env") -> dict:
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def get_connection(env: dict) -> pg8000.dbapi.Connection:
    return pg8000.dbapi.connect(
        host=env.get("DB_HOST", "localhost"),
        database=env.get("DB_NAME", "alumni_crm"),
        user=env.get("DB_USER", "postgres"),
        password=env.get("DB_PASSWORD", ""),
        port=int(env.get("DB_PORT", 5432)),
    )


# ── Table schema_migrations ─────────────────────────────
def ensure_tracking_table(conn) -> None:
    """Crée la table schema_migrations si elle n'existe pas."""
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            nom_fichier VARCHAR(255) PRIMARY KEY,
            date_execution TIMESTAMP NOT NULL DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()


def get_applied(conn) -> set:
    """Retourne l'ensemble des noms de fichiers déjà appliqués."""
    cur = conn.cursor()
    cur.execute("SELECT nom_fichier FROM schema_migrations ORDER BY nom_fichier;")
    applied = {row[0] for row in cur.fetchall()}
    cur.close()
    return applied


def mark_applied(conn, filename: str) -> None:
    """Enregistre un fichier comme appliqué."""
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO schema_migrations (nom_fichier, date_execution) VALUES (%s, %s);",
        (filename, datetime.now(timezone.utc)),
    )
    conn.commit()
    cur.close()


# ── Découverte et tri des fichiers ──────────────────────
MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")


def discover_migrations() -> list[str]:
    """Liste les fichiers .sql dans migrations/ triés par préfixe numérique."""
    if not os.path.isdir(MIGRATIONS_DIR):
        print(f"ERREUR : dossier migrations/ introuvable ({MIGRATIONS_DIR})")
        sys.exit(1)

    files = []
    for f in os.listdir(MIGRATIONS_DIR):
        if f.endswith(".sql"):
            files.append(f)

    def sort_key(name: str) -> int:
        match = re.match(r"^(\d+)", name)
        return int(match.group(1)) if match else 999999

    files.sort(key=sort_key)
    return files


# ── Exécution ───────────────────────────────────────────
def run_migration(conn, filepath: str, filename: str) -> bool:
    """Exécute un fichier SQL. Retourne True si succès, False si erreur."""
    with open(filepath, "r", encoding="utf-8") as f:
        sql = f.read().strip()

    if not sql:
        print(f"  [INFO] Fichier vide, ignore.")
        return True

    cur = conn.cursor()
    try:
        cur.execute(sql)
        conn.commit()
        print(f"  [OK] Appliquee avec succes.")
        return True
    except Exception as e:
        conn.rollback()
        print(f"  [ERREUR] {e}")
        return False
    finally:
        cur.close()


# ── Point d'entrée ──────────────────────────────────────
def main():
    print("=" * 60)
    print(" Alumni CRM — Exécuteur de migrations SQL")
    print("=" * 60)

    # Chargement config
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        print(f"ERREUR : fichier .env introuvable ({env_path})")
        sys.exit(1)

    env = load_env(env_path)
    conn = get_connection(env)

    # Créer la table de tracking
    ensure_tracking_table(conn)

    # Découvrir les migrations
    migrations = discover_migrations()
    if not migrations:
        print("\nAucun fichier .sql trouvé dans migrations/.")
        conn.close()
        return

    # Charger l'état déjà appliqué
    applied = get_applied(conn)

    print(f"\nFichiers trouvés : {len(migrations)}")
    print(f"Déjà appliqués  : {len(applied & set(migrations))}")
    print(f"À appliquer     : {len(set(migrations) - applied)}")
    print()

    # Parcourir chaque migration
    newly_applied = 0
    skipped = 0
    errors = 0

    for filename in migrations:
        filepath = os.path.join(MIGRATIONS_DIR, filename)

        if filename in applied:
            print(f"[SAUTÉ]  {filename} (déjà appliquée le {filename})")
            skipped += 1
            continue

        print(f"[APPLY]  {filename} ...")
        success = run_migration(conn, filepath, filename)

        if success:
            mark_applied(conn, filename)
            newly_applied += 1
        else:
            errors += 1
            print(f"\n  >>> ARRÊT : migration {filename} en échec.")
            print(f"  >>> Corrigez le fichier et relancez python run_migrations.py")
            break

    # Résumé
    print("\n" + "=" * 60)
    print(" RÉSUMÉ")
    print("=" * 60)
    print(f"  Nouvellement appliquées : {newly_applied}")
    print(f"  Déjà à jour (sautées)   : {skipped}")
    print(f"  Erreurs                 : {errors}")

    if errors == 0:
        print(f"\n  [OK] Aucune erreur. La base est a jour.")
    else:
        print(f"\n  [ERREUR] {errors} erreur(s). Corrigez et relancez.")

    print("=" * 60)
    conn.close()
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
