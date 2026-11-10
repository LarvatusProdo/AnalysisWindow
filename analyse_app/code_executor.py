"""Exécution du code Python saisi par l'utilisateur."""

import ast
import contextlib
import io
import traceback
from collections.abc import Mapping
from dataclasses import dataclass
from types import TracebackType
from typing import Any

SCRIPT_FILENAME = "<script>"


@dataclass(frozen=True)
class ExecutionResult:
    """Résultat d'une exécution.

    Attributes:
        output: Texte écrit sur stdout et stderr, suivi de la valeur de la
            dernière expression si le script se termine par une expression.
        error: Traceback formaté si l'exécution a échoué, sinon None.
    """

    output: str
    error: str | None = None

    @property
    def succeeded(self) -> bool:
        """Indique si l'exécution s'est terminée sans erreur."""
        return self.error is None


class CodeExecutor:
    """Exécute des scripts dans un espace de noms conservé entre les exécutions."""

    def __init__(self, context: Mapping[str, Any] | None = None) -> None:
        """Initialise l'espace de noms.

        Args:
            context: Objets à rendre accessibles aux scripts, indexés par leur nom.
        """
        self._namespace: dict[str, Any] = {**(context or {}), "__name__": "__main__"}

    @property
    def namespace(self) -> dict[str, Any]:
        """Retourne l'espace de noms contenant les variables de l'utilisateur."""
        return self._namespace

    def execute(self, code: str) -> ExecutionResult:
        """Exécute un script et capture ses sorties.

        Args:
            code: Code source Python à exécuter.

        Returns:
            Les sorties produites et l'éventuelle erreur.
        """
        buffer = io.StringIO()
        error = None
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
            try:
                self._run(code)
            except (Exception, SystemExit) as exception:
                error = _format_exception(exception)
        return ExecutionResult(buffer.getvalue(), error)

    def _run(self, code: str) -> None:
        """Exécute le script et affiche la valeur de sa dernière expression.

        Args:
            code: Code source Python à exécuter.
        """
        tree = ast.parse(code, filename=SCRIPT_FILENAME)
        last_expression = None
        if tree.body and isinstance(tree.body[-1], ast.Expr):
            last_expression = ast.Expression(tree.body.pop().value)
        exec(compile(tree, SCRIPT_FILENAME, "exec"), self._namespace)
        if last_expression is None:
            return
        value = eval(compile(last_expression, SCRIPT_FILENAME, "eval"), self._namespace)
        if value is not None:
            print(repr(value))


def _user_traceback(trace: TracebackType | None) -> TracebackType | None:
    """Retire d'un traceback les frames internes à l'application.

    Args:
        trace: Traceback complet de l'exception.

    Returns:
        Le traceback à partir de la première frame du script utilisateur.
    """
    while trace is not None and trace.tb_frame.f_code.co_filename != SCRIPT_FILENAME:
        trace = trace.tb_next
    return trace


def _format_exception(exception: BaseException) -> str:
    """Met en forme une exception levée par le script utilisateur.

    Args:
        exception: Exception à mettre en forme.

    Returns:
        Le texte du traceback.
    """
    trace = _user_traceback(exception.__traceback__)
    return "".join(traceback.format_exception(type(exception), exception, trace))
