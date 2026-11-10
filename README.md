# Fenêtre d'analyse

Console Python graphique (Tkinter) à intégrer dans une application existante. Elle permet de
saisir et d'exécuter du code Python, et ce code peut appeler les fonctions et les méthodes de
l'application qui l'héberge. Les scripts peuvent aussi être exécutés sans afficher la fenêtre,
puis vérifiés plus tard dans son historique.

La fenêtre comporte :

- **un éditeur** pour saisir le code, avec un bouton **▶ Exécuter** ;
- **un historique** des scripts exécutés et de leurs résultats (code en bleu, erreurs en rouge,
  fichier d'origine en gris), avec un bouton **Effacer l'historique** ;
- **un tableau des variables** (nom, type, valeur) regroupées par catégorie, avec une couleur
  par catégorie et un bouton **Réinitialiser les variables**.

Les trois zones ont une barre de défilement verticale et une horizontale.

## Prérequis

- Python 3.10 ou plus récent, avec Tkinter (fourni avec Python sous Windows).
- Aucune dépendance externe : seule la bibliothèque standard est utilisée.

## Lancement autonome

```
python main.py
```

## Intégration dans une application

Copier le dossier `analyse_app/` à côté du script de l'application, ou ajouter son
emplacement à `sys.path`, puis utiliser les classes suivantes.

| Classe | Usage |
|--------|-------|
| `AnalysisWindow(parent, context=None, session=None)` | Ouvre une fenêtre secondaire (`tk.Toplevel`). |
| `AnalysisPanel(parent, context=None, session=None)` | Crée un panneau (`ttk.Frame`) à placer dans votre interface : onglet, frame… |
| `AnalysisSession(context=None)` | Exécute des scripts et garde l'historique, sans interface. |

```python
from analyse_app import AnalysisPanel, AnalysisWindow

# Dans une fenêtre séparée
AnalysisWindow(self, context=contexte)

# Intégrée à l'interface existante
AnalysisPanel(mon_frame, context=contexte).pack(fill="both", expand=True)
```

Sans `session`, la fenêtre ou le panneau crée sa propre session, qui disparaît avec lui. Pour
garder l'historique entre deux ouvertures, ou pour exécuter des scripts sans fenêtre, passer une
`AnalysisSession` (voir plus bas). `context` et `session` ne peuvent pas être fournis ensemble
(`ValueError`) : le contexte se donne alors à la session.

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

### Exécuter un script sans afficher la fenêtre

`AnalysisSession` contient l'exécution et l'historique, sans aucune interface. L'application
crée une session au démarrage, y exécute des scripts ou des fichiers quand elle le souhaite,
puis la passe à la fenêtre ou au panneau, qui affiche alors tout l'historique et les variables :

```python
from analyse_app import AnalysisSession, AnalysisWindow

self.session = AnalysisSession(context={"app": self, "measures": self.measures})

# Sans fenêtre : du code…
result = self.session.run("compute_average(measures)")
# … ou le contenu d'un fichier
result = self.session.run_file(r"C:\scripts\analyse.py")

if result.succeeded:
    print(result.output)      # sorties + valeur de la dernière expression
else:
    print(result.error)       # traceback

# Plus tard : la fenêtre affiche les scripts déjà exécutés et leurs variables
AnalysisWindow(self, session=self.session)
```

| Élément | Rôle |
|---------|------|
| `session.run(code)` | Exécute le script, l'ajoute à l'historique, retourne un `ExecutionResult`. |
| `session.run_file(path, encoding="utf-8-sig")` | Idem avec le contenu d'un fichier (`str` ou `Path`). |
| `result.output`, `result.error`, `result.succeeded` | Sorties, traceback (ou `None`), succès. |
| `session.history` | Exécutions passées (`HistoryEntry` : `code`, `result`, `source`). |
| `session.namespace` | Variables de la session. |
| `session.clear_history()` | Efface l'historique ; les variables sont conservées. |
| `session.reset_namespace()` | Supprime les variables créées par les scripts et rétablit le contexte initial ; l'historique est conservé. |
| `session.subscribe(listener)`, `session.unsubscribe(listener)` | Abonne ou désabonne une fonction qui reçoit un `SessionEvent` à chaque modification. |

**Exécution d'un fichier :**
- **Historique :** l'entrée commence par `# Fichier : <chemin>`, et `HistoryEntry.source` contient ce chemin.
- **Erreur dans le script :** elle est renvoyée dans `result.error`, comme pour `run`.
- **Fichier introuvable ou illisible :** la méthode lève une exception (`OSError`, `UnicodeDecodeError`) et rien n'est ajouté à l'historique.
- **Encodage :** par défaut `utf-8-sig`, qui lit l'UTF-8 avec ou sans BOM.

**Mise à jour de la fenêtre :** si la fenêtre est ouverte, elle se met à jour immédiatement après `run`, `run_file`, `clear_history` ou `reset_namespace`, que l'appel vienne de la fenêtre ou de l'application. Fermer la fenêtre ne perd rien : la session conserve tout.

### Suivre les modifications d'une session

Le panneau s'abonne à sa session pour se mettre à jour. Une application peut faire de même,
par exemple pour journaliser les exécutions :

```python
from analyse_app import EventKind, SessionEvent

def on_event(event: SessionEvent) -> None:
    if event.kind is EventKind.ENTRY_ADDED:
        print("Exécuté :", event.entry.code, "→ succès :", event.entry.result.succeeded)

session.subscribe(on_event)
```

| `event.kind` | Déclencheur | `event.entry` |
|--------------|-------------|---------------|
| `EventKind.ENTRY_ADDED` | `run`, `run_file`, bouton Exécuter | la nouvelle `HistoryEntry` |
| `EventKind.HISTORY_CLEARED` | `clear_history`, bouton Effacer l'historique | `None` |
| `EventKind.NAMESPACE_RESET` | `reset_namespace`, bouton Réinitialiser les variables | `None` |

### Exemples

Le dossier [exemples/](exemples/) rassemble les différentes possibilités. Chaque exemple se lance
depuis la racine du projet :

| Fichier | Ce qu'il montre |
|---------|-----------------|
| [01_panneau_integre.py](exemples/01_panneau_integre.py) | `AnalysisPanel` placé dans un onglet de l'application. |
| [02_fenetre_secondaire.py](exemples/02_fenetre_secondaire.py) | `AnalysisWindow` ouverte par un bouton, avec une fonction dans `context`. |
| [03_application_complete.py](exemples/03_application_complete.py) | Application hôte avec une session partagée : script sans fenêtre, exécution d'un fichier choisi, ouverture de l'analyse (un second clic la ramène au premier plan). |
| [04_sans_interface.py](exemples/04_sans_interface.py) | Exécution de code et de fichiers sans fenêtre, résultats vérifiés dans la console, puis ouverture de la fenêtre sur l'historique (`--sans-fenetre` pour s'en passer). |

