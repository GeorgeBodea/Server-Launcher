from flask import Flask
from .views import ViewController  # Assuming ViewController contains the views Blueprint
from .auth import AuthController  # Assuming AuthController contains the auth Blueprint
from .models import db, User
from pathlib import Path
from secrets import token_hex
from flask_login import LoginManager

class AppSetup:
    def __init__(self):
        self.current_folder = Path(__file__).parent.absolute()
        self.configs_folder = self.current_folder / 'configs'
        self.secret_configs_path = self.configs_folder / 'secret_configs.py'
        self.db_configs_path = self.configs_folder / 'database_configs.py'
        self.database_path = self.current_folder / 'database' / 'database.db'

    def create_app(self):
        app = Flask(__name__)
        app.config['SECRET_KEY'] = self.generate_secret_configs()
        self.ensure_database_config_presence()
        app.config.from_pyfile(self.db_configs_path)
        self.create_database(app)
        self.handle_login(app)
        app.register_blueprint(ViewController.views, url_prefix='/')
        app.register_blueprint(AuthController.auth, url_prefix='/')
        return app

    def handle_login(self, app):
        login_manager = LoginManager()
        login_manager.login_view = 'auth.login'
        login_manager.init_app(app)

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

    def generate_secret_configs(self):
        secret_token_hex = token_hex()
        secret_key = f"SECRET_KEY='{str(secret_token_hex)}'"
        # Optionally, you can save this content to a file if needed
        return secret_key  

    def ensure_database_config_presence(self):
        if not self.database_path.exists():
            file_content = self.generate_database_config()
            with open(self.db_configs_path, 'w') as file_config:
                file_config.write(file_content)
            print("Database config file has been auto-generated.")

    def generate_database_config(self):
        str_database_path = str(self.database_path).replace("\\", "\\\\")
        content = f"SQLALCHEMY_DATABASE_URI='sqlite:///{str_database_path}'"
        return content

    def create_database(self, app):
        db.init_app(app)
        if not self.database_path.exists():
            with app.app_context():
                print("Database does not exist. Creating a new database.")
                db.create_all()
                print("Created a new database.")
        else:
            print("Database exists.")
