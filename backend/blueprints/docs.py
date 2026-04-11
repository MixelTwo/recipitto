from bafser import get_api_docs, get_app_config, render_docs_page
from flask import Blueprint, abort, request

bp = Blueprint("docs", __name__)


@bp.route("/api")
def docs():
    """Serve API documentation.

    The endpoint is only available in development mode (DEV_MODE=True).
    If the query parameter `?json` is present, returns raw JSON API spec.
    Otherwise returns an HTML documentation page.

    Returns:
        Union[dict, str]: JSON API spec if `json` query param is provided,
            otherwise HTML page.

    Raises:
        HTTPException: 404 if not in development mode.
    """
    if not get_app_config().DEV_MODE:
        abort(404)
    if request.args.get("json") is not None:
        return get_api_docs()
    return render_docs_page()
