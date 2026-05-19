"""
main_window.py
Window utama dashboard penjualan.
"""

from __future__ import annotations

import os
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QTableWidget,
    QTableWidgetItem, QSplitter, QFrame, QFileDialog,
    QMessageBox, QHeaderView, QAbstractItemView,
    QSizePolicy, QStatusBar,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QIcon

from database import (
    fetch_all, insert_row, update_row, delete_row,
    get_categories, get_summary, init_db,
)
from chart_widget import ChartWidget
from crud_dialog import CRUDDialog

CHART_TYPES = [
    "Bar – Pendapatan per Kategori",
    "Pie – Distribusi Kategori",
    "Line – Tren Penjualan Bulanan",
    "Scatter – Jumlah vs Total",
]

# Stylesheet 
STYLE = """
* { font-family: 'Segoe UI', 'Arial', sans-serif; }

QMainWindow, QWidget#central { background: #151827; }

/* Sidebar / panel */
QFrame#panel {
    background: #1E2132;
    border-radius: 10px;
}

/* Stat card */
QFrame#statCard {
    background: #252A40;
    border-radius: 8px;
    border: 1px solid #2E3250;
}

/* Table */
QTableWidget {
    background: #1E2132;
    color: #D0D6F9;
    gridline-color: #2E3250;
    border: none;
    font-size: 12px;
}
QTableWidget::item { padding: 4px 8px; }
QTableWidget::item:selected {
    background: #344070;
    color: #FFFFFF;
}
QHeaderView::section {
    background: #252A40;
    color: #8090C0;
    font-weight: bold;
    font-size: 11px;
    border: none;
    border-bottom: 1px solid #2E3250;
    padding: 6px 8px;
}

/* Buttons */
QPushButton {
    border-radius: 7px;
    padding: 7px 16px;
    font-size: 12px;
    font-weight: 600;
    border: none;
    color: white;
}
QPushButton#btnRefresh  { background: #4F86C6; }
QPushButton#btnRefresh:hover { background: #5F96D6; }
QPushButton#btnExport   { background: #3A9E6E; }
QPushButton#btnExport:hover  { background: #4ABE7E; }
QPushButton#btnAdd      { background: #6B5CE7; }
QPushButton#btnAdd:hover     { background: #7B6CF7; }
QPushButton#btnEdit     { background: #E8864A; }
QPushButton#btnEdit:hover    { background: #F8965A; }
QPushButton#btnDelete   { background: #E05252; }
QPushButton#btnDelete:hover  { background: #F06262; }

/* ComboBox */
QComboBox {
    background: #252A40;
    border: 1px solid #3A4170;
    border-radius: 6px;
    color: #D0D6F9;
    padding: 5px 10px;
    font-size: 12px;
    min-width: 180px;
    min-height: 28px;
}
QComboBox::drop-down { border: none; padding-right: 8px; }
QComboBox QAbstractItemView {
    background: #252A40;
    color: #D0D6F9;
    selection-background-color: #4F86C6;
}

/* Status bar */
QStatusBar { background: #151827; color: #606880; font-size: 11px; }

/* Scroll */
QScrollBar:vertical {
    background: #1E2132; width: 8px;
}
QScrollBar::handle:vertical {
    background: #3A4170; border-radius: 4px; min-height: 20px;
}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        init_db()
        self._current_data: list[dict] = []
        self._setup_ui()
        self._refresh()

    # UI Setup 

    def _setup_ui(self):
        self.setWindowTitle("Dashboard Penjualan 2024")
        self.setMinimumSize(1100, 700)
        self.setStyleSheet(STYLE)

        central = QWidget(objectName="central")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 12)
        root.setSpacing(12)

        # Header 
        root.addWidget(self._build_header())

        # Stat Cards 
        self._stat_layout = QHBoxLayout()
        self._stat_layout.setSpacing(12)
        self._lbl_transaksi = self._stat_card("Transaksi", "0", "#4F86C6")
        self._lbl_pendapatan = self._stat_card("Total Pendapatan", "Rp 0", "#3A9E6E")
        self._lbl_item = self._stat_card("Total Item Terjual", "0", "#F4845F")
        root.addLayout(self._stat_layout)

        #  Toolbar 
        root.addLayout(self._build_toolbar())

        #  Splitter: tabel + chart 
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        splitter.setStyleSheet("QSplitter::handle { background: #2E3250; width:2px; }")

        left = self._build_table_panel()
        right = self._build_chart_panel()
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 4)
        root.addWidget(splitter, stretch=1)

        self._status = QStatusBar()
        self.setStatusBar(self._status)

    def _build_header(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)

        title = QLabel("📊  Dashboard Penjualan")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #D0D6F9;")

        sub = QLabel("Data Transaksi 2024 · SQLite")
        sub.setStyleSheet("color: #5060A0; font-size: 12px;")

        v = QVBoxLayout()
        v.setSpacing(2)
        v.addWidget(title)
        v.addWidget(sub)
        h.addLayout(v)
        h.addStretch()
        return w

    def _stat_card(self, label: str, value: str, accent: str) -> QLabel:
        card = QFrame(objectName="statCard")
        card.setMinimumHeight(72)
        vl = QVBoxLayout(card)
        vl.setContentsMargins(16, 10, 16, 10)
        vl.setSpacing(4)

        lbl_label = QLabel(label)
        lbl_label.setStyleSheet(f"color: {accent}; font-size: 11px; font-weight: bold;")

        lbl_val = QLabel(value)
        lbl_val.setStyleSheet("color: #FFFFFF; font-size: 18px; font-weight: bold;")

        vl.addWidget(lbl_label)
        vl.addWidget(lbl_val)

        self._stat_layout.addWidget(card)
        return lbl_val   # return value label for update

    def _build_toolbar(self) -> QHBoxLayout:
        h = QHBoxLayout()
        h.setSpacing(8)

        lbl_kat = QLabel("Filter Kategori:")
        lbl_kat.setStyleSheet("color: #8090C0; font-size: 12px;")

        self._combo_kat = QComboBox()
        self._combo_kat.currentTextChanged.connect(self._on_filter_changed)

        lbl_chart = QLabel("Tipe Chart:")
        lbl_chart.setStyleSheet("color: #8090C0; font-size: 12px;")

        self._combo_chart = QComboBox()
        self._combo_chart.addItems(CHART_TYPES)
        self._combo_chart.currentTextChanged.connect(self._redraw_chart)

        btn_refresh = QPushButton("⟳  Refresh",  objectName="btnRefresh")
        btn_export  = QPushButton("↓  Export PNG", objectName="btnExport")
        btn_add     = QPushButton("＋  Tambah",   objectName="btnAdd")

        btn_refresh.clicked.connect(self._refresh)
        btn_export.clicked.connect(self._export_chart)
        btn_add.clicked.connect(self._add_row)

        for w in [lbl_kat, self._combo_kat, lbl_chart, self._combo_chart]:
            h.addWidget(w)
        h.addStretch()
        for btn in [btn_add, btn_refresh, btn_export]:
            h.addWidget(btn)

        return h

    def _build_table_panel(self) -> QWidget:
        panel = QFrame(objectName="panel")
        vl = QVBoxLayout(panel)
        vl.setContentsMargins(12, 12, 12, 12)
        vl.setSpacing(8)

        header = QLabel("Data Penjualan")
        header.setStyleSheet("color: #8090C0; font-size: 11px; font-weight: bold;")
        vl.addWidget(header)

        self._table = QTableWidget()
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels(
            ["ID", "Tanggal", "Kategori", "Produk", "Jumlah", "Harga (Rp)", "Total (Rp)"]
        )
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.setStyleSheet(
            "QTableWidget { alternate-background-color: #232840; }"
        )
        vl.addWidget(self._table, stretch=1)

        # row-action buttons
        bh = QHBoxLayout()
        bh.setSpacing(6)
        btn_edit   = QPushButton("✎  Edit",   objectName="btnEdit")
        btn_delete = QPushButton("✕  Hapus",  objectName="btnDelete")
        btn_edit.clicked.connect(self._edit_row)
        btn_delete.clicked.connect(self._delete_row)
        bh.addStretch()
        bh.addWidget(btn_edit)
        bh.addWidget(btn_delete)
        vl.addLayout(bh)

        return panel

    def _build_chart_panel(self) -> QWidget:
        panel = QFrame(objectName="panel")
        vl = QVBoxLayout(panel)
        vl.setContentsMargins(12, 12, 12, 12)
        vl.setSpacing(6)

        header = QLabel("Visualisasi")
        header.setStyleSheet("color: #8090C0; font-size: 11px; font-weight: bold;")
        vl.addWidget(header)

        self._chart = ChartWidget()
        vl.addWidget(self._chart, stretch=1)
        return panel

    # Data logic 

    def _refresh(self):
        # update filter combo
        current_kat = self._combo_kat.currentText() or "Semua"
        self._combo_kat.blockSignals(True)
        self._combo_kat.clear()
        self._combo_kat.addItems(get_categories())
        idx = self._combo_kat.findText(current_kat)
        self._combo_kat.setCurrentIndex(max(idx, 0))
        self._combo_kat.blockSignals(False)

        self._load_data()

    def _load_data(self):
        kat = self._combo_kat.currentText() or "Semua"
        self._current_data = fetch_all(kat)
        self._populate_table(self._current_data)
        self._redraw_chart()
        self._update_stats()
        self._status.showMessage(
            f"{len(self._current_data)} baris ditampilkan · "
            f"Filter: {kat} · {datetime.now().strftime('%H:%M:%S')}"
        )

    def _populate_table(self, data: list[dict]):
        self._table.setRowCount(len(data))
        for r, row in enumerate(data):
            def cell(val, align=Qt.AlignmentFlag.AlignLeft):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(align | Qt.AlignmentFlag.AlignVCenter)
                return item

            RIGHT = Qt.AlignmentFlag.AlignRight
            self._table.setItem(r, 0, cell(row["id"],       RIGHT))
            self._table.setItem(r, 1, cell(row["tanggal"]))
            self._table.setItem(r, 2, cell(row["kategori"]))
            self._table.setItem(r, 3, cell(row["produk"]))
            self._table.setItem(r, 4, cell(row["jumlah"],   RIGHT))
            self._table.setItem(r, 5, cell(f"{row['harga']:,.0f}", RIGHT))
            self._table.setItem(r, 6, cell(f"{row['total']:,.0f}", RIGHT))

    def _redraw_chart(self):
        chart_type = self._combo_chart.currentText()
        kat        = self._combo_kat.currentText() or "Semua"
        self._chart.plot(chart_type, self._current_data, kat)

    def _update_stats(self):
        summary = get_summary()
        self._lbl_transaksi.setText(f"{summary['total_transaksi']:,}")
        rp = summary["total_pendapatan"]
        if rp >= 1_000_000:
            self._lbl_pendapatan.setText(f"Rp {rp/1_000_000:,.1f} Jt")
        else:
            self._lbl_pendapatan.setText(f"Rp {rp:,.0f}")
        self._lbl_item.setText(f"{summary['total_item']:,}")

    def _on_filter_changed(self):
        self._load_data()

    # CRUD 

    def _add_row(self):
        dlg = CRUDDialog(self)
        if dlg.exec() == CRUDDialog.DialogCode.Accepted:
            v = dlg.get_values()
            insert_row(v["tanggal"], v["kategori"], v["produk"],
                       v["jumlah"], v["harga"], v["total"])
            self._refresh()
            self._status.showMessage("Data berhasil ditambahkan.")

    def _edit_row(self):
        row_idx = self._table.currentRow()
        if row_idx < 0:
            QMessageBox.information(self, "Info", "Pilih baris yang ingin diedit.")
            return
        row_data = self._current_data[row_idx]
        dlg = CRUDDialog(self, row_data)
        if dlg.exec() == CRUDDialog.DialogCode.Accepted:
            v = dlg.get_values()
            update_row(row_data["id"], v["tanggal"], v["kategori"], v["produk"],
                       v["jumlah"], v["harga"], v["total"])
            self._refresh()
            self._status.showMessage(f"Data ID {row_data['id']} berhasil diperbarui.")

    def _delete_row(self):
        row_idx = self._table.currentRow()
        if row_idx < 0:
            QMessageBox.information(self, "Info", "Pilih baris yang ingin dihapus.")
            return
        row_data = self._current_data[row_idx]
        confirm = QMessageBox.question(
            self, "Konfirmasi Hapus",
            f"Hapus transaksi ID {row_data['id']} – {row_data['produk']}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            delete_row(row_data["id"])
            self._refresh()
            self._status.showMessage(f"Data ID {row_data['id']} dihapus.")

    # Export 

    def _export_chart(self):
        default_name = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Chart", default_name, "PNG Image (*.png)"
        )
        if path:
            self._chart.export_png(path)
            self._status.showMessage(f"Chart berhasil diekspor ke: {path}")
            QMessageBox.information(self, "Export Berhasil",
                                    f"Chart disimpan di:\n{path}")
