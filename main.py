from app1 import app
from flask_migrate import Migrate

# Configurar Flask-Migrate
migrate = Migrate() 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5053, debug=False)
    # Trigger rebuild - do not remove
