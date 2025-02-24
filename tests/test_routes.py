import unittest
import json
from todo import create_app
from todo.views.routes import tasks


class TestToDoApi(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.testing = True

        tasks.clear()

    def test_health_endpoint(self):
        """GET /api/v1/health

        Returns
        -------
        HTTP/1.1 200 OK
        Content-Type: application/json

        {
        "status": "ok"
        }
        """
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, {"status": "ok"})

    def test_create_todo(self):
        """POST /api/v1/todos

        Returns
        -------
        HTTP/1.1 201 Created
        Content-Type: application/json

        {
        "id": 1,
        "title": "Watch CSSE6400 Lecture",
        "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
        "completed": false,
        "deadline_at": "2025-02-27T00:00:00",
        "created_at": "2025-02-20T00:00:00",
        "updated_at": "2025-02-20T00:00:00"
        }
        """
        payload = {
            "title": "Watch CSSE6400 Lecture",
            "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
            "completed": False,
            "deadline_at": "2025-02-27T00:00:00",
        }
        response = self.client.post("/api/v1/todos", json=payload)
        self.assertEqual(response.status_code, 201)
        todo = json.loads(response.data)
        self.assertEqual(todo["title"], "Watch CSSE6400 Lecture")
        self.assertEqual(todo["description"], "Watch the CSSE6400 lecture on ECHO360 for week 1")
        self.assertEqual(todo["completed"], False)
        self.assertIn("created_at", todo)
        self.assertIn("updated_at", todo)

    def test_get_todo_by_id(self):
        """GET /api/v1/todos/{id}

        Returns
        -------
        HTTP/1.1 200 OK
        Content-Type: application/json

        {
        "id": 1,
        "title": "Watch CSSE6400 Lecture",
        "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
        "completed": false,
        "deadline_at": "2025-02-27T00:00:00",
        "created_at": "2025-02-20T00:00:00",
        "updated_at": "2025-02-20T00:00:00"
        }
        """
        payload = {"title": "Watch CSSE6400 Lecture"}
        response = self.client.post("/api/v1/todos", json=payload)
        todo = json.loads(response.data)

        response = self.client.get(f'/api/v1/todos/{todo["id"]}')
        self.assertEqual(response.status_code, 200)
        fetched = json.loads(response.data)
        self.assertEqual(fetched["id"], todo["id"])
        self.assertEqual(fetched["title"], "Watch CSSE6400 Lecture")

    def test_get_todos_empty(self):
        """GET /api/v1/todos

        Returns
        -------
        HTTP/1.1 200 OK
        Content-Type: application/json

        []
        """
        response = self.client.get("/api/v1/todos")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])

    def test_get_todos_with_filters(self):
        """GET /api/v1/todos?completed=true

        Returns
        -------
        HTTP/1.1 200 OK
        Content-Type: application/json
        [
            {
                "id": 1,
                "title": "Task 1",
                "description": "",
                "completed": true,
                "deadline_at": "2025-02-27T00:00:00",
                "created_at": "2023-02-20T00:00:00",
                "updated_at": "2023-02-20T00:00:00"
            },
            ...
        ]
        """
        self.client.post("/api/v1/todos", json={"title": "Task 1", "completed": True})
        self.client.post("/api/v1/todos", json={"title": "Task 2", "completed": False})

        response = self.client.get("/api/v1/todos?completed=true")
        self.assertEqual(response.status_code, 200)
        todos = json.loads(response.data)
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]["completed"], True)

    def test_update_todo(self):
        """PUT /api/v1/todos/{id} HTTP/1.1
        Content-Type: application/json

        {
        "title": "Updated Task",
        }

        Returns
        -------
        HTTP/1.1 200 OK
        Content-Type: application/json

        {
        "id": 1,
        "title": "Updated Task",
        "description": "",
        "completed": false,
        "deadline_at": "2025-02-27T00:00:00",
        "created_at": "2025-02-20T00:00:00",
        "updated_at": "2025-02-20T00:00:00"
        }
        """
        payload = {"title": "Initial Task"}
        response = self.client.post("/api/v1/todos", json=payload)
        todo = json.loads(response.data)

        update_payload = {"title": "Updated Task"}
        response = self.client.put(f"/api/v1/todos/{todo['id']}", json=update_payload)
        self.assertEqual(response.status_code, 200)
        updated = json.loads(response.data)
        self.assertEqual(updated["title"], "Updated Task")

    def test_update_todo_invalid_field(self):
        """PUT /api/v1/todos/{id}

        Returns
        -------
        HTTP/1.1 400 Bad Request
        """
        payload = {"title": "Initial Task"}
        response = self.client.post("/api/v1/todos", json=payload)
        todo = json.loads(response.data)

        update_payload = {"created_at": "2000-02-04T00:00:00"}
        response = self.client.put(f"/api/v1/todos/{todo['id']}", json=update_payload)
        self.assertEqual(response.status_code, 400)

    def test_delete_todo(self):
        """DELETE /api/v1/todos/{id}"""

        payload = {"title": "Task to delete"}
        response = self.client.post("/api/v1/todos", json=payload)
        todo = json.loads(response.data)

        response = self.client.delete(f"/api/v1/todos/{todo['id']}")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f"/api/v1/todos/{todo['id']}")
        self.assertEqual(response.status_code, 404)

    def test_delete_non_existent_todo(self):
        """DELETE /api/v1/todos/{id}"""
        response = self.client.delete("/api/v1/todos/9999")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), {})


if __name__ == "__main__":
    unittest.main()
