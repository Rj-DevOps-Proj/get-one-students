from urllib.parse import urlsplit

from flask import Flask, request

from .db import get_database_url, init_db
from .methods.get_student import get_student_blueprint
from .methods.health import health_blueprint


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE_URL=get_database_url(),
        TESTING=False,
    )
    if config:
        app.config.update(config)

    @app.before_request
    def log_request():
        app.logger.info(
            "\033[94mvisitor_ip = %s ; path= %s\033[0m",
            request.headers.get("X-Real-IP"),
            request.path,
        )

    def is_allowed_frontend_origin(origin):
        try:
            parsed_origin = urlsplit(origin)
            valid_origin = (
                parsed_origin.scheme in {"http", "https"}
                and parsed_origin.hostname is not None
                and parsed_origin.username is None
                and parsed_origin.password is None
                and parsed_origin.path == ""
                and parsed_origin.query == ""
                and parsed_origin.fragment == ""
            )
            if not valid_origin:
                return False
            if parsed_origin.hostname in {"localhost", "127.0.0.1"}:
                return True

            request_host = urlsplit(f"//{request.host}").hostname
            return parsed_origin.hostname == request_host
        except ValueError:
            return False

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin")
        if origin and is_allowed_frontend_origin(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
            response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response.headers["Vary"] = "Origin"
        return response

    init_db(app.config["DATABASE_URL"])

    app.register_blueprint(health_blueprint())
    app.register_blueprint(get_student_blueprint())

    return app
