import sqlite3

def init_db():
    """Initialise la base de données avec les tables si elles n'existent pas."""
    with sqlite3.connect('gestion_activites.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS objectifs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nom TEXT NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS activites (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nom TEXT NOT NULL,
                            description TEXT,
                            lien TEXT,
                            objectif_id INTEGER,
                            FOREIGN KEY (objectif_id) REFERENCES objectifs(id))''')


def fetch_objectifs():
    """Récupère tous les objectifs."""
    with sqlite3.connect('gestion_activites.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom FROM objectifs")
        return cursor.fetchall()


def add_objectif(nom):
    """Ajoute un nouvel objectif."""
    with sqlite3.connect('gestion_activites.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO objectifs (nom) VALUES (?)", (nom,))
        conn.commit()


def delete_objectif(objectif_id):
    """Supprime un objectif et toutes ses activités associées."""
    with sqlite3.connect('gestion_activites.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activites WHERE objectif_id = ?", (objectif_id,))
        cursor.execute("DELETE FROM objectifs WHERE id = ?", (objectif_id,))
        conn.commit()


def fetch_activites_by_objectif(objectif_id):
    """Récupère toutes les activités associées à un objectif donné."""
    with sqlite3.connect('gestion_activites.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom FROM activites WHERE objectif_id = ?", (objectif_id,))
        return cursor.fetchall()


def add_activite(nom, description, lien, objectif_id):
    """Ajoute une nouvelle activité."""
    with sqlite3.connect('gestion_activites.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO activites (nom, description, lien, objectif_id) VALUES (?, ?, ?, ?)",
                       (nom, description, lien, objectif_id))
        conn.commit()


def update_activite(activite_id, nom, description, lien):
    """Met à jour une activité existante."""
    with sqlite3.connect('gestion_activites.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE activites SET nom = ?, description = ?, lien = ? WHERE id = ?",
                       (nom, description, lien, activite_id))
        conn.commit()


def delete_activite_by_id(activite_id):
    """Supprime une activité par son ID."""
    with sqlite3.connect('gestion_activites.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activites WHERE id = ?", (activite_id,))
        conn.commit()


def fetch_activity_by_id(activite_id):
    """Récupère les détails d'une activité par son ID."""
    with sqlite3.connect('gestion_activites.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom, description, lien FROM activites WHERE id = ?", (activite_id,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'nom': row[1],
                'description': row[2],
                'lien': row[3],
            }
        return None
