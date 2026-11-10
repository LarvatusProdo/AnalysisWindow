"""Affichage des variables de l'utilisateur, regroupées par catégorie."""

import tkinter as tk
from collections.abc import Callable
from tkinter import font, ttk

from analyse_app.scrollbars import attach_scrollbars
from analyse_app.variable_inspector import Category, VariableInfo, group_by_category

COLUMNS = (("type", "Type", 80), ("value", "Valeur", 200))
NAME_COLUMN_WIDTH = 150
VALUE_COLUMN = "value"
CELL_PADDING = 16
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

    def __init__(self, parent: tk.Misc, on_reset: Callable[[], None]) -> None:
        """Construit le Treeview, ses barres de défilement et le bouton de réinitialisation.

        Args:
            parent: Widget parent.
            on_reset: Fonction appelée lors d'un clic sur « Réinitialiser les variables ».
        """
        super().__init__(parent, text="Variables", padding=4)
        tree_container = ttk.Frame(self)
        tree_container.pack(fill="both", expand=True)
        self._tree = ttk.Treeview(tree_container, columns=[name for name, _, _ in COLUMNS],
                                  show="tree headings")
        self._configure_columns()
        self._configure_colors()
        attach_scrollbars(tree_container, self._tree)
        ttk.Button(self, text="Réinitialiser les variables", command=on_reset).pack(
            anchor="e", pady=(4, 0))

    def _configure_columns(self) -> None:
        """Définit les en-têtes et largeurs ; la colonne de l'arbre porte le nom.

        Seule la colonne des valeurs s'élargit avec le panneau.
        """
        self._tree.heading("#0", text="Nom", anchor="w")
        self._tree.column("#0", width=NAME_COLUMN_WIDTH, anchor="w", stretch=False)
        for identifier, heading, width in COLUMNS:
            self._tree.heading(identifier, text=heading, anchor="w")
            self._tree.column(identifier, width=width, anchor="w",
                              stretch=identifier == VALUE_COLUMN)

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
        self._fit_value_column(variables)

    def _fit_value_column(self, variables: list[VariableInfo]) -> None:
        """Empêche la colonne des valeurs d'être plus étroite que son contenu.

        Si le panneau est trop étroit, la barre horizontale permet alors de lire
        les valeurs en entier.

        Args:
            variables: Variables affichées.
        """
        measure = font.nametofont("TkDefaultFont").measure
        needed = max((measure(variable.value) for variable in variables), default=0)
        self._tree.column(VALUE_COLUMN, minwidth=needed + CELL_PADDING)

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
