from bafser import get_app_config, render_docs_page, get_api_docs
from flask import Blueprint, abort, request

bp = Blueprint("docs", __name__)


@bp.route("/api")
def docs():
    if not get_app_config().DEV_MODE:
        abort(404)
    if request.args.get("json") is not None:
        return get_api_docs()
    return render_docs_page()
