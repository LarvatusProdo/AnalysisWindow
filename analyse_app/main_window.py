"""Fenêtre principale de l'application."""

import tkinter as tk
from tkinter import ttk

from analyse_app.code_executor import CodeExecutor
from analyse_app.editor_frame import EditorFrame
from analyse_app.history_frame import HistoryFrame
from analyse_app.variable_inspector import inspect_variables
from analyse_app.variables_frame import VariablesFrame

WINDOW_TITLE = "Fenêtre d'analyse"
WINDOW_SIZE = "1100x700"


class MainWindow(tk.Tk):
    """Assemble les zones de la fenêtre et les relie au moteur d'exécution."""

    def __init__(self) -> None:
        """Construit la fenêtre et ses zones."""
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        self._executor = CodeExecutor()
        self._build_layout()

    def _build_layout(self) -> None:
        """Dispose l'historique et l'éditeur à gauche, les variables à droite."""
        horizontal_pane = ttk.PanedWindow(self, orient="horizontal")
        horizontal_pane.pack(fill="both", expand=True, padx=6, pady=6)
        left_pane = ttk.PanedWindow(horizontal_pane, orient="vertical")
        self._history_frame = HistoryFrame(left_pane)
        self._editor_frame = EditorFrame(left_pane, self._execute_code)
        self._variables_frame = VariablesFrame(horizontal_pane)
        left_pane.add(self._history_frame, weight=3)
        left_pane.add(self._editor_frame, weight=2)
        horizontal_pane.add(left_pane, weight=3)
        horizontal_pane.add(self._variables_frame, weight=1)

    def _execute_code(self) -> None:
        """Exécute le code saisi puis met à jour l'historique et les variables."""
        code = self._editor_frame.get_code()
        if not code.strip():
            return
        result = self._executor.execute(code)
        self._history_frame.add_entry(code, result)
        self._variables_frame.refresh(inspect_variables(self._executor.namespace))
