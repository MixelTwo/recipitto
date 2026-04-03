from bafser import JsonObj, create_access_token, doc_api, response_msg, use_db_sess
from flask import Blueprint, jsonify
from flask_jwt_extended import set_access_cookies, unset_jwt_cookies  # pyright: ignore[reportUnknownVariableType]
from sqlalchemy.orm import Session

from data.user import User, UserDict

bp = Blueprint("auth", __name__)


class LoginJson(JsonObj):
    """JSON schema for user login.

    Attributes:
        login: Username or email.
        password: User password.
    """

    login: str
    password: str


@bp.post("/api/auth")
@doc_api(req=LoginJson, res=UserDict, desc="Get auth cookie")
@use_db_sess
def login(db_sess: Session):
    """Authenticate user and set JWT cookie.

    Args:
        db_sess: Database session (injected by @use_db_sess).

    Returns:
        User object and sets an HTTP‑only JWT cookie.

    Raises:
        400 if login or password is incorrect.
    """
    data = LoginJson.get_from_req()
    user = User.get_by_login(db_sess, data.login)

    if not user or not user.check_password(data.password):
        return response_msg("Неправильный логин или пароль", 400)

    response = jsonify(user.get_dict())
    access_token = create_access_token(user)
    set_access_cookies(response, access_token)
    return response


@bp.post("/api/logout")
@doc_api(desc="Remove auth cookie")
def logout():
    """Clear authentication cookies.

    Returns:
        Success message and removes JWT cookies.
    """
    response = response_msg("logout successful")
    unset_jwt_cookies(response)
    return response
