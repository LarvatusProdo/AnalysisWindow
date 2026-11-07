"""Zone de saisie du code Python."""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText


class EditorFrame(ttk.LabelFrame):
    """Éditeur de code accompagné du bouton d'exécution."""

    def __init__(self, parent: tk.Misc, on_execute: Callable[[], None]) -> None:
        """Construit l'éditeur et le bouton.

        Args:
            parent: Widget parent.
            on_execute: Fonction appelée lors d'un clic sur le bouton.
        """
        super().__init__(parent, text="Code Python", padding=4)
        self._text = ScrolledText(self, height=10, wrap="none", undo=True, font="TkFixedFont")
        self._text.pack(fill="both", expand=True)
        self._execute_button = ttk.Button(self, text="▶ Exécuter", command=on_execute)
        self._execute_button.pack(anchor="e", pady=(4, 0))

    def get_code(self) -> str:
        """Retourne le code actuellement saisi."""
        return self._text.get("1.0", "end-1c")
