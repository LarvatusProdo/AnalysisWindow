"""Affichage des variables de l'utilisateur, regroupées par catégorie."""

import tkinter as tk
from tkinter import font, ttk

from analyse_app.variable_inspector import Category, VariableInfo, group_by_category

COLUMNS = (("type", "Type", 80), ("value", "Valeur", 200))
NAME_COLUMN_WIDTH = 150
CATEGORY_COLORS = {
    Category.FUNCTION: "#7b3fbf",
    Category.CLASS: "#b05a00",
    Category.NUMBER: "#1a5fb4",
    Category.TEXT: "#2e7d32",
    Category.COLLECTION: "#00838f",
    Category.OBJECT: "#5f6368",
}
HEADER_SUFFIX = "_header"


class VariablesFrame(ttk.LabelFrame):
    """Arborescence des variables : un groupe coloré par catégorie."""

    def __init__(self, parent: tk.Misc) -> None:
        """Construit le Treeview et sa barre de défilement.

        Args:
            parent: Widget parent.
        """
        super().__init__(parent, text="Variables", padding=4)
        self._tree = ttk.Treeview(self, columns=[name for name, _, _ in COLUMNS],
                                  show="tree headings")
        self._configure_columns()
        self._configure_colors()
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self._tree.pack(side="left", fill="both", expand=True)

    def _configure_columns(self) -> None:
        """Définit les en-têtes et largeurs ; la colonne de l'arbre porte le nom."""
        self._tree.heading("#0", text="Nom", anchor="w")
        self._tree.column("#0", width=NAME_COLUMN_WIDTH, anchor="w")
        for identifier, heading, width in COLUMNS:
            self._tree.heading(identifier, text=heading, anchor="w")
            self._tree.column(identifier, width=width, anchor="w")

    def _configure_colors(self) -> None:
        """Associe une couleur à chaque catégorie ; les groupes sont en gras."""
        self._header_font = font.nametofont("TkDefaultFont").copy()
        self._header_font.configure(weight="bold")
        for category, color in CATEGORY_COLORS.items():
            self._tree.tag_configure(category.name, foreground=color)
            self._tree.tag_configure(category.name + HEADER_SUFFIX, foreground=color,
                                     font=self._header_font)

    def refresh(self, variables: list[VariableInfo]) -> None:
        """Remplace le contenu du Treeview en conservant les groupes repliés.

        Args:
            variables: Variables à afficher.
        """
        collapsed = {item for item in self._tree.get_children()
                     if not self._tree.item(item, "open")}
        self._tree.delete(*self._tree.get_children())
        for category, members in group_by_category(variables).items():
            self._insert_category(category, members, category.name not in collapsed)

    def _insert_category(self, category: Category, members: list[VariableInfo],
                         is_open: bool) -> None:
        """Insère un groupe et ses variables.

        Args:
            category: Catégorie du groupe.
            members: Variables de cette catégorie.
            is_open: Indique si le groupe doit être déplié.
        """
        group = self._tree.insert("", "end", iid=category.name, open=is_open,
                                  text=f"{category.value} ({len(members)})",
                                  tags=(category.name + HEADER_SUFFIX,))
        for variable in members:
            self._tree.insert(group, "end", text=variable.name,
                              values=(variable.type_name, variable.value),
                              tags=(category.name,))
