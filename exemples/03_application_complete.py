"""Exemple 3 : application hôte partageant une session avec la fenêtre d'analyse.

L'application crée une `AnalysisSession` au démarrage :

- « Calculer la moyenne (sans fenêtre) » exécute un script sans rien afficher ;
- « Exécuter un fichier… » exécute un fichier choisi, par exemple dans `scripts/` ;
- « Ouvrir l'analyse » affiche l'historique de tout ce qui a été exécuté.

Une fois la fenêtre d'analyse ouverte, essayer par exemple ce script :

    add_measure(42)
    app.add_measure(58)
    print(compute_average(measures))

Lancement depuis la racine du projet :

    python exemples/03_application_complete.py
"""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analyse_app import AnalysisSession, AnalysisWindow, ExecutionResult  # noqa: E402

SCRIPTS_DIR = Path(__file__).resolve().parent / "scripts"
AVERAGE_SCRIPT = "add_measure(len(measures) * 10)\ncompute_average(measures)"


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
        """Construit l'interface de l'application et sa session d'analyse."""
        super().__init__()
        self.title("Exemple 3 : application complète")
        self.geometry("340x380")
        self.measures: list[float] = []
        self._analysis_window: AnalysisWindow | None = None
        self.analysis_session = AnalysisSession(context={
            "app": self,
            "add_measure": self.add_measure,
            "compute_average": compute_average,
            "measures": self.measures,
        })
        self._build_widgets()

    def _build_widgets(self) -> None:
        """Crée la liste des mesures, les boutons et la ligne d'état."""
        self._listbox = tk.Listbox(self)
        self._listbox.pack(fill="both", expand=True, padx=8, pady=8)
        buttons = (("Calculer la moyenne (sans fenêtre)", self.run_average_script),
                   ("Exécuter un fichier…", self.run_script_file),
                   ("Ouvrir l'analyse", self.open_analysis))
        for text, command in buttons:
            ttk.Button(self, text=text, command=command).pack(pady=(0, 4))
        self._status = ttk.Label(self, text="")
        self._status.pack(pady=8)

    def add_measure(self, value: float) -> None:
        """Ajoute une mesure à la liste et à l'affichage.

        Args:
            value: Valeur de la mesure.
        """
        self.measures.append(value)
        self._listbox.insert("end", str(value))

    def run_average_script(self) -> None:
        """Exécute un script dans la session sans ouvrir la fenêtre d'analyse."""
        self._show_status("Moyenne", self.analysis_session.run(AVERAGE_SCRIPT))

    def run_script_file(self) -> None:
        """Demande un fichier Python et l'exécute sans ouvrir la fenêtre d'analyse."""
        path = filedialog.askopenfilename(parent=self, initialdir=SCRIPTS_DIR,
                                          filetypes=[("Scripts Python", "*.py")])
        if not path:
            return
        try:
            result = self.analysis_session.run_file(path)
        except (OSError, UnicodeDecodeError) as error:
            messagebox.showerror("Lecture impossible", str(error), parent=self)
            return
        self._show_status(Path(path).name, result)

    def _show_status(self, label: str, result: ExecutionResult) -> None:
        """Affiche sous les boutons le résumé d'une exécution.

        Args:
            label: Nom de l'exécution.
            result: Résultat de l'exécution.
        """
        if not result.succeeded:
            self._status.configure(text=f"{label} : échec, voir l'historique.")
            return
        lines = result.output.strip().splitlines()
        self._status.configure(text=f"{label} : {lines[-1] if lines else 'terminé'}")

    def open_analysis(self) -> None:
        """Ouvre la fenêtre d'analyse, ou la ramène au premier plan si elle existe."""
        window = self._analysis_window
        if window is not None and window.winfo_exists():
            window.lift()
            return
        self._analysis_window = AnalysisWindow(self, session=self.analysis_session)


if __name__ == "__main__":
    HostApplication().mainloop()
