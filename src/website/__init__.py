from flask import Flask 
from .views import views
from .auth import auth
from pathlib import Path
from secrets import token_hex

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app

def ensure_config_presence():
    current_folder = Path(__file__).parent.absolute()
    config_abs_path = current_folder / "config.py"

    if config_abs_path.is_file():
        pass 
    else:
        secret_key = token_hex()
        file_content = "SECRET_APP=\'{}\'".format(secret_key)

        with open(config_abs_path, 'w') as file_config:
            file_config.write(file_content)
        
        print("Config file has been auto-generated.")
        