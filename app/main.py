# Gurujix Storefront — Orders service (Phase 2 starting point)
#
# Living-proof e-commerce workload for the platform.
# Content/blogs stay on gurujix.com; this API is the running system.
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Gurujix Orders Service",
    description="Thin order API for the Gurujix Storefront (platform reference workload).",
    version="0.1.0",
)

# In-memory store only (no database in this step).
# Data is lost on process restart — intentional for Phase 2 thin slice.
_orders: dict[str, "Order"] = {}


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
    return order


@app.get("/orders/{order_id}")
def get_order(order_id: str) -> Order:
    """Fetch one order by id."""
    order = _orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
