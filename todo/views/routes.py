from flask import Blueprint, jsonify

api = Blueprint("api", __name__, url_prefix="/api/v1")


def dummy():
    return jsonify({
        "id": 1,
        "title": "Watch CSSE6400 Lecture",
        "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
        "completed": True,
        "deadline_at": "2023-02-27T00:00:00",
        "created_at": "2023-02-20T00:00:00",
        "updated_at": "2023-02-20T00:00:00"
    })


@api.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@api.route("/todos", methods=["GET"])
def get_todos():
    return jsonify([dummy().json]), 200


@api.route("/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    return dummy(), 200


@api.route("/todos", methods=["POST"])
def create_todo():
    return dummy(), 201


@api.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    return dummy(), 200


@api.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    return dummy(), 200