```
python exemples/04_sans_interface.py
```

Le sous-dossier [exemples/scripts/](exemples/scripts/) contient des fichiers à exécuter avec
`run_file` ou le bouton « Exécuter un fichier… » de l'exemple 3 :

| Script | Contenu |
|--------|---------|
| [hello.py](exemples/scripts/hello.py) | `print("hello")`. |
| [statistiques.py](exemples/scripts/statistiques.py) | Fonction, import, compréhension de liste et valeur finale, en utilisant `measures` et `add_measure` du contexte. |
| [erreur.py](exemples/scripts/erreur.py) | Division par zéro, pour voir le traceback dans l'historique. |

## Fonctionnement

### Exécution

- **Variables conservées :** les variables restent disponibles d'une exécution à l'autre, comme
  dans une console Python, tant que la session existe.
- **Affichage de la dernière expression :** si le script se termine par une expression (par
  exemple `x + 1`), sa valeur est affichée sans qu'il faille appeler `print`.
- **Sorties capturées :** les sorties de `print` (stdout et stderr) s'affichent dans l'historique.
- **Erreurs sans fermeture :** une erreur, y compris `SyntaxError` ou `sys.exit()`, affiche le
  traceback mais ne ferme pas l'application.

### Boutons Effacer et Réinitialiser

