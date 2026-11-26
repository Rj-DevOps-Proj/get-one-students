"""Compatibility entry point for running the student service directly.

For the microservices deployment use ``docker compose up --build`` and send
requests to the API gateway on port 5000.
"""

from services.students.app import create_app

app = create_app()


if __name__ == "__main__":
    import os

    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5001")), debug=True)
