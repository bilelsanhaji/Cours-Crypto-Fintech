# Slides du cours

Les slides publiées sont dans **`etudiant/`**. Ce dossier-ci contient la
configuration commune : le thème et les profils de rendu.

## Compiler

```bash
cd etudiant
quarto render
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

Tout est dans `theme.scss` : palette (bleu de Klein, bleu de Prusse, argent,
or), tailles, et les encadrés du cours — `.retenir` (à mémoriser),
`.piege` (contre-intuitif), `.definition`, `.question`.
