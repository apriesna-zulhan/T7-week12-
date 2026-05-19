# Dashboard Penjualan 2024 — PySide6

Aplikasi dashboard visualisasi data penjualan menggunakan **PySide6** dan **Matplotlib**, dengan backend **SQLite**.

## Identitas Mahasiswa
- **Nama:** Apriesna Zulhan
- **NIM:** F1D02310100

---

## Struktur Project

```
dashboard_penjualan/
├── main.py          # Entry point aplikasi
├── main_window.py   # Window utama & layout dashboard
├── chart_widget.py  # Widget Matplotlib tertanam di PySide6
├── crud_dialog.py   # Dialog Tambah / Edit data
├── database.py      # Koneksi SQLite, CRUD, seed data
├── penjualan.db     # File database SQLite 
├── requirements.txt # Dependensi Python
└── README.md        # Dokumentasi ini
```

---

## Struktur Database SQLite

File: `penjualan.db`

### Tabel: `penjualan`

| Kolom      | Tipe    | Keterangan                             |
|------------|---------|----------------------------------------|
| `id`       | INTEGER | Primary key, auto-increment            |
| `tanggal`  | TEXT    | Tanggal transaksi format `YYYY-MM-DD`  |
| `kategori` | TEXT    | Kategori produk (5 kategori)           |
| `produk`   | TEXT    | Nama produk                            |
| `jumlah`   | INTEGER | Jumlah item terjual                    |
| `harga`    | REAL    | Harga satuan (Rupiah)                  |
| `total`    | REAL    | Total = jumlah × harga                 |

**Kategori yang tersedia:** Elektronik, Pakaian, Makanan, Olahraga, Rumah Tangga

Database di-seed otomatis dengan **80 baris data** realistis saat pertama kali dijalankan.

---

## Fitur Aplikasi

### Visualisasi Data
| Fitur | Detail |
|-------|--------|
| **QTableWidget** | Menampilkan semua data mentah dari database |
| **Bar Chart** | Pendapatan total per kategori |
| **Pie Chart** | Distribusi jumlah item per kategori |
| **Line Chart** | Tren pendapatan bulanan sepanjang 2024 |
| **Scatter Chart** | Korelasi jumlah item vs total pendapatan |

### Kontrol & Filter
- **Filter Kategori** — tampilkan data per kategori atau semua
- **Pilihan Tipe Chart** — 4 jenis chart tersedia
- **Tombol Refresh** — memuat ulang data dari database
- **Tombol Export PNG** — menyimpan chart aktif ke file `.png`

### CRUD
- **Tambah** — form dialog untuk input transaksi baru
- **Tampil** — tabel data real-time dari SQLite
- **Edit** — klik baris → Edit, ubah data via dialog
- **Hapus** — klik baris → Hapus, dengan konfirmasi
- **Refresh dashboard** otomatis setelah setiap operasi CRUD

---

## Cara Menjalankan

### 1. Install dependensi
```bash
pip install -r requirements.txt
```

### 2. Jalankan aplikasi
```bash
python main.py
```

Database `penjualan.db` akan otomatis dibuat dan diisi 80 data saat pertama kali dijalankan.

---

## Catatan Teknis
- Chart ditampilkan **langsung di dalam PySide6** menggunakan `FigureCanvasQTAgg` — tidak ada window Matplotlib terpisah.
- UI responsif saat window di-resize menggunakan `QSplitter` dan `QHeaderView.Stretch`.
- Warna menggunakan dark theme konsisten dengan CSS variables.
