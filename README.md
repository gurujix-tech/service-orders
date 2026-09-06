# Gurujix Orders Service (`service-orders`)

Thin FastAPI order API for the **Gurujix Storefront** — a living-proof e-commerce workload for the platform.

- Content hub / blogs: `https://gurujix.com/` (not this service)
- Future app hostname: `https://app.gurujix.com` (later)
- Platform portal: `platform-portal`

## Current scope

- `GET /health` — liveness (process up)
- `GET /ready` — readiness (safe to receive traffic)
- `POST /orders` — create an order (in-memory)
- `GET /orders/{order_id}` — fetch an order

No database yet. Restarting the process clears orders.

## Prerequisites

- Python 3.12+ (3.13 is fine)
- `python3 -m venv` available

## Run locally

```sh
cd service-orders
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

For local development including tests, prefer:

```sh
pip install -r requirements-dev.txt
```

### Probes

```sh
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/ready
```

### Create and fetch an order

```sh
curl -s -X POST http://127.0.0.1:8080/orders \
  -H 'Content-Type: application/json' \
  -d '{"product_id":"sku-tea-001","quantity":2,"customer_email":"guest@gurujix.com"}'

# copy the "id" from the response, then:
curl -s http://127.0.0.1:8080/orders/<order-id>
```

Interactive API docs: `http://127.0.0.1:8080/docs`

## Lint and format

Uses [Ruff](https://docs.astral.sh/ruff/) (config in `pyproject.toml`):

```sh
source .venv/bin/activate
pip install -r requirements-dev.txt
ruff check .
ruff format --check .
# to apply formatting:
ruff format .
```

## Tests

```sh
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
```

CI runs on GitHub Actions (`.github/workflows/ci.yml`) for pull requests and pushes to `main`:

1. **gitleaks** — secret scan (blocks known secret patterns in git history). Requires repo secret **`GITLEAKS_LICENSE`** (from [gitleaks.io](https://gitleaks.io)); the workflow must pass it as `GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}`. Do **not** create a secret named `GITHUB_TOKEN` (built-in; names cannot start with `GITHUB_`).
2. **ruff** — lint + format check
3. **pip-audit** — known vulnerabilities in Python deps
4. **pytest**
5. **docker build** + smoke `/health`
6. **ECR publish** (main only) — needs secret `AWS_ROLE_ARN` and variable `ECR_PUBLISH=true`

Dependabot (`.github/dependabot.yml`) opens weekly PRs for pip and Actions updates.

## Docker

Requires Docker Desktop (or another Docker engine) running.

```sh
docker build -t service-orders:local .
docker run --rm -p 8080:8080 service-orders:local
```

In another terminal:

```sh
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/ready
```

Stop the container with Ctrl+C in the `docker run` terminal.

## Software Catalog

`catalog-info.yaml` describes this service for Backstage:

```text
Domain: gurujix
  └── System: storefront
        └── Component: service-orders
              owner: storefront-team
```

Locally, `platform-portal` loads this file from the sibling path so the component appears in the Catalog UI.
