"""Ajout de barres de défilement verticale et horizontale à un widget."""

import tkinter as tk
from tkinter import ttk


def attach_scrollbars(container: tk.Misc, widget: tk.Text | ttk.Treeview) -> None:
    """Place un widget dans son conteneur avec deux barres de défilement.

    Le conteneur doit être réservé au widget et à ses barres, car il est géré
    avec `grid`.

    Args:
        container: Cadre parent du widget.
        widget: Widget défilable horizontalement et verticalement.
    """
    vertical = ttk.Scrollbar(container, orient="vertical", command=widget.yview)
    horizontal = ttk.Scrollbar(container, orient="horizontal", command=widget.xview)
    widget.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
    widget.grid(row=0, column=0, sticky="nsew")
    vertical.grid(row=0, column=1, sticky="ns")
    horizontal.grid(row=1, column=0, sticky="ew")
    container.rowconfigure(0, weight=1)
    container.columnconfigure(0, weight=1)
