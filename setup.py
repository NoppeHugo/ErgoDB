from setuptools import setup

APP = ['main.py']
DATA_FILES = [
    ('backups', ['backups/gestion_activites_20241128160050.db']),
    ('images', []),  # Ajoutez ici les fichiers d'images si nécessaire
    ('', ['gestion_activites.db', 'icon.png'])
]
OPTIONS = {
    'argv_emulation': True,
    'packages': ['tkinterdnd2', 'PIL'],
    'includes': ['tkinter', 'sqlite3', 'shutil', 'datetime', 'os', 'webbrowser'],
    'iconfile': 'icon.png',  # Chemin vers l'icône de votre application
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)