from bafser import get_app_config, render_docs_page
from flask import Blueprint, abort

bp = Blueprint("docs", __name__)


@bp.route("/api")
def docs():
    if not get_app_config().DEV_MODE:
        abort(404)
    return render_docs_page()
