# Slides du cours

Les slides publiées sont dans **`etudiant/`**. La configuration Quarto et le
thème se trouvent à la **racine du dépôt** (`_quarto.yml`, `theme.scss`).

## Compiler

Depuis la racine du dépôt :

```bash
quarto render 01-Slides/etudiant/S1-fondamentaux.qmd
```

ou tout d'un coup :

```bash
quarto render 01-Slides/etudiant
```

Nécessite [Quarto](https://quarto.org/docs/get-started/). Le rendu produit un
fichier HTML autonome par séance, qui fonctionne hors ligne.

## Naviguer pendant la présentation

| Touche | Effet |
|---|---|
| `F` | Plein écran |
| `O` ou `Échap` | Vue d'ensemble des slides |
| `←` `→` | Slide précédente / suivante |
| `?` | Liste complète des raccourcis |

## Personnaliser

Tout est dans `theme.scss`, à la racine : palette (bleu de Klein, bleu de Prusse,
argent, or), tailles, et les encadrés du cours — `.retenir` (à mémoriser),
`.piege` (contre-intuitif), `.definition`, `.question`.
