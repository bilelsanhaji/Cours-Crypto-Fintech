# Guide de démarrage — installer son environnement Python

Ce guide vous explique comment installer tout ce qu'il faut pour faire les TP
du cours, **une seule fois**, avant la première séance. Comptez 15-20 minutes.

Vous aurez besoin d'un ordinateur (Mac, Windows ou Linux) et d'une connexion
internet.

---

## Étape 1 — Installer les outils de base

### a) Python

Vérifiez si Python est déjà installé. Ouvrez un terminal :

- **Mac** : application *Terminal* (Cmd+Espace, tapez « terminal »)
- **Windows** : application *PowerShell* ou *Invite de commandes*

et tapez :

```bash
python3 --version
```

(sous Windows, essayez `python --version` si `python3` ne fonctionne pas)

- Si une version **3.10 ou plus récente** s'affiche → passez à l'étape suivante.
- Si vous avez une erreur, ou une version **antérieure à 3.9** → installez Python
  depuis [python.org/downloads](https://www.python.org/downloads/) (choisissez
  la version la plus récente). **Sous Windows**, cochez bien la case
  *"Add python.exe to PATH"* pendant l'installation.

### b) VS Code

Téléchargez et installez [Visual Studio Code](https://code.visualstudio.com/).

Une fois ouvert, allez dans l'onglet **Extensions** (icône de carrés dans la
barre de gauche) et installez :

- **Python** (éditeur Microsoft)
- **Jupyter** (éditeur Microsoft)

---

## Étape 2 — Récupérer les fichiers du cours

Récupérez le dossier du cours (transmis par l'enseignant — clé USB, lien de
téléchargement, ou dépôt Git) et placez-le où vous voulez sur votre
ordinateur, par exemple dans `Documents/`.

Ouvrez ce dossier dans VS Code : **Fichier → Ouvrir le dossier…**, sélectionnez
le dossier `M2-Crypto-Fintech`.

---

## Étape 3 — Créer l'environnement Python

Un « environnement virtuel » est un dossier isolé qui contient uniquement les
bibliothèques du cours, sans toucher au reste de votre ordinateur. C'est la
bonne pratique — on l'utilise toujours.

Dans VS Code, ouvrez un terminal intégré (**Terminal → Nouveau terminal**, ou
`` Ctrl+` ``). Vérifiez que vous êtes à la racine de `M2-Crypto-Fintech` (pas
dans un sous-dossier), puis tapez :

**Mac / Linux :**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Windows (PowerShell) :**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

L'installation des bibliothèques (pandas, numpy, jupyterlab, etc.) prend
1 à 3 minutes. C'est normal si le terminal n'affiche rien pendant quelques
secondes.

> **Windows — erreur "impossible de charger le fichier ... l'exécution de
> scripts est désactivée"** : ouvrez PowerShell **en administrateur** et tapez
> une fois `Set-ExecutionPolicy RemoteSigned`, validez avec `O` (Oui), puis
> refaites l'étape 3.

---

## Étape 4 — Télécharger les données du cours

Toujours dans le même terminal (l'environnement doit rester activé — vous
voyez `(.venv)` au début de la ligne) :

```bash
python 03-Data/download_data.py
```

Si votre réseau bloque l'accès à Yahoo Finance (Wi-Fi de certaines
résidences, par exemple), ce n'est pas grave : les notebooks basculent
automatiquement sur une copie de secours déjà fournie dans le dossier.

---

## Étape 5 — Ouvrir un notebook et choisir le bon interpréteur

1. Dans VS Code, ouvrez `02-TP/TP0-prise-en-main.ipynb`.
2. En haut à droite du notebook, cliquez sur **Sélectionner le kernel**
   (« Select Kernel »).
3. Choisissez **Environnements Python…** puis celui qui contient `.venv`
   (souvent affiché comme `.venv (Python 3.x.x)`).

Sans cette étape, VS Code utilise un Python par défaut qui ne connaît pas les
bibliothèques installées à l'étape 3, et vous aurez une erreur
`ModuleNotFoundError`.

---

## Étape 6 — Vérifier que tout fonctionne

Cliquez sur la première cellule de code du notebook (celle sous
« ## 1. Environnement ») et exécutez-la avec **Shift+Entrée**.

Si vous voyez s'afficher :

```
Environnement prêt.
```

→ tout est en ordre, vous pouvez commencer le TP.

---

## Dépannage — les erreurs les plus fréquentes

| Message d'erreur | Cause probable | Solution |
|---|---|---|
| `ModuleNotFoundError: No module named 'pandas'` (ou autre) | Le mauvais kernel est sélectionné | Refaites l'étape 5 |
| La cellule tourne indéfiniment (`[*]`) sans jamais finir | Le kernel a planté ou n'a jamais démarré | Cliquez sur **Redémarrer le kernel** (icône ↻ en haut du notebook) |
| Vous venez de corriger le code mais l'erreur persiste à l'identique | Le kernel garde en mémoire l'ancienne version | Redémarrez le kernel (↻), ou fermez et rouvrez le fichier |
| `command not found: python3` / `'python' n'est pas reconnu` | Python n'est pas installé, ou pas dans le PATH | Réinstallez Python en cochant *"Add to PATH"* (Windows) |
| Le terminal affiche `(.venv)` disparu après avoir fermé/rouvert VS Code | L'environnement n'est plus activé dans ce terminal | Relancez la commande d'activation de l'étape 3 (`source .venv/bin/activate` ou `.venv\Scripts\Activate.ps1`) — l'installation elle-même n'est pas à refaire |
| Erreur réseau lors de `download_data.py` | API Yahoo Finance temporairement inaccessible | Rien à faire : le notebook bascule seul sur les données de secours |

Si une erreur ne correspond à rien de la liste, copiez le message complet
affiché sous la cellule (pas juste la dernière ligne) et montrez-le à
l'enseignant ou posez la question en séance.
