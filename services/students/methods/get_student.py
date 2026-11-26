from flask import Blueprint, current_app, jsonify

from ..db import connect, execute


def get_student_blueprint():
    blueprint = Blueprint("get_student", __name__)

    @blueprint.route("/students/<int:student_id>", methods=["GET"])
    def get_student(student_id):
        connection = connect(current_app.config["DATABASE_URL"])
        try:
            row = execute(
                connection,
                "SELECT * FROM students WHERE id = %s",
                (student_id,),
            ).fetchone()
        finally:
            connection.close()

        if row is None:
            return jsonify({"error": "Student not found."}), 404
        return jsonify(dict(row))

    return blueprint
