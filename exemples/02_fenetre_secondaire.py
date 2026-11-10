"""Exemple 2 : fenêtre d'analyse secondaire ouverte par un bouton.

`AnalysisWindow` est un `tk.Toplevel`. Sans session partagée, chaque fenêtre
repart d'un historique vide.

Lancement depuis la racine du projet :

    python exemples/02_fenetre_secondaire.py
"""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analyse_app import AnalysisWindow  # noqa: E402


def greet(name: str) -> str:
    """Construit un message de bienvenue.

    Args:
        name: Nom de la personne à saluer.

    Returns:
        Le message de bienvenue.
    """
    return f"Bonjour {name} !"


def main() -> None:
    """Crée une petite fenêtre avec un bouton qui ouvre l'analyse."""
    root = tk.Tk()
    root.title("Exemple 2 : fenêtre secondaire")
    root.geometry("320x120")
    ttk.Label(root, text="Essayer dans l'analyse : greet(\"Alice\")").pack(pady=12)
    ttk.Button(root, text="Ouvrir l'analyse",
               command=lambda: AnalysisWindow(root, context={"greet": greet})).pack()
    root.mainloop()


if __name__ == "__main__":
    main()
