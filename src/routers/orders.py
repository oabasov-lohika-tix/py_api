from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from src.core.database import DatabaseConnection
from src.core.dependencies import get_db_connection
from src.schemas.requests import OrderCreateRequest
from src.schemas.responses import OrderListResponse, OrderResponse
from src.core.responses import success_response

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    responses={404: {"description": "Not found"}}
)

@router.get("", response_model=OrderListResponse, summary="List orders")
async def list_orders(
    db: DatabaseConnection = Depends(get_db_connection),
):
    orders = db.query_all("SELECT * FROM orders ORDER BY created_at DESC")
    return success_response(data=orders)

@router.get("/{order_id}", response_model=OrderResponse, summary="Get an order")
async def get_order(
    order_id: UUID,
    db: DatabaseConnection = Depends(get_db_connection),
):
    order = db.query_one("SELECT * FROM orders WHERE id = %s", (order_id,))
    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Order not found")
    return success_response(data=order)

@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an order",
)
async def create_order(
    payload: OrderCreateRequest,
    db: DatabaseConnection = Depends(get_db_connection),
):
    # flatten items into a DB insert — you’ll need your own SQL here
    created = db.query_one(
        "INSERT INTO orders (user_email, product_ids) VALUES (%s, %s) RETURNING *",
        (payload.user_email, payload.product_ids),
    )
    return success_response(data=created)

@router.put(
    "{order_id}",
    response_model=OrderResponse,
    summary="Update an order"
)
async def update_order(
    order_id: UUID,
    payload: OrderCreateRequest,
    db: DatabaseConnection = Depends(get_db_connection),
):
    # Verify the user exists
    user_check = db.query_one("SELECT * FROM users WHERE email = %s", (payload.user_email,))
    if not user_check:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check if the order exists
    order = db.query_one("SELECT * FROM orders WHERE id = %s", (order_id,))
    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Order not found")

    # Update the order
    updated_order = db.query_one(
        "UPDATE orders SET user_email = %s, product_ids = %s WHERE id = %s RETURNING *",
        (payload.user_email, payload.product_ids, order_id),
    )
    return success_response(data=updated_order)
