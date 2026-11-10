"""Exemple 1 : panneau d'analyse intégré dans un onglet de l'application.

`AnalysisPanel` est un `ttk.Frame` : il se place dans n'importe quel conteneur,
ici un `ttk.Notebook`.

Lancement depuis la racine du projet :

    python exemples/01_panneau_integre.py
"""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analyse_app import AnalysisPanel  # noqa: E402

TEMPERATURES = [18.5, 21.0, 19.75, 23.25]


def main() -> None:
    """Crée une fenêtre à deux onglets : données et analyse."""
    root = tk.Tk()
    root.title("Exemple 1 : panneau intégré")
    root.geometry("1000x600")
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)
    data_tab = ttk.Frame(notebook, padding=12)
    ttk.Label(data_tab, text=f"Températures : {TEMPERATURES}").pack(anchor="w")
    ttk.Label(data_tab, text="Essayer dans l'onglet Analyse : max(temperatures)").pack(anchor="w")
    notebook.add(data_tab, text="Données")
    notebook.add(AnalysisPanel(notebook, context={"temperatures": TEMPERATURES}), text="Analyse")
    root.mainloop()


if __name__ == "__main__":
    main()
