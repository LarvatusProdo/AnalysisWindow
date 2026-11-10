"""Panneau d'analyse intégrable dans n'importe quelle interface Tkinter."""

import tkinter as tk
from collections.abc import Mapping
from tkinter import ttk
from typing import Any

from analyse_app.analysis_session import AnalysisSession, HistoryEntry
from analyse_app.editor_frame import EditorFrame
from analyse_app.history_frame import HistoryFrame
from analyse_app.variable_inspector import inspect_variables
from analyse_app.variables_frame import VariablesFrame


class AnalysisPanel(ttk.Frame):
    """Affiche une session d'analyse : historique, éditeur et variables."""

    def __init__(self, parent: tk.Misc, context: Mapping[str, Any] | None = None,
                 session: AnalysisSession | None = None) -> None:
        """Construit le panneau.

        Args:
            parent: Widget parent.
            context: Objets, fonctions et méthodes de l'application principale
                à rendre accessibles aux scripts, indexés par leur nom. Ignoré
                lorsqu'une session est fournie.
            session: Session existante à afficher, avec son historique et ses
                variables. Si absente, une nouvelle session est créée.

        Raises:
            ValueError: Si `context` et `session` sont fournis ensemble.
        """
        super().__init__(parent)
        self._session = _resolve_session(context, session)
        self._build_layout()
        for entry in self._session.history:
            self._history_frame.add_entry(entry.code, entry.result, entry.source)
        self._refresh_variables()
        self._session.subscribe(self._on_new_entry)
        self.bind("<Destroy>", self._on_destroy, add="+")

    @property
    def session(self) -> AnalysisSession:
        """Retourne la session affichée par le panneau."""
        return self._session

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
        """Exécute le code saisi ; l'affichage est mis à jour par `_on_new_entry`."""
        code = self._editor_frame.get_code()
        if code.strip():
            self._session.run(code)

    def _on_new_entry(self, entry: HistoryEntry) -> None:
        """Affiche une exécution, qu'elle vienne de l'éditeur ou de l'application.

        Args:
            entry: Nouvelle entrée de l'historique de la session.
        """
        self._history_frame.add_entry(entry.code, entry.result, entry.source)
        self._refresh_variables()

    def _on_destroy(self, event: tk.Event) -> None:
        """Cesse de suivre la session lorsque le panneau est détruit.

        Args:
            event: Événement de destruction, propagé aussi par les widgets enfants.
        """
        if event.widget is self:
            self._session.unsubscribe(self._on_new_entry)

    def _refresh_variables(self) -> None:
        """Met à jour l'affichage des variables."""
        self._variables_frame.refresh(inspect_variables(self._session.namespace))


def _resolve_session(context: Mapping[str, Any] | None,
                     session: AnalysisSession | None) -> AnalysisSession:
    """Retourne la session fournie, ou en crée une à partir du contexte.

    Args:
        context: Contexte d'une nouvelle session.
        session: Session existante.

    Returns:
        La session à afficher.

    Raises:
        ValueError: Si `context` et `session` sont fournis ensemble.
    """
    if session is None:
        return AnalysisSession(context)
    if context is not None:
        raise ValueError("Fournir soit context, soit session, pas les deux.")
    return session
