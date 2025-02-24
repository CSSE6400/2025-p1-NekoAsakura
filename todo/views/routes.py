from flask import Blueprint, jsonify, request, abort
from datetime import datetime, timedelta

api = Blueprint("api", __name__, url_prefix="/api/v1")

tasks = {}
next_id = 1


@api.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@api.route("/todos", methods=["GET"])
def get_todos():
    completed = request.args.get("completed")
    window = request.args.get("window", type=int)
    result = list(tasks.values())
    filter = {}

    if completed is not None:
        if completed.lower() == "true":
            filter["completed"] = True
        elif completed.lower() == "false":
            filter["completed"] = False
        else:
            return jsonify({"error": "Invalid value for completed"}), 400
        result = [task for task in result if task.get("completed") == filter["completed"]]

    if window is not None:
        cutoff = datetime.now() + timedelta(days=window)
        filtered = []
        for task in result:
            deadline_str = task.get("deadline_at")
            if deadline_str:
                try:
                    deadline = datetime.strptime(deadline_str, "%Y-%m-%dT%H:%M:%S")
                    if deadline <= cutoff:
                        filtered.append(task)
                except ValueError:
                    continue
        result = filtered
    return jsonify(result), 200


@api.route("/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    task = tasks.get(todo_id)
    if not task:
        abort(404)
    return jsonify(task), 200


@api.route("/todos", methods=["POST"])
def create_todo():
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "Title is required"}), 400

    allowed_fields = {"title", "description", "completed", "deadline_at"}
    if not set(data.keys()).issubset(allowed_fields):
        return jsonify({"error": "Invalid fields in payload"}), 400

    global next_id
    todo_id = next_id
    next_id += 1

    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    task = {
        "id": todo_id,
        "title": data.get("title"),
        "description": data.get("description", ""),
        "completed": data.get("completed", False),
        "deadline_at": data.get(
            "deadline_at",
            (datetime.strptime(now, "%Y-%m-%dT%H:%M:%S") + timedelta(days=7))
            .replace(hour=0, minute=0, second=0, microsecond=0)
            .strftime("%Y-%m-%dT%H:%M:%S"),
        ),
        "created_at": now,
        "updated_at": now,
    }
    tasks[todo_id] = task
    return jsonify(task), 201


@api.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    task = tasks.get(todo_id)
    if not task:
        abort(404)

    data = request.get_json()
    allowed_fields = {"title", "description", "completed", "deadline_at"}
    if not data or not set(data.keys()).issubset(allowed_fields):
        return jsonify({"error": "Invalid fields in payload"}), 400

    for field in allowed_fields:
        if field in data:
            task[field] = data[field]
    task["updated_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    tasks[todo_id] = task
    return jsonify(task), 200


@api.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    task = tasks.pop(todo_id, None)
    if task is None:
        return jsonify({}), 200
    return jsonify(task), 200
