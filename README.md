# Hospital API

A small, production-shaped FastAPI service that does CRUD on a `patients` table.
It's the `hospital-api` referenced throughout the Azure DevOps task guide
(Docker/ACR, Container Apps, PostgreSQL + Key Vault, Application Insights,
Application Gateway health probes, and API Management/Swagger import).

## Features

- Full CRUD on `/api/patients` (create, list + search + pagination, get, update, delete)
- Interactive **Swagger UI** at `/docs` and ReDoc at `/redoc` (auto-generated OpenAPI spec — importable directly into APIM for Task 15)
- `/health` endpoint for container/load-balancer health probes
- Input validation (Pydantic) with clean, consistent JSON error responses — no raw stack traces ever returned to the client
- Works against SQLite out of the box (zero setup) or PostgreSQL by changing one environment variable
- Dockerfile + docker-compose (API + Postgres) for containerized runs

## Project layout

```
hospital-api/
├── app/
│   ├── main.py            # FastAPI app, middleware, error handlers, /health
│   ├── database.py        # SQLAlchemy engine/session
│   ├── models.py          # Patient ORM model
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── crud.py             # DB access functions
│   └── routers/
│       └── patients.py     # /api/patients endpoints
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── .gitignore
```

---

## Option A — Run locally (fastest way to see Swagger)

Requires Python 3.11+ (3.10+ also works).

```bash
cd hospital-api

# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) copy the env file — default SQLite needs no changes
cp .env.example .env

# 4. Run the API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health check:** http://localhost:8000/health

A `hospital.db` SQLite file is created automatically on first run — no database setup needed.

---

## Option B — Run with Docker (matches Task 3/4 of the guide)

Single container, still using SQLite inside the container:

```bash
cd hospital-api
docker build -t hospital-api:v1 .
docker run -d -p 8000:8000 --name hospital-api hospital-api:v1
```

Open http://localhost:8000/docs

---

## Option C — Run with docker-compose (API + real PostgreSQL, matches Task 5)

```bash
cd hospital-api
docker compose up --build
```

This starts a Postgres 16 container and the API, wired together with
`DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/hospitaldb`
(see `docker-compose.yml`). Swagger is still at http://localhost:8000/docs.

To stop and remove containers:
```bash
docker compose down
```
Add `-v` to also drop the Postgres data volume.

---

## Using your own Azure PostgreSQL (Task 5 — Key Vault integration)

Set `DATABASE_URL` to the connection string you pull from Key Vault instead of hardcoding it:

```bash
export DATABASE_URL="postgresql+psycopg2://<user>:<password>@<server>.postgres.database.azure.com:5432/<dbname>?sslmode=require"
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

In Container Apps, set this as an environment variable referencing the Key Vault secret rather than a plain string, per the guide's Task 5.

---

## Quick test via curl

```bash
# Create a patient
curl -X POST http://localhost:8000/api/patients \
  -H "Content-Type: application/json" \
  -d '{
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1990-05-12",
        "gender": "Male",
        "phone_number": "+91-9876543210",
        "email": "john.doe@example.com",
        "blood_group": "O+",
        "diagnosis": "Routine checkup"
      }'

# List patients
curl http://localhost:8000/api/patients

# Get one
curl http://localhost:8000/api/patients/1

# Update
curl -X PUT http://localhost:8000/api/patients/1 \
  -H "Content-Type: application/json" \
  -d '{"diagnosis": "Follow-up visit"}'

# Delete
curl -X DELETE http://localhost:8000/api/patients/1
```

Or just use the Swagger UI at `/docs` — every endpoint is documented there with a "Try it out" button.

## Error handling

- Invalid input → `422` with a structured `{"detail": ..., "errors": [...]}` body
- Missing patient → `404`
- Duplicate email → `409`
- Database unreachable → `503`
- Anything unexpected → `500` with a generic message (full details are logged server-side, never sent to the client)

## Pushing to Azure Container Registry (Task 3)

```bash
az acr create --name hospitalacr --resource-group myRG --sku Basic
az acr login --name hospitalacr
docker tag hospital-api:v1 hospitalacr.azurecr.io/hospital-api:v1
docker push hospitalacr.azurecr.io/hospital-api:v1
```

## Importing into API Management (Task 15)

Once deployed, point APIM's "Import OpenAPI" at:
```
http://<your-deployed-host>/openapi.json
```
FastAPI generates this spec automatically from the code — no manual Swagger file to maintain.
