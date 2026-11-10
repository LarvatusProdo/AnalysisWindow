"""Exemple 4 : exécuter des scripts sans afficher de fenêtre, puis vérifier.

Les scripts du dossier `scripts/` sont exécutés dans une `AnalysisSession` et leurs
résultats sont affichés dans la console. La fenêtre d'analyse s'ouvre ensuite et
présente tout l'historique et les variables.

Lancement depuis la racine du projet :

    python exemples/04_sans_interface.py                 # console puis fenêtre
    python exemples/04_sans_interface.py --sans-fenetre  # console uniquement
"""

import sys
import tkinter as tk
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analyse_app import AnalysisPanel, AnalysisSession, ExecutionResult  # noqa: E402

SCRIPTS_DIR = Path(__file__).resolve().parent / "scripts"
SCRIPT_NAMES = ("hello.py", "statistiques.py", "erreur.py")
NO_WINDOW_OPTION = "--sans-fenetre"


def build_session() -> AnalysisSession:
    """Crée une session dont le contexte simule une application de mesures.

    Returns:
        La session, avec `measures` et `add_measure` dans son contexte.
    """
    measures: list[float] = []
    return AnalysisSession(context={"measures": measures, "add_measure": measures.append})


def report(title: str, result: ExecutionResult) -> None:
    """Affiche dans la console le résultat d'une exécution.

    Args:
        title: Nom de l'exécution.
        result: Résultat à afficher.
    """
    status = "succès" if result.succeeded else "ÉCHEC"
    print(f"=== {title} : {status}")
    print(result.output, end="")
    if result.error:
        print(result.error.strip().splitlines()[-1])


def show_window(session: AnalysisSession) -> None:
    """Ouvre la fenêtre d'analyse sur une session existante.

    Args:
        session: Session dont l'historique et les variables sont affichés.
    """
    root = tk.Tk()
    root.title("Exemple 4 : vérification après exécution")
    root.geometry("1100x700")
    AnalysisPanel(root, session=session).pack(fill="both", expand=True)
    root.mainloop()


def main() -> None:
    """Exécute du code puis des fichiers, et affiche éventuellement la fenêtre."""
    session = build_session()
    report("Code direct", session.run("answer = 6 * 7\nanswer"))
    for name in SCRIPT_NAMES:
        report(name, session.run_file(SCRIPTS_DIR / name))
    print(f"\n{len(session.history)} exécutions dans l'historique.")
    print(f"Mesures : {session.namespace['measures']}")
    if NO_WINDOW_OPTION not in sys.argv:
        show_window(session)


if __name__ == "__main__":
    main()
