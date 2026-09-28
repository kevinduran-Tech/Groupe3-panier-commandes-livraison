"""Journalisation des opérations sensibles (traçabilité)."""


def journaliser(conn, auteur, action, entite, entite_id=None, detail=""):
    conn.execute(
        "INSERT INTO journal (auteur, action, entite, entite_id, detail) VALUES (?, ?, ?, ?, ?)",
        (auteur, action, entite, entite_id, detail),
    )


def lister(conn, limite=100):
    lignes = conn.execute("SELECT * FROM journal ORDER BY id DESC LIMIT ?", (limite,)).fetchall()
    return [dict(r) for r in lignes]
