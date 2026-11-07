"""Affichage des variables de l'utilisateur."""

import tkinter as tk
from tkinter import ttk

from analyse_app.variable_inspector import VariableInfo

COLUMNS = (("name", "Nom", 100), ("type", "Type", 80), ("value", "Valeur", 180))


class VariablesFrame(ttk.LabelFrame):
    """Tableau de type Treeview listant les variables."""

    def __init__(self, parent: tk.Misc) -> None:
        """Construit le Treeview et sa barre de défilement.

        Args:
            parent: Widget parent.
        """
        super().__init__(parent, text="Variables", padding=4)
        identifiers = [identifier for identifier, _, _ in COLUMNS]
        self._tree = ttk.Treeview(self, columns=identifiers, show="headings")
        for identifier, heading, width in COLUMNS:
            self._tree.heading(identifier, text=heading, anchor="w")
            self._tree.column(identifier, width=width, anchor="w")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self._tree.pack(side="left", fill="both", expand=True)

    def refresh(self, variables: list[VariableInfo]) -> None:
        """Remplace le contenu du Treeview.

        Args:
            variables: Variables à afficher.
        """
        self._tree.delete(*self._tree.get_children())
        for variable in variables:
            values = (variable.name, variable.type_name, variable.value)
            self._tree.insert("", "end", values=values)
