"""
database.py
Quản lý kết nối SQLite + tạo bảng ban đầu.
"""
import sqlite3

DB_NAME = "milktea.db"


def get_connection():
    """Mỗi lần cần thao tác DB, gọi hàm này để lấy connection mới."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # cho phép truy cập cột theo tên, vd row["title"]
    return conn


def init_db():
    """Chạy 1 lần khi khởi động app để đảm bảo bảng tồn tại."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            description TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (item_id) REFERENCES menu_items(id)
        )
    """)

    cur.execute("SELECT COUNT(*) FROM menu_items")
    if cur.fetchone()[0] == 0:
        sample_items = [
            ("Trà sữa truyền thống", 25000, "Trà đen + sữa + trân châu đen"),
            ("Trà sữa matcha", 30000, "Matcha Nhật + sữa tươi"),
            ("Trà sữa Thái xanh", 28000, "Trà Thái + sữa + trân châu"),
            ("Hồng trà chanh sả", 22000, "Hồng trà + chanh + sả tươi"),
        ]
        cur.executemany(
            "INSERT INTO menu_items (name, price, description) VALUES (?, ?, ?)",
            sample_items,
        )

    conn.commit()
    conn.close()