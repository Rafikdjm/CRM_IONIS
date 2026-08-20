"""
Gestion de la connexion à PostgreSQL.

Corrections par rapport à la version initiale :
1. Plus d'identifiants en dur (voir config.py).
2. Pool de connexions au lieu d'ouvrir/fermer une connexion à chaque requête
   HTTP : moins coûteux, surtout dès que plusieurs utilisateurs (admin +
   alumni) interrogent l'API en même temps.
3. Erreurs de connexion loggées proprement plutôt qu'affichées avec des
   `print()`.
"""
import logging
import queue
from contextlib import contextmanager
from typing import Iterator

import pg8000.dbapi

from config import settings

logger = logging.getLogger(__name__)


class ConnectionPool:
    """Pool de connexions pg8000 très simple, basé sur une file thread-safe.

    Pour un projet plus exigeant en charge, on privilégierait un vrai pool
    (SQLAlchemy `QueuePool`, ou psycopg2 `ThreadedConnectionPool`) qui gère
    en plus la détection des connexions mortes. Ici, l'objectif est déjà de
    ne plus ouvrir une connexion neuve à chaque requête HTTP.
    """

    def __init__(self, size: int) -> None:
        self._pool: "queue.Queue[pg8000.dbapi.Connection]" = queue.Queue(maxsize=size)
        for _ in range(size):
            self._pool.put(self._create_connection())

    def _create_connection(self) -> pg8000.dbapi.Connection:
        try:
            return pg8000.dbapi.connect(
                host=settings.db_host,
                database=settings.db_name,
                user=settings.db_user,
                password=settings.db_password,
                port=settings.db_port,
            )
        except Exception:
            logger.exception("Impossible de joindre PostgreSQL.")
            raise

    def acquire(self) -> pg8000.dbapi.Connection:
        return self._pool.get()

    def release(self, connection: pg8000.dbapi.Connection) -> None:
        # On s'assure qu'aucune transaction ouverte ne "fuit" vers le prochain
        # utilisateur de cette connexion.
        try:
            connection.rollback()
        except Exception:
            logger.exception("Erreur lors du nettoyage d'une connexion avant remise en pool.")
        self._pool.put(connection)


pool = ConnectionPool(settings.pool_size)


@contextmanager
def get_db_connection() -> Iterator[pg8000.dbapi.Connection]:
    connection = pool.acquire()
    try:
        yield connection
    finally:
        pool.release(connection)


def get_db() -> Iterator[pg8000.dbapi.Connection]:
    """Dépendance FastAPI : fournit une connexion issue du pool le temps de la requête."""
    with get_db_connection() as connection:
        yield connection
