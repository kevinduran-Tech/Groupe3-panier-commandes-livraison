"""Accès aux données : connexion SQLite, transactions atomiques, initialisation du schéma."""
import os
import sqlite3
from contextlib import contextmanager

from flask import current_app, g

SCHEMA = os.path.join(os.path.dirname(__file__), "schema.sql")


def connecter(chemin):
    """Ouvre une connexion. isolation_level=None : les transactions sont gérées explicitement."""
    conn = sqlite3.connect(chemin, timeout=10, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


@contextmanager
def transaction(conn):
    """Transaction atomique. BEGIN IMMEDIATE prend le verrou d'écriture dès le début :
    deux opérations simultanées sur le stock sont donc traitées l'une après l'autre."""
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise


def init_schema(conn):
    with open(SCHEMA, encoding="utf-8") as f:
        conn.executescript(f.read())


def get_db():
    """Une connexion par requête HTTP, fermée automatiquement à la fin."""
    if "db" not in g:
        g.db = connecter(current_app.config["DATABASE"])
    return g.db


def fermer_db(_exc=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()
