import os
import uuid

import psycopg
import pytest
from psycopg import sql
from psycopg.conninfo import make_conninfo
from services.students.app import create_app


@pytest.fixture()
def client():
    database_url = os.environ.get("TEST_DATABASE_URL")
    if not database_url:
        pytest.fail("TEST_DATABASE_URL must point to a PostgreSQL test database.")

    schema = f"test_{uuid.uuid4().hex}"
    with psycopg.connect(database_url, autocommit=True) as connection:
        connection.execute(
            sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema))
        )

    isolated_database_url = make_conninfo(
        database_url,
        options=f"-c search_path={schema}",
    )
    try:
        app = create_app({"TESTING": True, "DATABASE_URL": isolated_database_url})
        with app.test_client() as test_client:
            yield test_client
    finally:
        with psycopg.connect(database_url, autocommit=True) as connection:
            connection.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema))
            )


def test_student_can_be_retrieved(client):
    connection = psycopg.connect(client.application.config["DATABASE_URL"])
    try:
        cursor = connection.execute(
            """
            INSERT INTO students (name, email, grade)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            ("Amina Yusuf", "amina@example.com", 8),
        )
        student_id = cursor.fetchone()[0]
        connection.commit()
    finally:
        connection.close()

    response = client.get(f"/students/{student_id}")
    assert response.status_code == 200
    assert response.get_json() == {
        "id": student_id,
        "name": "Amina Yusuf",
        "email": "amina@example.com",
        "grade": 8,
    }


def test_missing_student_returns_not_found(client):
    response = client.get("/students/999999")
    assert response.status_code == 404


def test_service_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
    assert response.get_json()["service"] == "Get One Student Service"


def test_cors_allows_local_frontend_development_port(client):
    response = client.get("/students", headers={"Origin": "http://localhost:5500"})

    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:5500"


def test_cors_rejects_non_local_frontend(client):
    response = client.get("/students", headers={"Origin": "https://example.com"})

    assert "Access-Control-Allow-Origin" not in response.headers


def test_cors_allows_frontend_on_same_host(client):
    response = client.get(
        "/students",
        headers={"Host": "192.168.1.10:5000", "Origin": "http://192.168.1.10:8000"},
    )

    assert response.headers["Access-Control-Allow-Origin"] == "http://192.168.1.10:8000"


def test_cors_rejects_different_non_local_frontend_host(client):
    response = client.get(
        "/students",
        headers={"Host": "192.168.1.10:5000", "Origin": "https://example.com"},
    )

    assert "Access-Control-Allow-Origin" not in response.headers
