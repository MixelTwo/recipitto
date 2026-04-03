from bafser import doc_api, protected_route
from flask import Blueprint

from data.user import User, UserDict

bp = Blueprint("user", __name__)


@bp.route("/api/user")
@doc_api(res=UserDict, desc="Get current user")
@protected_route()
def user():
    """Retrieve the currently authenticated user's profile.

    Requires authentication.

    Returns:
        The user object of the authenticated user.
    """
    return User.current.get_dict()
