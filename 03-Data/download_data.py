#!/usr/bin/env python3
"""
Collecte des données du cours M2 Crypto/Fintech.

À exécuter UNE FOIS avant la première séance, depuis une machine connectée.
Le script écrit :
  - 03-Data/panier.csv           prix de clôture des 5 actifs du fil rouge
  - 03-Data/rendements.csv       rendements log quotidiens
  - 03-Data/backup/panier.csv    copie de secours, à versionner dans Git

Usage
-----
    python download_data.py                  # période par défaut
    python download_data.py --start 2015-01-01
    python download_data.py --no-backup      # ne pas écraser la copie de secours

Si Yahoo Finance est indisponible, utiliser make_synthetic_fallback.py pour
générer un jeu de test synthétique (mécanique des TP uniquement, PAS de vraies
données).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------- #
# Panier du fil rouge — utilisé de la séance 1 au projet final
# --------------------------------------------------------------------------- #
PANIER = {
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "SOL-USD": "Solana",
    "^GSPC": "SP500",
    "GC=F": "Or",
}

ICI = Path(__file__).resolve().parent
DOSSIER_BACKUP = ICI / "backup"


def telecharger(tickers: list[str], start: str, end: str | None) -> pd.DataFrame:
    """Télécharge les clôtures ajustées et renvoie un DataFrame à colonnes nommées."""
    try:
        import yfinance as yf
    except ImportError:
        sys.exit("yfinance n'est pas installé — lancer : pip install yfinance")

    brut = yf.download(
        tickers,
        start=start,
        end=end,
        progress=False,
        auto_adjust=True,
        group_by="column",
    )

    if brut.empty:
        sys.exit(
            "Téléchargement vide. Vérifier la connexion, ou utiliser "
            "make_synthetic_fallback.py / le CSV de secours dans backup/."
        )

    # yfinance renvoie un MultiIndex (champ, ticker) quand plusieurs tickers
    prix = brut["Close"] if isinstance(brut.columns, pd.MultiIndex) else brut[["Close"]]
    prix = prix.rename(columns=PANIER)
    prix = prix[[PANIER[t] for t in tickers if PANIER[t] in prix.columns]]
    return prix


def nettoyer(prix: pd.DataFrame) -> pd.DataFrame:
    """
    Aligne les calendriers 24/7 (crypto) et 5j/7 (actions, or).

    Choix pédagogique assumé : on garde le calendrier des marchés traditionnels
    (intersection) pour que les corrélations soient calculées sur des dates
    comparables. Les TP font expliciter ce choix et ses conséquences.
    Le fichier complet 24/7 est conservé à part pour la séance 2.
    """
    prix = prix.sort_index()
    prix.index.name = "Date"
    return prix


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--start", default="2018-01-01")
    p.add_argument("--end", default=None)
    p.add_argument("--no-backup", action="store_true")
    args = p.parse_args()

    print(f"Téléchargement : {', '.join(PANIER)}  ({args.start} → {args.end or 'aujourd’hui'})")
    prix = nettoyer(telecharger(list(PANIER), args.start, args.end))

    # --- fichier 1 : toutes les dates disponibles (crypto = 7j/7) ------------- #
    prix.to_csv(ICI / "panier_complet.csv")

    # --- fichier 2 : calendrier commun, sans trou -----------------------------#
    commun = prix.dropna()
    commun.to_csv(ICI / "panier.csv")

    # --- fichier 3 : rendements log ------------------------------------------#
    rendements = np.log(commun).diff().dropna()
    rendements.to_csv(ICI / "rendements.csv")

    if not args.no_backup:
        DOSSIER_BACKUP.mkdir(exist_ok=True)
        commun.to_csv(DOSSIER_BACKUP / "panier.csv")
        prix.to_csv(DOSSIER_BACKUP / "panier_complet.csv")
        rendements.to_csv(DOSSIER_BACKUP / "rendements.csv")
        print(f"Copie de secours écrite dans {DOSSIER_BACKUP}")

    # --- contrôle qualité ----------------------------------------------------#
    print("\n--- Contrôle ---")
    print(f"Période        : {commun.index.min():%Y-%m-%d} → {commun.index.max():%Y-%m-%d}")
    print(f"Observations   : {len(commun)} (calendrier commun) / {len(prix)} (brut)")
    print(f"Colonnes       : {list(commun.columns)}")
    print(f"Valeurs nulles : {int(prix.isna().sum().sum())} avant alignement")
    print("\nVolatilité annualisée (base 252 j, sur calendrier commun) :")
    print((rendements.std() * np.sqrt(252) * 100).round(1).to_string())
    print("\n⚠️  Sur le fichier 24/7, l'annualisation correcte est √365 — voir séance 2.")


if __name__ == "__main__":
    main()
