from flask import Flask 
from .views import views
from .auth import auth
from .models import db
from pathlib import Path
from secrets import token_hex

current_folder = Path(__file__).parent.absolute()

# Configs
configs_folder = current_folder / 'configs' 
secret_configs_path = configs_folder / 'secret_configs.py'
db_configs_path = configs_folder / 'database_configs.py'

# Database
database_path = current_folder / 'database' / 'database.db'

def create_app():
    app = Flask(__name__)
    
    ensure_config_presence()
    app.config.from_pyfile(secret_configs_path)

    ensure_database_config_presence()
    app.config.from_pyfile(db_configs_path)

    create_database(app)

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app

# Secret config
def ensure_config_presence():
    if secret_configs_path.exists():
        pass 
    else:
        file_content = generate_secret_configs()

        with open(secret_configs_path, 'w') as file_config:
            file_config.write(file_content)
        
        print("Config file has been auto-generated.")
    
def generate_secret_configs():
    secret_token_hex = token_hex()
    secret_key = f"SECRET_KEY='{str(secret_token_hex)}'"
    content = f"{secret_key}\n"

    return content  
    

# Database 
def ensure_database_config_presence():
    if database_path.exists():
       pass
    else:
        file_content = generate_database_config()

        with open(db_configs_path, 'w') as file_config:
            file_config.write(file_content)

        print("Database config file has been auto-generated.")

def generate_database_config():
    str_database_path = str(database_path).replace("\\", "\\\\")
    content = f"SQLALCHEMY_DATABASE_URI='sqlite:///{str_database_path}'"
    
    return content

def create_database(app):
    db.init_app(app)

    if database_path.exists():
        print("Database exists.")
    else:
        with app.app_context():
            print("Database does not exists. Creating new database.")
            db.create_all()
            print("Created a new database.")
