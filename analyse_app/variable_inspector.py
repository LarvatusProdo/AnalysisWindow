"""Extraction des variables utilisateur à partir d'un espace de noms."""

from dataclasses import dataclass
from types import ModuleType
from typing import Any

MAX_VALUE_LENGTH = 100
UNAVAILABLE_VALUE = "<valeur indisponible>"


@dataclass(frozen=True)
class VariableInfo:
    """Description d'une variable affichable.

    Attributes:
        name: Nom de la variable.
        type_name: Nom du type de la valeur.
        value: Représentation de la valeur sur une ligne, éventuellement tronquée.
    """

    name: str
    type_name: str
    value: str


def inspect_variables(namespace: dict[str, Any]) -> list[VariableInfo]:
    """Liste les variables utilisateur, triées par nom.

    Les noms commençant par un tiret bas et les modules importés sont ignorés.

    Args:
        namespace: Espace de noms à inspecter.

    Returns:
        La description de chaque variable retenue.
    """
    return [
        VariableInfo(name, type(value).__name__, _format_value(value))
        for name, value in sorted(namespace.items())
        if not name.startswith("_") and not isinstance(value, ModuleType)
    ]


def _format_value(value: Any) -> str:
    """Produit une représentation courte et sur une ligne d'une valeur.

    Args:
        value: Valeur à représenter.

    Returns:
        La représentation, tronquée à MAX_VALUE_LENGTH caractères.
    """
    try:
        text = repr(value).replace("\r", "").replace("\n", " ")
    except Exception:
        return UNAVAILABLE_VALUE
    if len(text) > MAX_VALUE_LENGTH:
        return text[:MAX_VALUE_LENGTH] + "…"
    return text
