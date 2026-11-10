"""Session d'analyse indépendante de l'interface graphique."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from analyse_app.code_executor import CodeExecutor, ExecutionResult


@dataclass(frozen=True)
class HistoryEntry:
    """Script exécuté accompagné de son résultat.

    Attributes:
        code: Code source exécuté.
        result: Résultat de l'exécution.
        source: Chemin du fichier exécuté, ou None si le code a été fourni directement.
    """

    code: str
    result: ExecutionResult
    source: str | None = None


class EventKind(Enum):
    """Nature d'une modification de la session."""

    ENTRY_ADDED = "entrée ajoutée"
    HISTORY_CLEARED = "historique effacé"
    NAMESPACE_RESET = "variables réinitialisées"


@dataclass(frozen=True)
class SessionEvent:
    """Modification de la session transmise aux abonnés.

    Attributes:
        kind: Nature de la modification.
        entry: Nouvelle entrée d'historique pour `EventKind.ENTRY_ADDED`, sinon None.
    """

    kind: EventKind
    entry: HistoryEntry | None = None


SessionListener = Callable[[SessionEvent], None]


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
        self._listeners: list[SessionListener] = []

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
        return self._record(HistoryEntry(code, self._executor.execute(code)))

    def run_file(self, path: str | Path, encoding: str = "utf-8-sig") -> ExecutionResult:
        """Exécute le contenu d'un fichier et l'ajoute à l'historique.

        Args:
            path: Chemin du fichier Python à exécuter.
            encoding: Encodage du fichier ; la valeur par défaut accepte l'UTF-8
                avec ou sans BOM.

        Returns:
            Les sorties produites et l'éventuelle erreur du script.

        Raises:
            OSError: Si le fichier ne peut pas être lu (introuvable, droits…).
            UnicodeDecodeError: Si le fichier n'est pas dans l'encodage indiqué.
        """
        code = Path(path).read_text(encoding=encoding)
        result = self._executor.execute(code)
        return self._record(HistoryEntry(code, result, str(path)))

    def _record(self, entry: HistoryEntry) -> ExecutionResult:
        """Ajoute une entrée à l'historique et prévient les abonnés.

        Args:
            entry: Exécution à enregistrer.

        Returns:
            Le résultat de l'exécution enregistrée.
        """
        self._history.append(entry)
        self._notify(SessionEvent(EventKind.ENTRY_ADDED, entry))
        return entry.result

    def clear_history(self) -> None:
        """Efface l'historique ; les variables sont conservées."""
        self._history.clear()
        self._notify(SessionEvent(EventKind.HISTORY_CLEARED))

    def reset_namespace(self) -> None:
        """Supprime les variables créées par les scripts et rétablit le contexte initial.

        L'historique est conservé. Les objets du contexte gardent leurs modifications
        internes : une liste de l'application à laquelle un script a ajouté des éléments
        n'est pas vidée.
        """
        self._executor.reset()
        self._notify(SessionEvent(EventKind.NAMESPACE_RESET))

    def subscribe(self, listener: SessionListener) -> None:
        """Enregistre une fonction appelée après chaque modification de la session.

        Args:
            listener: Fonction recevant l'événement décrivant la modification.
        """
        self._listeners.append(listener)

    def _notify(self, event: SessionEvent) -> None:
        """Transmet un événement à tous les abonnés.

        Args:
            event: Modification à signaler.
        """
        for listener in list(self._listeners):
            listener(event)

    def unsubscribe(self, listener: SessionListener) -> None:
        """Retire une fonction enregistrée avec `subscribe`, si elle l'est.

        Args:
            listener: Fonction à retirer.
        """
        if listener in self._listeners:
            self._listeners.remove(listener)
