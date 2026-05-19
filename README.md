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

## Screenshots Aplikasi

- Tampilan Utama Aplikasi dengan Berbagai Chart
<img width="1919" height="1149" alt="image" src="https://github.com/user-attachments/assets/73e4728c-7906-4f13-9474-862986661755" />
<img width="1919" height="1143" alt="image" src="https://github.com/user-attachments/assets/6fc9eba2-f9d3-450c-ba84-a99da320bf34" />
<img width="1919" height="1152" alt="image" src="https://github.com/user-attachments/assets/0bb69edf-9c00-4b45-8adc-622894bea216" />
<img width="1917" height="1147" alt="image" src="https://github.com/user-attachments/assets/8b851b3d-463f-4991-8d8b-b94ece601a47" />

- Tambah
<img width="1916" height="1154" alt="image" src="https://github.com/user-attachments/assets/5bdb991a-d570-47fb-b416-195eee51ad57" />
- Edit
<img width="1919" height="1152" alt="image" src="https://github.com/user-attachments/assets/a81ed663-673a-468b-8a88-846501050699" />
-Hapus
<img width="1919" height="1152" alt="image" src="https://github.com/user-attachments/assets/1a8f43d6-1af6-4b68-a8ea-582b1ceef6cf" />
-Export ke Gambar
<img width="1919" height="1152" alt="image" src="https://github.com/user-attachments/assets/b59699a9-435e-4f2f-afe9-0236678ac3a0" />

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
