import sqlite3

def init_db():
    """Initialise la base de données et crée les tables si elles n'existent pas."""
    conn = sqlite3.connect("ergo.db")
    cursor = conn.cursor()

    # Table Objectifs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS objectifs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL
    )
    """)

    # Table Activités
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        description TEXT,
        lien TEXT,
        objectif_id INTEGER NOT NULL,
        FOREIGN KEY(objectif_id) REFERENCES objectifs(id)
    )
    """)

    conn.commit()
    conn.close()

def fetch_objectifs():
    """Récupère tous les objectifs dans la base de données."""
    conn = sqlite3.connect("ergo.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nom FROM objectifs")
    objectifs = cursor.fetchall()
    conn.close()
    return objectifs

def fetch_activites_by_objectif(objectif_id):
    """Récupère toutes les activités associées à un objectif donné."""
    conn = sqlite3.connect("ergo.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nom, description, lien, objectif_id, id FROM activites WHERE objectif_id = ?", (objectif_id,))
    activites = cursor.fetchall()
    conn.close()
    return activites

def add_objectif(nom):
    """Ajoute un nouvel objectif dans la base de données."""
    conn = sqlite3.connect("ergo.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO objectifs (nom) VALUES (?)", (nom,))
    conn.commit()
    conn.close()

def add_activite(nom, description, lien, image, objectif_id):
    """Ajoute une nouvelle activité dans la base de données."""
    conn = sqlite3.connect("ergo.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO activites (nom, description, lien, objectif_id) VALUES (?, ?, ?, ?)
    """, (nom, description, lien, objectif_id))
    conn.commit()
    conn.close()

def update_activite(activite_id, nom, description, lien):
    """Met à jour une activité existante dans la base de données."""
    conn = sqlite3.connect("ergo.db")
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE activites
    SET nom = ?, description = ?, lien = ?
    WHERE id = ?
    """, (nom, description, lien, activite_id))
    conn.commit()
    conn.close()
