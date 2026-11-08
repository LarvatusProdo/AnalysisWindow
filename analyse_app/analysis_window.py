"""Fenêtre secondaire contenant le panneau d'analyse."""

import tkinter as tk
from collections.abc import Mapping
from typing import Any

from analyse_app.analysis_panel import AnalysisPanel

WINDOW_TITLE = "Fenêtre d'analyse"
WINDOW_SIZE = "1100x700"


class AnalysisWindow(tk.Toplevel):
    """Fenêtre d'analyse ouverte depuis une application Tkinter existante."""

    def __init__(self, parent: tk.Misc, context: Mapping[str, Any] | None = None) -> None:
        """Construit la fenêtre.

        Args:
            parent: Widget de l'application principale.
            context: Objets, fonctions et méthodes de l'application principale
                à rendre accessibles aux scripts, indexés par leur nom.
        """
        super().__init__(parent)
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        self.panel = AnalysisPanel(self, context)
        self.panel.pack(fill="both", expand=True)
