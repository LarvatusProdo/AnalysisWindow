"""Lancement autonome de la fenêtre d'analyse."""

import tkinter as tk

from analyse_app import AnalysisPanel

WINDOW_TITLE = "Fenêtre d'analyse"
WINDOW_SIZE = "1100x700"


def main() -> None:
    """Lance la fenêtre d'analyse sans application principale."""
    root = tk.Tk()
    root.title(WINDOW_TITLE)
    root.geometry(WINDOW_SIZE)
    AnalysisPanel(root).pack(fill="both", expand=True)
    root.mainloop()


if __name__ == "__main__":
    main()
