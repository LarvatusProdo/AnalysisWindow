"""Script volontairement en erreur, pour voir le traceback dans l'historique.

La variable `total` reste définie dans la session malgré l'erreur.
"""

total = sum(measures)
print(f"Total : {total}")
ratio = total / 0
print("Cette ligne n'est jamais atteinte.")
