from flask import Flask 
from .views import views
from .auth import auth
from .models import db, User
from pathlib import Path
from secrets import token_hex
from flask_login import LoginManager

current_folder = Path(__file__).parent.absolute()

# Configs paths
configs_folder = current_folder / 'configs' 
secret_configs_path = configs_folder / 'secret_configs.py'
db_configs_path = configs_folder / 'database_configs.py'

# Database paths
database_path = current_folder / 'database' / 'database.db'

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = generate_secret_configs()

    ensure_database_config_presence()
    app.config.from_pyfile(db_configs_path)

    create_database(app)

    handle_login(app)

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app

# Login handler
def handle_login(app):
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

# Secret    
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
