"""
crud_dialog.py
Dialog untuk menambah dan mengedit data penjualan.
"""

from __future__ import annotations
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox,
    QSpinBox, QDoubleSpinBox, QDialogButtonBox,
    QLabel, QVBoxLayout, QHBoxLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

KATEGORI_LIST = ["Elektronik", "Pakaian", "Makanan", "Olahraga", "Rumah Tangga"]

STYLE = """
QDialog {
    background: #1E2132;
    color: #D0D6F9;
}
QLabel {
    color: #A0AACF;
    font-size: 12px;
}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background: #252A40;
    border: 1px solid #3A4170;
    border-radius: 6px;
    color: #D0D6F9;
    padding: 6px 10px;
    font-size: 12px;
    min-height: 28px;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #4F86C6;
}
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background: #252A40;
    color: #D0D6F9;
    selection-background-color: #4F86C6;
}
QPushButton {
    background: #4F86C6;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 22px;
    font-size: 12px;
    font-weight: bold;
}
QPushButton:hover { background: #5F96D6; }
QPushButton[text="Cancel"] { background: #3A4170; }
QPushButton[text="Cancel"]:hover { background: #4A5190; }
"""


class CRUDDialog(QDialog):
    def __init__(self, parent=None, row_data: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Tambah Data" if row_data is None else "Edit Data")
        self.setMinimumWidth(380)
        self.setStyleSheet(STYLE)
        self._build_ui(row_data)

    def _build_ui(self, row_data):
        title = QLabel("Tambah Transaksi" if row_data is None else "Edit Transaksi")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #D0D6F9; margin-bottom: 8px;")

        self.f_tanggal  = QLineEdit()
        self.f_tanggal.setPlaceholderText("YYYY-MM-DD")

        self.f_kategori = QComboBox()
        self.f_kategori.addItems(KATEGORI_LIST)

        self.f_produk   = QLineEdit()
        self.f_produk.setPlaceholderText("Nama produk")

        self.f_jumlah   = QSpinBox()
        self.f_jumlah.setRange(1, 9999)

        self.f_harga    = QDoubleSpinBox()
        self.f_harga.setRange(0, 999_999_999)
        self.f_harga.setDecimals(0)
        self.f_harga.setSingleStep(1000)
        self.f_harga.setPrefix("Rp ")

        self.f_total    = QDoubleSpinBox()
        self.f_total.setRange(0, 999_999_999_999)
        self.f_total.setDecimals(0)
        self.f_total.setSingleStep(10000)
        self.f_total.setPrefix("Rp ")

        # auto-compute total
        self.f_jumlah.valueChanged.connect(self._recalc_total)
        self.f_harga.valueChanged.connect(self._recalc_total)

        form = QFormLayout()
        form.setSpacing(10)
        form.addRow("Tanggal:",  self.f_tanggal)
        form.addRow("Kategori:", self.f_kategori)
        form.addRow("Produk:",   self.f_produk)
        form.addRow("Jumlah:",   self.f_jumlah)
        form.addRow("Harga:",    self.f_harga)
        form.addRow("Total:",    self.f_total)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addLayout(form)
        layout.addWidget(buttons)

        if row_data:
            self.f_tanggal.setText(row_data.get("tanggal", ""))
            idx = self.f_kategori.findText(row_data.get("kategori", ""))
            if idx >= 0:
                self.f_kategori.setCurrentIndex(idx)
            self.f_produk.setText(row_data.get("produk", ""))
            self.f_jumlah.setValue(row_data.get("jumlah", 1))
            self.f_harga.setValue(row_data.get("harga", 0))
            self.f_total.setValue(row_data.get("total", 0))

    def _recalc_total(self):
        self.f_total.setValue(self.f_jumlah.value() * self.f_harga.value())

    def get_values(self) -> dict:
        return {
            "tanggal":  self.f_tanggal.text().strip(),
            "kategori": self.f_kategori.currentText(),
            "produk":   self.f_produk.text().strip(),
            "jumlah":   self.f_jumlah.value(),
            "harga":    self.f_harga.value(),
            "total":    self.f_total.value(),
        }
