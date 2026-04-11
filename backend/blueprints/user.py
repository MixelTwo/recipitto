from bafser import Image, ImageJson, JsonObj, JsonOpt, Log, Undefined, doc_api, protected_route, response_msg
from flask import Blueprint

from data.user import User, UserDict

bp = Blueprint("user", __name__)


class UpdateUserJson(JsonObj):
    name: JsonOpt[str] = Undefined
    avatar: JsonOpt[ImageJson | None] = Undefined


@bp.route("/api/user")
@doc_api(res=UserDict, desc="Get current user")
@protected_route()
def user() -> UserDict:
    """Retrieve the currently authenticated user's profile.

    Requires authentication.

    Returns:
        dict: The user object of the authenticated user.
    """
    return User.current.get_dict()


@bp.patch("/api/user")
@doc_api(req=UpdateUserJson, res=UserDict, desc="Update current user")
@protected_route()
def update_user():
    req = UpdateUserJson.get_from_req()
    user = User.current

    # Update avatar if defined
    if Undefined.defined(req.avatar):
        value = req.avatar
        avatar_id = None
        if value is not None:
            image, error = Image.new(user, value)
            if error:
                return response_msg(f"Image upload failed: {error}", 400)
            assert image is not None
            avatar_id = image.id
            if user.avatar:
                user.avatar.delete2(commit=False)
        user.avatar_id = avatar_id

    # Update name if defined
    if Undefined.defined(req.name):
        user.name = req.name

    # Commit changes
    Log.updated(user)
    return user.get_dict()
