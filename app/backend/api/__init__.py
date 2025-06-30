from flask import Flask ,Blueprint
from .views import  init_auth_routes ,init_user_routes
from ..db import initialize_database 
from typing import Callable ,List,Tuple
from app.backend.config import CONFIG  ,AppConfig
from flask_cors import CORS

version_no = '1.0'

generate_prefix:Callable = lambda x: f"/api/{version_no}/{x}"

def register_blueprints(app: Flask, blueprints: List[Tuple[Blueprint, str]]) -> Flask:
    """
    Registers a list of Flask blueprints with dynamically generated URL prefixes.

    Args:
        app (Flask): The Flask application instance to which the blueprints will be registered.
        blueprints (List[Tuple[Blueprint, str]]): 
            A list of tuples where each tuple contains:
            - A Flask Blueprint instance
            - A string identifier used to generate the URL prefix via `generate_prefix(endpoint)`

    Returns:
        Flask: The same Flask application instance, with the blueprints registered.
    """

    for bp , endpoint in blueprints:
        app.register_blueprint(bp ,url_prefix = generate_prefix(endpoint))

    return app 

def init_app(config:AppConfig=CONFIG):
    """
    Initialize and configure the Flask application.

    Args:
        config (AppConfig, optional): Configuration object for the application.
            Defaults to the global CONFIG.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)
    CORS(app)

    db_url = initialize_database(config)
    
    auth_bp = init_auth_routes(config)
    user_bp = init_user_routes(config)

    bp_list = [
        (auth_bp,'auth'),
        (user_bp,'user')
    ]

    app = register_blueprints(
        app=app ,
        blueprints=bp_list
    )
    app.config['db_url'] = db_url 

    return app

