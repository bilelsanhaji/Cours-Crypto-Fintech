# Jeu de données de secours

**Ce dossier est vide tant que `download_data.py` n'a pas été lancé une fois.**

```bash
python 03-Data/download_data.py
```

Le script écrit ici une copie de `panier.csv`, `panier_complet.csv` et
`rendements.csv`. **Versionner cette copie dans Git** : c'est le plan B si le
réseau tombe en salle, ou si l'API change.

`outils_cours.charger_panier()` cherche dans cet ordre :

1. `03-Data/<fichier>` — les données fraîches
2. `03-Data/backup/<fichier>` — cette copie
3. `03-Data/SYNTHETIQUE_panier.csv` — données **simulées**, avec avertissement

Le niveau 3 sert uniquement à vérifier que les notebooks s'exécutent.
Ne jamais présenter un résultat obtenu dessus comme empirique.
