
from flask import Blueprint
from .login import LoginView
from .register import RegisterView
from .token import TokenView

def init_auth_routes(config):
    auth_bp = Blueprint('auth', __name__)

    auth_bp.add_url_rule(
        '/login',
        view_func=LoginView(config).as_view('login'),
        methods=['POST']
    )
    
    auth_bp.add_url_rule(
        '/register',
        view_func=RegisterView(config).as_view('register'),
        methods=['POST']
    )
    
    auth_bp.add_url_rule(
        '/token',
        view_func=TokenView(config).as_view('token'),
        methods=['POST', 'GET', 'DELETE']
    )

    return auth_bp
