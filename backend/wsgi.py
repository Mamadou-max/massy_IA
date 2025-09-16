from backend.app import create_app
from backend.config import config
import os

# Déterminer l'environnement Flask
env = os.environ.get('FLASK_ENV', 'default')
flask_config = config.get(env, config['default'])

# Créer l'application Flask
app = create_app(flask_config)
