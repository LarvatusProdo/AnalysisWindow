"""Exemple d'application principale utilisant la fenêtre d'analyse.

Une fois la fenêtre d'analyse ouverte, essayer par exemple ce script :

    add_measure(42)
    app.add_measure(58)
    print(compute_average(measures))
"""

import tkinter as tk
from tkinter import ttk

from analyse_app import AnalysisWindow


def compute_average(values: list[float]) -> float:
    """Calcule la moyenne d'une liste de nombres.

    Args:
        values: Nombres dont on veut la moyenne.

    Returns:
        La moyenne arrondie à 2 décimales.

    Raises:
        ValueError: Si la liste est vide.
    """
    if not values:
        raise ValueError("La liste est vide.")
    return round(sum(values) / len(values), 2)


class HostApplication(tk.Tk):
    """Application principale gérant une liste de mesures."""

    def __init__(self) -> None:
        """Construit l'interface de l'application."""
        super().__init__()
        self.title("Application principale")
        self.geometry("320x300")
        self.measures: list[float] = []
        self._analysis_window: AnalysisWindow | None = None
        self._listbox = tk.Listbox(self)
        self._listbox.pack(fill="both", expand=True, padx=8, pady=8)
        button = ttk.Button(self, text="Ouvrir l'analyse", command=self.open_analysis)
        button.pack(pady=(0, 8))

    def add_measure(self, value: float) -> None:
        """Ajoute une mesure à la liste et à l'affichage.

        Args:
            value: Valeur de la mesure.
        """
        self.measures.append(value)
        self._listbox.insert("end", str(value))

    def open_analysis(self) -> None:
        """Ouvre la fenêtre d'analyse, ou la ramène au premier plan si elle existe."""
        window = self._analysis_window
        if window is not None and window.winfo_exists():
            window.lift()
            return
        self._analysis_window = AnalysisWindow(self, context={
            "app": self,
            "add_measure": self.add_measure,
            "compute_average": compute_average,
            "measures": self.measures,
        })


if __name__ == "__main__":
    HostApplication().mainloop()
