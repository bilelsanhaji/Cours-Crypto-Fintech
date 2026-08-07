#!/usr/bin/env python3
"""
Génère un jeu de données SYNTHÉTIQUE pour tester la mécanique des TP hors ligne.

⚠️  CE NE SONT PAS DE VRAIES DONNÉES DE MARCHÉ.
    Ne jamais l'utiliser pour un résultat présenté comme empirique.
    Usage strictement technique : vérifier que les notebooks s'exécutent quand
    l'API est indisponible en salle.

Le générateur reproduit délibérément trois faits stylisés (voir séance 2) :
  - agrégation de la volatilité, via un processus de volatilité stochastique
  - queues épaisses, via des innovations de Student
  - effet de levier, via une corrélation négative choc/volatilité

Cela permet aussi un usage pédagogique honnête : comparer les résultats obtenus
sur données simulées « bien élevées » et sur données réelles.

Usage
-----
    python make_synthetic_fallback.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ICI = Path(__file__).resolve().parent
GRAINE = 20260904

# nom -> (vol annuelle cible, dérive annuelle, ddl Student, effet de levier)
PROFILS = {
    "Bitcoin":  (0.62, 0.30, 5.0, -0.20),
    "Ethereum": (0.75, 0.25, 5.0, -0.18),
    "Solana":   (0.95, 0.20, 4.5, -0.15),
    "SP500":    (0.17, 0.09, 7.0, -0.35),
    "Or":       (0.14, 0.06, 9.0, -0.05),
}

# corrélation instantanée entre actifs (ordre : BTC, ETH, SOL, SP500, Or)
CORR = np.array(
    [
        [1.00, 0.82, 0.72, 0.35, 0.10],
        [0.82, 1.00, 0.78, 0.33, 0.08],
        [0.72, 0.78, 1.00, 0.30, 0.06],
        [0.35, 0.33, 0.30, 1.00, 0.05],
        [0.10, 0.08, 0.06, 0.05, 1.00],
    ]
)


def simule(n: int, rng: np.random.Generator) -> pd.DataFrame:
    noms = list(PROFILS)
    k = len(noms)

    # innovations corrélées, à queues épaisses (mélange gaussien / Student)
    L = np.linalg.cholesky(CORR)
    z = rng.standard_normal((n, k)) @ L.T

    rendements = np.zeros((n, k))
    for j, nom in enumerate(noms):
        vol_cible, derive, ddl, levier = PROFILS[nom]
        sigma_j = vol_cible / np.sqrt(252)

        # volatilité stochastique log-AR(1) -> agrégation de la volatilité
        phi, eta = 0.96, 0.11
        h = np.zeros(n)
        bruit_vol = rng.standard_normal(n)
        for t in range(1, n):
            # effet de levier : un choc négatif fait monter la volatilité future
            h[t] = phi * h[t - 1] + eta * (levier * z[t - 1, j] + np.sqrt(1 - levier**2) * bruit_vol[t])
        vol_t = sigma_j * np.exp(h - h.var() / 2)

        # innovations de Student standardisées -> queues épaisses
        chi = rng.chisquare(ddl, n) / ddl
        eps = z[:, j] / np.sqrt(chi)
        eps /= np.sqrt(ddl / (ddl - 2))

        rendements[:, j] = derive / 252 + vol_t * eps

    dates = pd.bdate_range("2018-01-01", periods=n, name="Date")
    r = pd.DataFrame(rendements, index=dates, columns=noms)

    # niveaux de prix plausibles (base 100 rééchelonnée)
    bases = {"Bitcoin": 13_000, "Ethereum": 700, "Solana": 12, "SP500": 2_700, "Or": 1_300}
    prix = pd.DataFrame(
        {c: bases[c] * np.exp(r[c].cumsum()) for c in noms}, index=dates
    )
    return prix, r


def main() -> None:
    rng = np.random.default_rng(GRAINE)
    prix, rendements = simule(n=2100, rng=rng)

    entete = "# DONNEES SYNTHETIQUES - NE PAS UTILISER COMME DONNEES DE MARCHE\n"
    for nom, df in (("panier", prix), ("rendements", rendements)):
        chemin = ICI / f"SYNTHETIQUE_{nom}.csv"
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(entete)
            df.to_csv(f)
        print(f"écrit : {chemin.name}")

    print("\n--- Faits stylisés obtenus (contrôle) ---")
    diag = pd.DataFrame(
        {
            "vol. annualisée %": rendements.std() * np.sqrt(252) * 100,
            "asymétrie": rendements.skew(),
            "kurtosis excès": rendements.kurtosis(),
            "autocorr. r(1)": [rendements[c].autocorr(1) for c in rendements],
            "autocorr. |r|(1)": [rendements[c].abs().autocorr(1) for c in rendements],
        }
    )
    print(diag.round(2).to_string())
    print(
        "\nLecture : kurtosis en excès > 0 et autocorr. de |r| >> autocorr. de r "
        "\n=> queues épaisses + agrégation de la volatilité, comme sur données réelles."
    )


if __name__ == "__main__":
    main()
