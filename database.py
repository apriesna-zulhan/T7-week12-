"""
database.py
Modul untuk manajemen database SQLite: koneksi, inisialisasi tabel, dan seed data.
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "penjualan.db")

PRODUK_PER_KATEGORI = {
    "Elektronik": ["Laptop", "Smartphone", "Tablet", "Headphone", "Smartwatch"],
    "Pakaian":    ["Kaos", "Jaket", "Celana Jeans", "Dress", "Hoodie"],
    "Makanan":    ["Kopi Arabica", "Coklat Premium", "Teh Herbal", "Snack Box", "Madu Murni"],
    "Olahraga":   ["Sepatu Lari", "Dumbbell", "Matras Yoga", "Raket Badminton", "Sepeda Lipat"],
    "Rumah Tangga": ["Blender", "Rice Cooker", "Vacuum Cleaner", "Lampu LED", "Rak Buku"],
}

HARGA_PRODUK = {
    "Laptop": 8500000, "Smartphone": 4200000, "Tablet": 3100000,
    "Headphone": 850000, "Smartwatch": 1200000,
    "Kaos": 120000, "Jaket": 350000, "Celana Jeans": 280000,
    "Dress": 220000, "Hoodie": 300000,
    "Kopi Arabica": 95000, "Coklat Premium": 75000, "Teh Herbal": 55000,
    "Snack Box": 65000, "Madu Murni": 110000,
    "Sepatu Lari": 650000, "Dumbbell": 420000, "Matras Yoga": 180000,
    "Raket Badminton": 320000, "Sepeda Lipat": 2800000,
    "Blender": 380000, "Rice Cooker": 450000, "Vacuum Cleaner": 920000,
    "Lampu LED": 85000, "Rak Buku": 260000,
}


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Buat tabel dan isi data awal jika belum ada."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS penjualan (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal   TEXT    NOT NULL,
            kategori  TEXT    NOT NULL,
            produk    TEXT    NOT NULL,
            jumlah    INTEGER NOT NULL,
            harga     REAL    NOT NULL,
            total     REAL    NOT NULL
        )
    """)
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM penjualan")
    if cur.fetchone()[0] == 0:
        _seed_data(cur, conn)

    conn.close()


def _seed_data(cur, conn):
    """Generate 80 baris data penjualan realistis."""
    random.seed(42)
    start = datetime(2024, 1, 1)
    records = []

    for _ in range(80):
        delta = timedelta(days=random.randint(0, 364))
        tanggal = (start + delta).strftime("%Y-%m-%d")
        kategori = random.choice(list(PRODUK_PER_KATEGORI.keys()))
        produk   = random.choice(PRODUK_PER_KATEGORI[kategori])
        jumlah   = random.randint(1, 15)
        harga    = HARGA_PRODUK[produk]
        # variasi harga ±10%
        harga    = round(harga * random.uniform(0.90, 1.10), -2)
        total    = round(harga * jumlah, 2)
        records.append((tanggal, kategori, produk, jumlah, harga, total))

    cur.executemany(
        "INSERT INTO penjualan (tanggal, kategori, produk, jumlah, harga, total) VALUES (?,?,?,?,?,?)",
        records,
    )
    conn.commit()


# CRUD 

def fetch_all(kategori_filter: str = "Semua") -> list[dict]:
    conn = get_connection()
    cur  = conn.cursor()
    if kategori_filter == "Semua":
        cur.execute("SELECT * FROM penjualan ORDER BY tanggal DESC")
    else:
        cur.execute(
            "SELECT * FROM penjualan WHERE kategori=? ORDER BY tanggal DESC",
            (kategori_filter,),
        )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def insert_row(tanggal, kategori, produk, jumlah, harga, total) -> int:
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO penjualan (tanggal, kategori, produk, jumlah, harga, total) VALUES (?,?,?,?,?,?)",
        (tanggal, kategori, produk, jumlah, harga, total),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def update_row(row_id, tanggal, kategori, produk, jumlah, harga, total):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "UPDATE penjualan SET tanggal=?, kategori=?, produk=?, jumlah=?, harga=?, total=? WHERE id=?",
        (tanggal, kategori, produk, jumlah, harga, total, row_id),
    )
    conn.commit()
    conn.close()


def delete_row(row_id):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("DELETE FROM penjualan WHERE id=?", (row_id,))
    conn.commit()
    conn.close()


def get_categories() -> list[str]:
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT DISTINCT kategori FROM penjualan ORDER BY kategori")
    cats = [r[0] for r in cur.fetchall()]
    conn.close()
    return ["Semua"] + cats


def get_summary() -> dict:
    """Statistik ringkasan untuk header dashboard."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT COUNT(*), SUM(total), SUM(jumlah) FROM penjualan")
    row = cur.fetchone()
    conn.close()
    return {
        "total_transaksi": row[0] or 0,
        "total_pendapatan": row[1] or 0,
        "total_item":       row[2] or 0,
    }
