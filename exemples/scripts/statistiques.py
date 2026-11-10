"""Statistiques sur les mesures de l'application.

Utilise `measures` et `add_measure`, fournis par le contexte de la session.
Si aucune mesure n'existe, quelques valeurs de démonstration sont ajoutées.
"""

import statistics

DEMO_VALUES = (12.5, 15.0, 9.75, 20.25, 14.0)


def summarize(values: list[float]) -> dict[str, float]:
    """Calcule les statistiques principales d'une série de valeurs.

    Args:
        values: Valeurs à résumer, au moins deux.

    Returns:
        Le nombre de valeurs, le minimum, le maximum, la moyenne et l'écart type.
    """
    return {
        "nombre": len(values),
        "minimum": min(values),
        "maximum": max(values),
        "moyenne": round(statistics.mean(values), 2),
        "écart type": round(statistics.stdev(values), 2),
    }


if len(measures) < 2:
    for value in DEMO_VALUES:
        add_measure(value)

summary = summarize(measures)
for name, value in summary.items():
    print(f"{name:>10} : {value}")

above_average = [value for value in measures if value > summary["moyenne"]]
print(f"Au-dessus de la moyenne : {above_average}")
summary["moyenne"]
