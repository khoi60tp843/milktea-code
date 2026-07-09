"""
models.py
Pydantic models = định nghĩa "hình dạng" dữ liệu ra vào API.
FastAPI dùng cái này để tự kiểm tra dữ liệu + tự sinh docs.
"""
from pydantic import BaseModel
from typing import List


class MenuItem(BaseModel):
    id: int
    name: str
    price: int
    description: str | None = None


class OrderItemRequest(BaseModel):
    item_id: int
    quantity: int = 1


class OrderCreateRequest(BaseModel):
    customer_name: str
    items: List[OrderItemRequest]