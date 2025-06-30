
from .auth import init_auth_routes

from flask import Blueprint

from .education import EducationView
from .work import WorkView
from .user_optional import OptionalView
from .profile import ProfileView

def init_user_routes(config):

    user_bp = Blueprint('user',__name__)

    user_bp.add_url_rule(
        '/education',
        view_func=EducationView(config).as_view("education"),
        methods=['POST','GET','PUT','DELETE']
    )
    user_bp.add_url_rule(
        '/work',
        view_func=WorkView(config).as_view('work'),
        methods=['GET','POST','DELETE','PUT']
    )

    user_bp.add_url_rule(
        '/optional',
        view_func=OptionalView(config).as_view('optional'),
        methods=['GET','POST','DELETE','PUT']
    )
    user_bp.add_url_rule(
        '/profile',
        view_func=ProfileView(config).as_view('profile'),
        methods=['GET']
    )
    return user_bp