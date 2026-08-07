# Cryptomonnaies et Fintech — M2 MBFA, parcours Finance

**Université Paris 8 — Master 2 Monnaie, Banque, Finance, Assurance**
Enseignement de 9 heures — 3 séances de 3 × 50 min · B. Sanhaji

---

## De quoi il s'agit

Ce cours traite les crypto-actifs comme une **classe d'actifs à part entière** :
leurs instruments, leur microstructure, leur cadre réglementaire, et surtout
leurs propriétés statistiques particulières.

Le fil des trois séances :

| | Question directrice | Ce que vous saurez faire |
|---|---|---|
| **1** | De quoi parle-t-on ? | Classer un crypto-actif, lire un marché, situer une règle |
| **2** | En quoi ces séries sont-elles particulières ? | Établir les faits stylisés, tester l'efficience |
| **3** | Combien peut-on perdre ? | Estimer une VaR, la *backtester*, la critiquer |

La compétence visée n'est pas « connaître la crypto ». C'est **mesurer un risque
sur un actif dont la distribution se comporte mal, et vérifier sa mesure** — ce
qui vaut aussi pour les matières premières, les marchés émergents ou le risque
de crédit.

---

## Ce que contient ce dépôt

| Dossier | Contenu |
|---|---|
| `00-Syllabus/` | Le syllabus complet : objectifs, programme, évaluation, bibliographie |
| `01-Slides/etudiant/` | Les slides des trois séances (Quarto reveal.js) |
| `02-TP/` | Les notebooks des travaux pratiques, et le guide d'installation |
| `03-Data/` | Le script de collecte des données, et un jeu de secours |
| `04-Eval/` | Les sujets de projet et les consignes de rendu |

Les corrigés des TP sont déposés après chaque séance.

---

## Installation — à faire avant la première séance

**Suivez `02-TP/GUIDE-DEMARRAGE.md`** : c'est un pas-à-pas complet, sans
prérequis technique, qui prend 15 à 20 minutes.

Version courte, si vous êtes déjà à l'aise :

```bash
git clone https://github.com/bilelsanhaji/Cours-Crypto-Fintech.git
cd Cours-Crypto-Fintech

python3 -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements.txt

python 03-Data/download_data.py
```

> **Si le téléchargement échoue**
>
> Un jeu de secours est versionné dans `03-Data/backup/`, et les notebooks
> basculent dessus automatiquement. Le cours fonctionne hors ligne.

**Un ordinateur portable est obligatoire** : la troisième partie de chaque
séance se fait sur machine, en binômes.

---

## Le panier du fil rouge

Les mêmes cinq actifs servent de la première séance au projet final :

| Actif | Ticker | Pourquoi lui |
|---|---|---|
| Bitcoin | `BTC-USD` | Le crypto-actif « macro », détenu en ETF par des institutionnels |
| Ethereum | `ETH-USD` | Plateforme avec des flux — frais brûlés et *staking* |
| Solana | `SOL-USD` | Altcoin à bêta élevé — le comportement extrême |
| S&P 500 | `^GSPC` | Référence actions |
| Or | `GC=F` | Référence « valeur refuge » |

Période : **2018-01-01 → aujourd'hui**, soit trois cycles complets.

---

## Compiler les slides vous-même

```bash
cd 01-Slides/etudiant
quarto render
```

Nécessite [Quarto](https://quarto.org/docs/get-started/). Les slides sont aussi
distribuées en HTML autonome — un seul fichier, qui fonctionne hors ligne.

---

## Prérequis

- **Théoriques** : séries temporelles (stationnarité, autocorrélation,
  rendements) ; statistique inférentielle (tests d'hypothèses).
- **Techniques** : Python — manipulation de `DataFrame` pandas, tracé matplotlib.

---

## Évaluation

| Composante | Poids |
|---|---|
| Fiche d'actif | 10 % |
| Note de diagnostic empirique | 20 % |
| Rapport de risque | 20 % |
| Projet final — écrit | 40 % |
| Projet final — soutenance | 10 % |

Le détail, les sujets et les attendus sont dans `04-Eval/sujets-projet.md`.

**La reproductibilité est notée** dans chaque rendu comportant du code : un
notebook qui ne s'exécute pas de bout en bout après *Restart & Run All* est
sanctionné, quelle que soit la qualité de l'analyse.

---

## Licence et usage

Matériel pédagogique mis à disposition des étudiants du M2 MBFA de
l'Université Paris 8. Réutilisation à des fins d'enseignement bienvenue, avec
mention de la source.

**Ce cours ne constitue pas un conseil en investissement.** Il porte sur
l'analyse et la mesure du risque.
