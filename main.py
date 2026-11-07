"""Point d'entrée de la fenêtre d'analyse."""

from analyse_app.main_window import MainWindow


def main() -> None:
    """Lance la fenêtre d'analyse."""
    MainWindow().mainloop()


if __name__ == "__main__":
    main()
