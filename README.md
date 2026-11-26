# School Management API

## Run locally

The Docker image connects to PostgreSQL at host `database`, port `5432`.
Supply the database name, user, and password through the standard PostgreSQL
variables (`PGDATABASE`, `PGUSER`, and `PGPASSWORD`), or set a `DATABASE_URL`.
The application requires a PostgreSQL connection; it has no local database
fallback.

To run tests, set `TEST_DATABASE_URL` to a PostgreSQL test database. Tests
create and remove an isolated schema for each test.

Start the Flask API in one terminal:

```bash
cd Dev/Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The API listens on port `5000` and binds to all network interfaces. Check it
at `http://localhost:5000/health`.

In a second terminal, serve the frontend over HTTP:

```bash
cd Dev/Frontend
python3 -m http.server 8000 --bind 0.0.0.0
```

Open `http://localhost:8000`. The frontend uses the hostname in the page URL
for API requests, so when accessing it from another device, use the server
machine's hostname or LAN IP in the frontend URL. Do not open `index.html`
directly as a `file://` URL; browsers restrict API requests from local files.

## API endpoints

- `GET /health`
- `GET /students`
- `POST /students`
- `GET /students/<id>`
- `PATCH /students/<id>`
- `DELETE /students/<id>`
