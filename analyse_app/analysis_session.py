"""Session d'analyse indépendante de l'interface graphique."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from analyse_app.code_executor import CodeExecutor, ExecutionResult


@dataclass(frozen=True)
class HistoryEntry:
    """Script exécuté accompagné de son résultat.

    Attributes:
        code: Code source exécuté.
        result: Résultat de l'exécution.
    """

    code: str
    result: ExecutionResult


EntryListener = Callable[[HistoryEntry], None]


class AnalysisSession:
    """Exécute des scripts et conserve leur historique, sans afficher de fenêtre.

    Une même session peut être partagée avec une fenêtre ou un panneau d'analyse :
    à son ouverture, celui-ci affiche l'historique et les variables de la session.
    """

    def __init__(self, context: Mapping[str, Any] | None = None) -> None:
        """Initialise la session.

        Args:
            context: Objets, fonctions et méthodes de l'application principale
                à rendre accessibles aux scripts, indexés par leur nom.
        """
        self._executor = CodeExecutor(context)
        self._history: list[HistoryEntry] = []
        self._listeners: list[EntryListener] = []

    @property
    def namespace(self) -> dict[str, Any]:
        """Retourne l'espace de noms contenant les variables de l'utilisateur."""
        return self._executor.namespace

    @property
    def history(self) -> tuple[HistoryEntry, ...]:
        """Retourne les exécutions passées, de la plus ancienne à la plus récente."""
        return tuple(self._history)

    def run(self, code: str) -> ExecutionResult:
        """Exécute un script et l'ajoute à l'historique.

        Args:
            code: Code source Python à exécuter.

        Returns:
            Les sorties produites et l'éventuelle erreur.
        """
        result = self._executor.execute(code)
        entry = HistoryEntry(code, result)
        self._history.append(entry)
        for listener in list(self._listeners):
            listener(entry)
        return result

    def subscribe(self, listener: EntryListener) -> None:
        """Enregistre une fonction appelée après chaque exécution.

        Args:
            listener: Fonction recevant la nouvelle entrée d'historique.
        """
        self._listeners.append(listener)

    def unsubscribe(self, listener: EntryListener) -> None:
        """Retire une fonction enregistrée avec `subscribe`, si elle l'est.

        Args:
            listener: Fonction à retirer.
        """
        if listener in self._listeners:
            self._listeners.remove(listener)
