"""
chart_widget.py
Widget Matplotlib yang tertanam di dalam PySide6.
Mendukung berbagai jenis chart dan ekspor ke PNG.
"""

from __future__ import annotations

import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Qt

PALETTE = [
    "#4F86C6", "#F4845F", "#62C370", "#F7C948",
    "#A06CD5", "#E05252", "#38A0A0", "#E8864A",
]

DARK_BG  = "#1E2132"
GRID_CLR = "#2E3250"
TEXT_CLR = "#D0D6F9"


def _apply_dark_style(ax, fig):
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.tick_params(colors=TEXT_CLR, labelsize=8)
    ax.xaxis.label.set_color(TEXT_CLR)
    ax.yaxis.label.set_color(TEXT_CLR)
    ax.title.set_color(TEXT_CLR)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_CLR)
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"Rp{x/1_000_000:.1f}Jt" if x >= 1_000_000 else f"Rp{x:,.0f}")
    )


class ChartWidget(QWidget):
    """Widget yang menampilkan satu Matplotlib figure di dalam PySide6."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._fig = Figure(figsize=(6, 4), dpi=100, facecolor=DARK_BG)
        self._canvas = FigureCanvas(self._fig)
        self._canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._canvas)

    # public API 

    def plot(self, chart_type: str, data: list[dict], kategori_filter: str = "Semua"):
        self._fig.clear()
        if not data:
            ax = self._fig.add_subplot(111)
            ax.text(0.5, 0.5, "Tidak ada data", ha="center", va="center",
                    color=TEXT_CLR, fontsize=14)
            ax.set_facecolor(DARK_BG)
            self._fig.patch.set_facecolor(DARK_BG)
            self._canvas.draw()
            return

        dispatch = {
            "Bar – Pendapatan per Kategori": self._bar_revenue_by_category,
            "Pie – Distribusi Kategori":     self._pie_category_distribution,
            "Line – Tren Penjualan Bulanan": self._line_monthly_trend,
            "Scatter – Jumlah vs Total":     self._scatter_qty_vs_total,
        }
        fn = dispatch.get(chart_type, self._bar_revenue_by_category)
        fn(data, kategori_filter)
        self._canvas.draw()

    def export_png(self, path: str):
        self._fig.savefig(path, dpi=150, bbox_inches="tight",
                          facecolor=DARK_BG)

    # chart implementations 

    def _bar_revenue_by_category(self, data, _filter):
        ax = self._fig.add_subplot(111)
        rev: dict[str, float] = defaultdict(float)
        for row in data:
            rev[row["kategori"]] += row["total"]

        cats   = sorted(rev.keys())
        values = [rev[c] for c in cats]
        colors = PALETTE[:len(cats)]

        bars = ax.bar(cats, values, color=colors, edgecolor="none", width=0.6)
        ax.bar_label(bars,
                     labels=[f"Rp{v/1_000_000:.1f}Jt" for v in values],
                     padding=4, color=TEXT_CLR, fontsize=8)

        ax.set_title("Pendapatan per Kategori", fontsize=12, fontweight="bold", pad=12)
        ax.set_xlabel("Kategori")
        ax.set_ylabel("Total Pendapatan")
        ax.grid(axis="y", color=GRID_CLR, linestyle="--", linewidth=0.7)
        ax.set_axisbelow(True)
        _apply_dark_style(ax, self._fig)
        self._fig.tight_layout()

    def _pie_category_distribution(self, data, _filter):
        ax = self._fig.add_subplot(111)
        count: dict[str, int] = defaultdict(int)
        for row in data:
            count[row["kategori"]] += row["jumlah"]

        labels = list(count.keys())
        sizes  = [count[l] for l in labels]
        colors = PALETTE[:len(labels)]

        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, autopct="%1.1f%%",
            colors=colors, startangle=140,
            pctdistance=0.82,
            wedgeprops=dict(edgecolor=DARK_BG, linewidth=2),
        )
        for t in texts:
            t.set_color(TEXT_CLR)
            t.set_fontsize(8)
        for at in autotexts:
            at.set_color("#FFFFFF")
            at.set_fontsize(7.5)
            at.set_fontweight("bold")

        ax.set_title("Distribusi Jumlah Item per Kategori",
                     fontsize=12, fontweight="bold", color=TEXT_CLR, pad=12)
        self._fig.patch.set_facecolor(DARK_BG)
        ax.set_facecolor(DARK_BG)
        self._fig.tight_layout()

    def _line_monthly_trend(self, data, _filter):
        ax = self._fig.add_subplot(111)

        monthly: dict[str, float] = defaultdict(float)
        for row in data:
            month_key = row["tanggal"][:7]   # "YYYY-MM"
            monthly[month_key] += row["total"]

        sorted_months = sorted(monthly.keys())
        values = [monthly[m] for m in sorted_months]
        short_labels = [m[5:] for m in sorted_months]  # "MM"

        ax.fill_between(range(len(values)), values,
                        alpha=0.25, color=PALETTE[0])
        ax.plot(range(len(values)), values, marker="o", color=PALETTE[0],
                linewidth=2, markersize=5)

        ax.set_xticks(range(len(short_labels)))
        ax.set_xticklabels(short_labels, rotation=45, ha="right", fontsize=7)
        ax.set_title("Tren Pendapatan Bulanan (2024)", fontsize=12,
                     fontweight="bold", pad=12)
        ax.set_xlabel("Bulan")
        ax.set_ylabel("Total Pendapatan")
        ax.grid(color=GRID_CLR, linestyle="--", linewidth=0.5)
        ax.set_axisbelow(True)
        _apply_dark_style(ax, self._fig)
        self._fig.tight_layout()

    def _scatter_qty_vs_total(self, data, _filter):
        ax = self._fig.add_subplot(111)

        cat_colors = {}
        cats = list({r["kategori"] for r in data})
        for i, c in enumerate(sorted(cats)):
            cat_colors[c] = PALETTE[i % len(PALETTE)]

        for row in data:
            ax.scatter(row["jumlah"], row["total"],
                       color=cat_colors[row["kategori"]],
                       alpha=0.75, s=50, edgecolors="none")

        # legend
        handles = [
            plt.Line2D([0], [0], marker="o", color="w",
                       markerfacecolor=cat_colors[c], markersize=8, label=c)
            for c in sorted(cats)
        ]
        leg = ax.legend(handles=handles, fontsize=7,
                        facecolor="#2A2F4A", edgecolor=GRID_CLR,
                        labelcolor=TEXT_CLR, loc="upper left")

        ax.set_title("Jumlah Item vs Total Pendapatan", fontsize=12,
                     fontweight="bold", pad=12)
        ax.set_xlabel("Jumlah Item")
        ax.set_ylabel("Total (Rp)")
        ax.grid(color=GRID_CLR, linestyle="--", linewidth=0.5)
        ax.set_axisbelow(True)
        _apply_dark_style(ax, self._fig)
        self._fig.tight_layout()