- **Confirmation :** les deux boutons demandent une confirmation avant d'agir.
- **« Effacer l'historique » :** vide l'historique ; les variables restent.
- **« Réinitialiser les variables » :** supprime les variables, fonctions et classes créées par les scripts et rétablit le contexte initial ; l'historique reste.
- **Limite de la réinitialisation :** elle n'annule pas ce que les scripts ont fait aux objets de l'application. Après `add_measure(5)`, `measures` contient toujours `5`, car c'est la vraie liste de l'application. En revanche, `measures = []` est bien annulé.

### Tableau des variables

- **Groupes :** les variables sont rangées en groupes repliables, chacun avec sa couleur. Un
  groupe replié le reste après les exécutions suivantes. Les groupes vides ne sont pas affichés.

  | Groupe | Contenu | Couleur |
  |--------|---------|---------|
  | Fonctions | fonctions, méthodes, lambdas, objets appelables (affichés avec leur signature) | violet |
  | Classes | classes | orange |
  | Nombres | `int`, `float`, `complex`, `bool` | bleu |
  | Textes | `str`, `bytes`, `bytearray` | vert |
  | Collections | `list`, `tuple`, `dict`, `set`… et tout objet ayant `len`, l'itération et `in` | turquoise |
  | Objets | tout le reste, y compris `None` | gris |

- **Variables masquées :** les modules importés et les noms commençant par `_` n'apparaissent
  pas.
- **Valeurs tronquées :** les valeurs sont coupées à 100 caractères.
- **Rafraîchissement :** le tableau est mis à jour après chaque exécution et chaque
  réinitialisation, pas pendant qu'un script tourne.

### Défilement

L'historique, l'éditeur et le tableau des variables ont chacun une barre verticale et une
horizontale. Les lignes longues ne sont pas renvoyées à la ligne, y compris dans l'historique.
La colonne Valeur est toujours assez large pour afficher la valeur la plus longue.

## Points d'attention

- **Sécurité :** le code saisi s'exécute avec tous les droits du programme. Il ne faut exécuter
  que du code de confiance. Restreindre `context` limite ce qui est directement accessible, mais
  ne protège de rien : un script peut toujours faire `import os`.
- **Réaffecter n'est pas modifier :** `measures.append(1)` modifie la liste de l'application,
  alors que `measures = []` ne fait que redéfinir le nom dans la session. Après une
  réaffectation, ce nom ne désigne plus les données de l'application.
- **Interface bloquée :** les scripts s'exécutent dans le fil de l'interface. Les méthodes de
  l'application peuvent donc manipuler ses widgets sans risque, mais un calcul long fige toute
  l'application, et une boucle infinie oblige à la fermer de force.
- **Appels depuis le fil Tkinter uniquement :** si la fenêtre est ouverte, les méthodes de la
  session mettent à jour ses widgets. Il faut donc les appeler depuis le fil Tkinter, pas depuis
  un thread secondaire.
- **`input()` :** cette fonction ne passe pas par la fenêtre. Elle attend une saisie dans le
  terminal et bloque l'interface.

## Structure du projet

L'architecture est expliquée en détail, avec schémas, dans
[docs/architecture.html](docs/architecture.html) (à ouvrir dans un navigateur).

```
fenetre_analyse/
├── main.py                    # Lancement autonome
├── docs/architecture.html     # Architecture détaillée
├── exemples/                  # Exemples d'utilisation (voir ci-dessus)
│   └── scripts/               # Fichiers à exécuter avec run_file
└── analyse_app/
    ├── analysis_window.py     # Fenêtre secondaire (Toplevel)
    ├── analysis_panel.py      # Panneau assemblant les zones et suivant la session
    ├── analysis_session.py    # Session sans interface : exécution, historique, événements
    ├── editor_frame.py        # Éditeur et bouton Exécuter
    ├── history_frame.py       # Historique et bouton Effacer
    ├── variables_frame.py     # Variables par catégorie (Treeview) et bouton Réinitialiser
    ├── scrollbars.py          # Barres de défilement verticale et horizontale
    ├── code_executor.py       # Exécution du code, capture des sorties, réinitialisation
    └── variable_inspector.py  # Extraction et classement des variables
```
