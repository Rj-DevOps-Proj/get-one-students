import os

import psycopg
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row


def get_database_url():
    if os.getenv("DATABASE_URL"):
        return os.environ["DATABASE_URL"]
    return make_conninfo(
        host=os.getenv("PGHOST", "database"),
        port=os.getenv("PGPORT", "5432"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD"),
        dbname=os.getenv("PGDATABASE", os.getenv("PGUSER", "postgres")),
    )


def connect(database_url):
    return psycopg.connect(database_url, row_factory=dict_row)


def execute(connection, query, parameters=()):
    return connection.execute(query, parameters)


INTEGRITY_ERRORS = (psycopg.IntegrityError,)


def init_db(database_url):
    connection = connect(database_url)
    try:
        execute(
            connection,
            """
            CREATE TABLE IF NOT EXISTS students (
                id BIGSERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                grade INTEGER NOT NULL
            )
            """,
        )
        connection.commit()
    finally:
        connection.close()


def fetch_student_by_id(database_url, student_id):
    connection = connect(database_url)
    try:
        row = execute(
            connection,
            "SELECT * FROM students WHERE id = %s",
            (student_id,),
        ).fetchone()
        return dict(row) if row is not None else None
    finally:
        connection.close()


def validate_student_payload(payload):
    if not isinstance(payload, dict):
        return None, ({"error": "A JSON object is required."}, 400)

    name = payload.get("name")
    email = payload.get("email")
    grade = payload.get("grade")

    if not isinstance(name, str) or not name.strip():
        return None, ({"error": "Name is required."}, 400)
    if not isinstance(email, str) or not email.strip():
        return None, ({"error": "Email is required."}, 400)
    if not isinstance(grade, int):
        return None, ({"error": "Grade must be an integer."}, 400)

    return {"name": name.strip(), "email": email.strip(), "grade": grade}, None
