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
        cursor.execute('''CREATE TABLE IF NOT EXISTS activite_images (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            activite_id INTEGER,
                            image_path TEXT,
                            FOREIGN KEY (activite_id) REFERENCES activites(id))''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS activite_objectifs (
                            activite_id INTEGER,
                            objectif_id INTEGER,
                            FOREIGN KEY (activite_id) REFERENCES activites(id),
                            FOREIGN KEY (objectif_id) REFERENCES objectifs(id))''')
        conn.commit()

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


def fetch_activites_by_objectifs(objectif_ids):
    """Récupère les activités correspondant à une liste d'objectifs donnés."""
    with sqlite3.connect('gestion_activites.db') as conn:
        cursor = conn.cursor()
        query = '''
            SELECT a.id, a.nom
            FROM activites a
            JOIN activite_objectifs ao ON a.id = ao.activite_id
            WHERE ao.objectif_id IN ({seq})
            GROUP BY a.id, a.nom
            HAVING COUNT(DISTINCT ao.objectif_id) = ?
        '''.format(seq=','.join(['?']*len(objectif_ids)))
        cursor.execute(query, objectif_ids + [len(objectif_ids)])
        return cursor.fetchall()

def add_activite(nom, description, lien, objectif_ids, image_paths):
    """Ajoute une nouvelle activité."""
    with sqlite3.connect('gestion_activites.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO activites (nom, description, lien) VALUES (?, ?, ?)",
            (nom, description, lien)
        )
        activite_id = cursor.lastrowid
        for objectif_id in objectif_ids:
            cursor.execute(
                "INSERT INTO activite_objectifs (activite_id, objectif_id) VALUES (?, ?)",
                (activite_id, objectif_id)
            )
        for image_path in image_paths:
            cursor.execute(
                "INSERT INTO activite_images (activite_id, image_path) VALUES (?, ?)",
                (activite_id, image_path)
            )
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
            cursor.execute("SELECT objectif_id FROM activite_objectifs WHERE activite_id = ?", (activite_id,))
            objectifs = cursor.fetchall()
            cursor.execute("SELECT image_path FROM activite_images WHERE activite_id = ?", (activite_id,))
            images = cursor.fetchall()
            return {
                'id': row[0],
                'nom': row[1],
                'description': row[2],
                'lien': row[3],
                'objectifs': [obj[0] for obj in objectifs],
                'images': [img[0] for img in images]
            }
        return None
    
def fetch_objectif_by_id(objectif_id):
    """Récupère les détails d'un objectif par son ID."""
    with sqlite3.connect('gestion_activites.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom FROM objectifs WHERE id = ?", (objectif_id,))
        row = cursor.fetchone()
        if row:
            return {'id': row[0], 'nom': row[1]}
        return None
    
def update_activity_images(activity_id, new_images):
    """Met à jour les images d'une activité dans la base de données."""
    # Supprimer les images existantes
    delete_images_query = "DELETE FROM activite_images WHERE activite_id = ?"
    insert_image_query = "INSERT INTO activite_images (activite_id, image_path) VALUES (?, ?)"

    with sqlite3.connect('gestion_activites.db') as conn:
        cursor = conn.cursor()
        cursor.execute(delete_images_query, (activity_id,))
        for image_path in new_images:
            cursor.execute(insert_image_query, (activity_id, image_path))
        conn.commit()
        
def update_activity_objectifs(activity_id, new_objectifs):
    """Met à jour les objectifs d'une activité dans la base de données."""
    delete_objectifs_query = "DELETE FROM activite_objectifs WHERE activite_id = ?"
    insert_objectif_query = "INSERT INTO activite_objectifs (activite_id, objectif_id) VALUES (?, ?)"
    
    with sqlite3.connect('gestion_activites.db') as conn:
        cursor = conn.cursor()
        cursor.execute(delete_objectifs_query, (activity_id,))
        for objectif_id in new_objectifs:
            cursor.execute(insert_objectif_query, (activity_id, objectif_id))
        conn.commit()

def fetch_all_activites():
    """Récupère toutes les activités."""
    with sqlite3.connect('gestion_activites.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom FROM activites")
        return cursor.fetchall()