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
        cursor.execute("SELECT * FROM objectifs")
        return cursor.fetchall()

def fetch_activites_by_objectif(objectif_id):
    """Récupère les activités liées à un objectif donné."""
    with sqlite3.connect('gestion_activites.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM activites WHERE objectif_id=?", (objectif_id,))
        return cursor.fetchall()

def add_objectif(nom):
    """Ajoute un nouvel objectif."""
    with sqlite3.connect('gestion_activites.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO objectifs (nom) VALUES (?)", (nom,))
        conn.commit()

def add_activite(nom, description, lien, objectif_id):
    """Ajoute une nouvelle activité."""
    with sqlite3.connect('gestion_activites.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO activites (nom, description, lien, objectif_id) VALUES (?, ?, ?, ?)", 
                       (nom, description, lien, objectif_id))
        conn.commit()

def update_activite(activite_id, new_nom, new_desc, new_link):
    """Met à jour une activité."""
    with sqlite3.connect('gestion_activites.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE activites SET nom = ?, description = ?, lien = ? WHERE id = ?", 
                       (new_nom, new_desc, new_link, activite_id))
        conn.commit()

def get_db_connection():
    conn = sqlite3.connect('gestion_activites.db')
    conn.row_factory = sqlite3.Row
    return conn

def delete_activite_by_id(activite_id):
    """Supprime une activité."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activites WHERE id=?", (activite_id,))
        conn.commit()

def delete_objectif(objectif_id):
    """Supprime un objectif ainsi que ses activités associées."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activites WHERE objectif_id=?", (objectif_id,))
        cursor.execute("DELETE FROM objectifs WHERE id=?", (objectif_id,))
        conn.commit()

def fetch_activity_by_id(activite_id):
    """Récupère les détails d'une activité par son ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nom, description, lien FROM activites WHERE id=?", (activite_id,))
    activity = cursor.fetchone()
    conn.close()
    return activity
