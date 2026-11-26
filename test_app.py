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


def test_student_crud(client):
    listed = client.get("/students")
    assert listed.status_code == 200
    assert len(listed.get_json()) == 1


def test_invalid_student_is_rejected(client):
    response = client.post("/students", json={"name": "Incomplete"})
    assert response.status_code == 400


def test_service_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
    assert response.get_json()["service"] == "students"


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
