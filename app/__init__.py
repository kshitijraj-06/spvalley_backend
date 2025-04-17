from flask import Flask
from .maintenance import maintenance
from .profile import profile
from .config import Config
from .firebase import initialize_firebase, generate_custom_token, get_id_token
from .auth_routes import auth_bp
from .users_auth import users_auth


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Firebase
    initialize_firebase()
    get_id_token(
        custom_token=generate_custom_token(email="test3@example.com"),
    )

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(users_auth)
    app.register_blueprint(profile)
    app.register_blueprint(maintenance)

    return app
