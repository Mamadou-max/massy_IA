import os
import sys
from pathlib import Path
from flask_migrate import upgrade, init, migrate

# Ajouter le dossier parent au PYTHONPATH pour que 'backend' soit visible
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# Maintenant les imports absolus depuis 'backend' fonctionnent
from backend.app import create_app
from backend.extensions import db
from backend.config import config

# Déterminer l'environnement Flask
env = os.environ.get('FLASK_ENV', 'default')
flask_config = config.get(env, config['default'])

# Créer l'application Flask
app = create_app(flask_config)

# Chemin du projet et dossier migrations
project_root = current_dir
migrations_dir = project_root / "migrations"

with app.app_context():
    # --- Création de la base SQLite si elle n'existe pas ---
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith("sqlite:///"):
        db_path = db_uri.replace("sqlite:///", "")
        db_folder = Path(db_path).parent
        if not Path(db_path).exists():
            db_folder.mkdir(parents=True, exist_ok=True)
            db.create_all()
            print(f"[INFO] Base de données créée : {db_path}")
        else:
            print(f"[INFO] Base de données existante : {db_path}")

    # --- Initialisation du dossier migrations si nécessaire ---
    if not migrations_dir.exists() or not any(migrations_dir.iterdir()):
        print("[INFO] Initialisation du dossier migrations...")
        init()

    # --- Génération des migrations ---
    try:
        print("[INFO] Génération des migrations...")
        migrate(message="Auto migration")
    except Exception:
        print("[INFO] Pas de modifications détectées pour les migrations.")

    # --- Application des migrations ---
    try:
        print("[INFO] Application des migrations...")
        upgrade()
        print("[INFO] Migrations appliquées avec succès !")
    except Exception as e:
        print(f"[WARN] Erreur lors de l'application des migrations : {e}")

if __name__ == '__main__':
    debug_mode = getattr(flask_config, 'DEBUG', False)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
