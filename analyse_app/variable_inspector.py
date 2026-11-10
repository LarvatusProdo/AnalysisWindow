"""Extraction et classement des variables utilisateur à partir d'un espace de noms."""

import inspect
from collections.abc import Collection
from dataclasses import dataclass
from enum import Enum
from types import ModuleType
from typing import Any

MAX_VALUE_LENGTH = 100
UNAVAILABLE_VALUE = "<valeur indisponible>"


class Category(Enum):
    """Catégorie d'affichage d'une variable, dans l'ordre de présentation."""

    FUNCTION = "Fonctions"
    CLASS = "Classes"
    NUMBER = "Nombres"
    TEXT = "Textes"
    COLLECTION = "Collections"
    OBJECT = "Objets"


@dataclass(frozen=True)
class VariableInfo:
    """Description d'une variable affichable.

    Attributes:
        name: Nom de la variable.
        type_name: Nom du type de la valeur.
        value: Représentation de la valeur sur une ligne, éventuellement tronquée.
        category: Catégorie dans laquelle la variable est rangée.
    """

    name: str
    type_name: str
    value: str
    category: Category


def inspect_variables(namespace: dict[str, Any]) -> list[VariableInfo]:
    """Liste les variables utilisateur, triées par nom.

    Les noms commençant par un tiret bas et les modules importés sont ignorés.

    Args:
        namespace: Espace de noms à inspecter.

    Returns:
        La description de chaque variable retenue.
    """
    variables = []
    for name, value in sorted(namespace.items()):
        if name.startswith("_") or isinstance(value, ModuleType):
            continue
        category = classify(value)
        variables.append(VariableInfo(name, type(value).__name__,
                                      _format_value(value, category), category))
    return variables


def group_by_category(variables: list[VariableInfo]) -> dict[Category, list[VariableInfo]]:
    """Regroupe les variables par catégorie, en omettant les catégories vides.

    Args:
        variables: Variables à regrouper.

    Returns:
        Les variables de chaque catégorie, dans l'ordre de `Category`.
    """
    groups: dict[Category, list[VariableInfo]] = {category: [] for category in Category}
    for variable in variables:
        groups[variable.category].append(variable)
    return {category: members for category, members in groups.items() if members}


def classify(value: Any) -> Category:
    """Détermine la catégorie d'une valeur.

    Args:
        value: Valeur à classer.

    Returns:
        La catégorie de la valeur ; `Category.OBJECT` par défaut.
    """
    if isinstance(value, type):
        return Category.CLASS
    if callable(value):
        return Category.FUNCTION
    if isinstance(value, (int, float, complex)):
        return Category.NUMBER
    if isinstance(value, (str, bytes, bytearray)):
        return Category.TEXT
    if isinstance(value, Collection):
        return Category.COLLECTION
    return Category.OBJECT


def _format_value(value: Any, category: Category) -> str:
    """Produit une représentation courte et sur une ligne d'une valeur.

    Les fonctions sont représentées par leur signature plutôt que par leur adresse.

    Args:
        value: Valeur à représenter.
        category: Catégorie de la valeur.

    Returns:
        La représentation, tronquée à MAX_VALUE_LENGTH caractères.
    """
    try:
        if category is Category.FUNCTION:
            text = _describe_callable(value)
        else:
            text = repr(value).replace("\r", "").replace("\n", " ")
    except Exception:
        return UNAVAILABLE_VALUE
    if len(text) > MAX_VALUE_LENGTH:
        return text[:MAX_VALUE_LENGTH] + "…"
    return text


def _describe_callable(function: Any) -> str:
    """Décrit une fonction par son nom et sa signature.

    Args:
        function: Fonction, méthode ou objet appelable.

    Returns:
        Par exemple `compute_average(values: list[float]) -> float`, ou la
        représentation habituelle si la signature n'est pas disponible.
    """
    name = getattr(function, "__name__", type(function).__name__)
    try:
        return f"{name}{inspect.signature(function)}"
    except (TypeError, ValueError):
        return repr(function)
