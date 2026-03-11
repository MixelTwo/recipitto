from bafser import JsonObj, JsonOpt, Undefined, abort_if_none, doc_api, jsonify_list, protected_route, response_msg, use_db_sess
from flask import Blueprint
from sqlalchemy.orm import Session

from data._operations import Operations
from data.comment import Comment, CommentDict
from data.recipe import Recipe
from data.user import User

bp = Blueprint("comment", __name__)


class CreateCommentJson(JsonObj):
    text: str


class UpdateCommentJson(JsonObj):
    text: JsonOpt[str] = Undefined


@bp.get("/api/recipes/<int:recipe_id>/comments")
@doc_api(res=list[CommentDict], desc="List comments of a recipe")
@use_db_sess
def list_comments(db_sess: Session, recipe_id: int):
    abort_if_none(Recipe.get2(recipe_id), "recipe")
    comments = Comment.get_by_recipe(db_sess, recipe_id)
    return jsonify_list(comments)


@bp.get("/api/comments/<int:comment_id>")
@doc_api(res=CommentDict, desc="Get a comment by ID")
def get_comment(comment_id: int):
    comment = abort_if_none(Comment.get2(comment_id), "comment")
    return comment.get_dict()


@bp.post("/api/recipes/<int:recipe_id>/comments")
@doc_api(req=CreateCommentJson, res=CommentDict, desc="Create a comment on a recipe")
@protected_route(perms=Operations.comment_create)
def create_comment(recipe_id: int):
    abort_if_none(Recipe.get2(recipe_id), "recipe")
    req = CreateCommentJson.get_from_req()
    comment = Comment.new(
        user_id=User.current.id,
        recipe_id=recipe_id,
        text=req.text,
    )
    return comment.get_dict()


@bp.patch("/api/comments/<int:comment_id>")
@doc_api(req=UpdateCommentJson, res=CommentDict, desc="Update a comment")
@protected_route(perms=Operations.comment_update)
def update_comment(comment_id: int):
    comment = abort_if_none(Comment.get2(comment_id), "comment")
    # Check ownership: if user is not admin and not author, deny
    if not User.current.has_operation(Operations.admin_manage_comments) and comment.user_id != User.current.id:
        return response_msg("You can only edit your own comments", 403)
    req = UpdateCommentJson.get_from_req()
    comment.update(
        text=Undefined.default(req.text, None),
    )
    return comment.get_dict()


@bp.delete("/api/comments/<int:comment_id>")
@doc_api(res=None, desc="Delete a comment")
@protected_route(perms=Operations.comment_delete)
def delete_comment(comment_id: int):
    comment = abort_if_none(Comment.get2(comment_id), "comment")
    # Check ownership: if user is not admin and not author, deny
    if not User.current.has_operation(Operations.admin_manage_comments) and comment.user_id != User.current.id:
        return response_msg("You can only delete your own comments", 403)
    comment.delete2()
    return "", 204
