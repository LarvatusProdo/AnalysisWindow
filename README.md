# Fenêtre d'analyse

Console Python graphique (Tkinter) à intégrer dans une application existante. Elle permet de
saisir et d'exécuter du code Python, et ce code peut appeler les fonctions et les méthodes de
l'application qui l'héberge.

La fenêtre comporte :

- **un éditeur** pour saisir le code, avec un bouton **▶ Exécuter** ;
- **un historique** des scripts exécutés et de leurs résultats (code en bleu, erreurs en rouge) ;
- **un tableau des variables** (nom, type, valeur), mis à jour après chaque exécution.

## Prérequis

- Python 3.10 ou plus récent, avec Tkinter (fourni avec Python sous Windows).
- Aucune dépendance externe : seule la bibliothèque standard est utilisée.

## Lancement autonome

```
python main.py
```

## Intégration dans une application

Copier le dossier `analyse_app/` à côté du script de l'application, ou ajouter son
emplacement à `sys.path`, puis utiliser l'une des deux classes suivantes.

| Classe | Usage |
|--------|-------|
| `AnalysisWindow(parent, context=None)` | Ouvre une fenêtre secondaire (`tk.Toplevel`). |
| `AnalysisPanel(parent, context=None)` | Crée un panneau (`ttk.Frame`) à placer dans votre interface : onglet, frame… |

```python
from analyse_app import AnalysisPanel, AnalysisWindow

# Dans une fenêtre séparée
AnalysisWindow(self, context=contexte)

# Intégrée à l'interface existante
AnalysisPanel(mon_frame, context=contexte).pack(fill="both", expand=True)
```

### Rendre des fonctions de l'application accessibles

Le paramètre `context` est un dictionnaire qui associe un nom à chaque objet utilisable dans les
scripts :

```python
AnalysisWindow(self, context={
    "app": self,                         # l'application entière
    "add_measure": self.add_measure,     # une méthode
    "compute_average": compute_average,  # une fonction
    "measures": self.measures,           # une donnée
})
```

Dans l'éditeur, l'utilisateur peut alors écrire :

```python
add_measure(42)
app.add_measure(58)
print(compute_average(measures))   # affiche 50.0
```

Ces appels agissent sur la véritable application. Les objets transmis apparaissent aussi dans le
tableau des variables.

### Exemple complet

[exemple_application.py](exemple_application.py) montre une application qui gère une liste
de mesures, avec un bouton qui ouvre la fenêtre d'analyse. Un second clic ramène la fenêtre au
premier plan au lieu d'en créer une autre.

```
python exemple_application.py
```

## Fonctionnement

- **Variables conservées :** les variables restent disponibles d'une exécution à l'autre, comme
  dans une console Python.
- **Affichage de la dernière expression :** si le script se termine par une expression (par
  exemple `x + 1`), sa valeur est affichée sans qu'il faille appeler `print`.
- **Sorties capturées :** les sorties de `print` (stdout et stderr) s'affichent dans l'historique.
- **Erreurs sans fermeture :** une erreur, y compris `SyntaxError` ou `sys.exit()`, affiche le
  traceback mais ne ferme pas l'application.
- **Variables masquées :** les modules importés et les noms commençant par `_` n'apparaissent pas
  dans le tableau.
- **Valeurs tronquées :** dans le tableau, les valeurs sont coupées à 100 caractères.

## Points d'attention

- **Sécurité :** le code saisi s'exécute avec tous les droits du programme. Il ne faut exécuter
  que du code de confiance. Restreindre `context` limite ce qui est directement accessible, mais
  ne protège de rien : un script peut toujours faire `import os`.
- **Réaffecter n'est pas modifier :** `measures.append(1)` modifie la liste de l'application,
  alors que `measures = []` ne fait que redéfinir le nom dans la fenêtre d'analyse. Après une
  réaffectation, ce nom ne désigne plus les données de l'application.
- **Interface bloquée :** les scripts s'exécutent dans le fil de l'interface. Les méthodes de
  l'application peuvent donc manipuler ses widgets sans risque, mais un calcul long fige toute
  l'application, et une boucle infinie oblige à la fermer de force.
- **`input()` :** cette fonction ne passe pas par la fenêtre. Elle attend une saisie dans le
  terminal et bloque l'interface.
- **Tableau des variables :** il n'est rafraîchi qu'après une exécution.

## Structure du projet

L'architecture est expliquée en détail, avec schémas, dans
[docs/architecture.html](docs/architecture.html) (à ouvrir dans un navigateur).

```
fenetre_analyse/
├── main.py                    # Lancement autonome
├── exemple_application.py     # Exemple d'application hôte
└── analyse_app/
    ├── analysis_window.py     # Fenêtre secondaire (Toplevel)
    ├── analysis_panel.py      # Panneau assemblant les zones
    ├── editor_frame.py        # Éditeur et bouton Exécuter
    ├── history_frame.py       # Historique
    ├── variables_frame.py     # Tableau des variables (Treeview)
    ├── code_executor.py       # Exécution du code et capture des sorties
    └── variable_inspector.py  # Extraction des variables à afficher
```
