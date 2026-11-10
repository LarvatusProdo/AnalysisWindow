"""Historique des scripts exécutés et de leurs résultats."""

import tkinter as tk
from tkinter import ttk

from analyse_app.code_executor import ExecutionResult
from analyse_app.scrollbars import attach_scrollbars

CODE_COLOR = "#1f4e9e"
ERROR_COLOR = "#c62828"
SOURCE_COLOR = "#6a737d"


class HistoryFrame(ttk.LabelFrame):
    """Affichage en lecture seule des exécutions successives."""

    def __init__(self, parent: tk.Misc) -> None:
        """Construit la zone d'historique.

        Args:
            parent: Widget parent.
        """
        super().__init__(parent, text="Historique", padding=4)
        self._text = tk.Text(self, height=15, wrap="none", state="disabled",
                             font="TkFixedFont")
        self._text.tag_configure("code", foreground=CODE_COLOR)
        self._text.tag_configure("error", foreground=ERROR_COLOR)
        self._text.tag_configure("source", foreground=SOURCE_COLOR)
        attach_scrollbars(self, self._text)

    def add_entry(self, code: str, result: ExecutionResult, source: str | None = None) -> None:
        """Ajoute un script et son résultat à la fin de l'historique.

        Args:
            code: Code source exécuté.
            result: Résultat de l'exécution.
            source: Chemin du fichier exécuté, affiché avant le code s'il est fourni.
        """
        self._text.configure(state="normal")
        self._insert_block(f"# Fichier : {source}" if source else "", "source")
        self._insert_block(_format_code(code), "code")
        self._insert_block(result.output, "output")
        self._insert_block(result.error or "", "error")
        self._text.insert("end", "\n")
        self._text.configure(state="disabled")
        self._text.see("end")

    def _insert_block(self, content: str, tag: str) -> None:
        """Insère un bloc de texte s'il n'est pas vide.

        Args:
            content: Texte à insérer.
            tag: Style à appliquer au texte.
        """
        if content:
            self._text.insert("end", content.rstrip("\n") + "\n", tag)


def _format_code(code: str) -> str:
    """Préfixe le code à la manière d'une console Python.

    Args:
        code: Code source exécuté.

    Returns:
        Le code avec des invites `>>>` puis `...` en début de ligne.
    """
    first_line, *other_lines = code.strip("\n").split("\n")
    return "\n".join([f">>> {first_line}", *(f"... {line}" for line in other_lines)])
