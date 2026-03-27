from bafser import Image, doc_api
from flask import Blueprint, abort

bp = Blueprint("images", __name__)


@bp.route("/api/img/<int:imgId>")
@doc_api(desc="Get image as file")
def img(imgId: int):
    img = Image.get2(imgId)
    if img is None:
        abort(404)

    return img.create_file_response()
