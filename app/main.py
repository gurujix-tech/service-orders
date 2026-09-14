# Gurujix Storefront — Orders service (Phase 2 starting point)
#
# Living-proof e-commerce workload for the platform.
# Content/blogs stay on gurujix.com; this API is the running system.
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field

app = FastAPI(
    title="Gurujix Orders Service",
    description="Thin order API for the Gurujix Storefront (platform reference workload).",
    version="0.1.0",
)

# In-memory store only (no database in this step).
# Data is lost on process restart — intentional for Phase 2 thin slice.
_orders: dict[str, "Order"] = {}

# --- Phase 6a step 2: one business metric (you control when it increases) ---
# Counter = number that only goes up (resets when the process restarts).
ORDERS_CREATED = Counter(
    "orders_created_total",
    "Number of storefront orders successfully created",
)

# --- Phase 6a step 3+5: count every HTTP request (RED rate/errors) ---
# Label "handler" = route template (/orders/{order_id}), NOT raw URL with ids.
HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "handler", "status"],
)

# --- Phase 6a step 4: how long each request took (RED "duration") ---
# Histogram records observations into buckets (not a single average).
HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "handler"],
)


def _handler_label(request: Request) -> str:
    """Prefer route template over raw path (avoids one series per order id)."""
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    return path if isinstance(path, str) else request.url.path


@app.middleware("http")
async def http_requests_middleware(request: Request, call_next):
    """Wrap each request: measure duration, then count the request."""
    # Don't count scrapes of /metrics as application traffic.
    if request.url.path == "/metrics":
        return await call_next(request)

    start = perf_counter()
    response = await call_next(request)
    elapsed = perf_counter() - start

    # After call_next, the matched route is available → use template label.
    handler = _handler_label(request)
    HTTP_REQUEST_DURATION.labels(request.method, handler).observe(elapsed)
    HTTP_REQUESTS.labels(
        request.method,
        handler,
        str(response.status_code),
    ).inc()
    return response


# --- Phase 6a step 1: scrape endpoint only ---
@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    """Expose Prometheus text so a scraper (or curl) can read process metrics."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


class OrderCreate(BaseModel):
    """Request body to place an order."""

    product_id: str = Field(min_length=1, examples=["sku-tea-001"])
    quantity: int = Field(gt=0, examples=[2])
    customer_email: str = Field(min_length=3, examples=["guest@gurujix.com"])


class Order(BaseModel):
    """Stored order returned by the API."""

    id: str
    product_id: str
    quantity: int
    customer_email: str
    status: str = "created"


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness: process is up. No dependency checks here."""
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    """Readiness: safe to receive traffic.

    Today there are no external dependencies, so ready == ok.
    Later this checks things like DB/cache connectivity and returns
    non-200 when the process is alive but not ready to serve.
    """
    return {"status": "ready"}


@app.post("/orders", status_code=201)
def create_order(payload: OrderCreate) -> Order:
    """Create a storefront order (in-memory)."""
    order = Order(
        id=str(uuid4()),
        product_id=payload.product_id,
        quantity=payload.quantity,
        customer_email=payload.customer_email,
    )
    _orders[order.id] = order
    ORDERS_CREATED.inc()  # step 2: record the business event
    return order


@app.get("/orders/{order_id}")
def get_order(order_id: str) -> Order:
    """Fetch one order by id."""
    order = _orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
