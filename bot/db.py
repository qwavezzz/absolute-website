import sqlite3
import asyncio
from typing import List, Optional

from models import Order

conn = sqlite3.connect("orders.db", check_same_thread=False)
conn.row_factory = sqlite3.Row


def init_db() -> None:
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                telegram_id INTEGER,
                product_name TEXT,
                size TEXT,
                contact TEXT,
                status TEXT,
                created_at TEXT
            )
            """
        )


def _create_order(order: Order) -> None:
    with conn:
        conn.execute(
            "INSERT INTO orders VALUES (?,?,?,?,?,?,?)",
            (
                order.id,
                order.telegram_id,
                order.product_name,
                order.size,
                order.contact,
                order.status,
                order.created_at,
            ),
        )


async def create_order(order: Order) -> None:
    await asyncio.to_thread(_create_order, order)


def _update_status(order_id: str, status: str) -> None:
    with conn:
        conn.execute(
            "UPDATE orders SET status=? WHERE id=?",
            (status, order_id),
        )


async def update_status(order_id: str, status: str) -> None:
    await asyncio.to_thread(_update_status, order_id, status)


def _get_orders_by_status(status: str) -> List[Order]:
    cursor = conn.execute("SELECT * FROM orders WHERE status=?", (status,))
    rows = cursor.fetchall()
    return [Order(**dict(row)) for row in rows]


async def get_orders_by_status(status: str) -> List[Order]:
    return await asyncio.to_thread(_get_orders_by_status, status)


def _get_order(order_id: str) -> Optional[Order]:
    cursor = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    row = cursor.fetchone()
    return Order(**dict(row)) if row else None


async def get_order(order_id: str) -> Optional[Order]:
    return await asyncio.to_thread(_get_order, order_id)
