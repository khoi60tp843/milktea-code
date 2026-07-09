"""
main.py
Entry point của backend. Chạy: uvicorn main:app --reload
Xem docs tự sinh tại: http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import get_connection, init_db
from models import OrderCreateRequest

app = FastAPI(title="Milktea Shop API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def home():
    return {"message": "Milktea Shop API đang chạy 🧋"}


@app.get("/menu")
def get_menu():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM menu_items").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.post("/orders")
def create_order(order: OrderCreateRequest):
    if not order.items:
        raise HTTPException(status_code=400, detail="Đơn hàng phải có ít nhất 1 món")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO orders (customer_name) VALUES (?)",
        (order.customer_name,),
    )
    order_id = cur.lastrowid

    total = 0
    for item in order.items:
        menu_row = cur.execute(
            "SELECT price FROM menu_items WHERE id = ?", (item.item_id,)
        ).fetchone()
        if menu_row is None:
            conn.rollback()
            conn.close()
            raise HTTPException(status_code=404, detail=f"Không tìm thấy món id={item.item_id}")

        total += menu_row["price"] * item.quantity
        cur.execute(
            "INSERT INTO order_items (order_id, item_id, quantity) VALUES (?, ?, ?)",
            (order_id, item.item_id, item.quantity),
        )

    conn.commit()
    conn.close()

    return {"order_id": order_id, "total_price": total, "status": "pending"}


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    conn = get_connection()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if order is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")

    items = conn.execute("""
        SELECT mi.name, mi.price, oi.quantity
        FROM order_items oi
        JOIN menu_items mi ON mi.id = oi.item_id
        WHERE oi.order_id = ?
    """, (order_id,)).fetchall()
    conn.close()
    items_list = [dict(i) for i in items]
    total_price = sum(item["price"] * item["quantity"] for item in items_list)
    return {
        "order_id": order["id"],
        "customer_name": order["customer_name"],
        "status": order["status"],
        "total_price": total_price,
        "items": items_list,
    }