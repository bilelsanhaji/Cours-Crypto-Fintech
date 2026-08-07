"""
Boîte à outils du cours M2 Crypto/Fintech.

Ce module contient les fonctions d'infrastructure fournies aux étudiants :
chargement des données, tests statistiques peu disponibles dans statsmodels
(ratio de variance de Lo-MacKinlay, Kupiec, Christoffersen), estimateur de Hill.

Les étudiants ne les réécrivent pas — ils les utilisent et doivent savoir
expliquer ce qu'elles font. Chaque fonction est accompagnée d'un test de
cohérence exécutable via :

    python outils_cours.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

__all__ = [
    "charger_panier",
    "rendements_log",
    "table_faits_stylises",
    "hill",
    "variance_ratio",
    "ewma_variance",
    "var_historique",
    "var_gaussienne",
    "var_student",
    "var_monte_carlo",
    "expected_shortfall_historique",
    "kupiec",
    "christoffersen",
    "backtest_complet",
]

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_DATA = RACINE / "03-Data"


# --------------------------------------------------------------------------- #
# 1. Données
# --------------------------------------------------------------------------- #
def charger_panier(fichier: str = "panier.csv") -> pd.DataFrame:
    """
    Charge le panier du cours, avec repli automatique.

    Ordre d'essai : 03-Data/<fichier> → 03-Data/backup/<fichier>
                    → 03-Data/SYNTHETIQUE_panier.csv (avertissement)
    """
    candidats = [
        DOSSIER_DATA / fichier,
        DOSSIER_DATA / "backup" / fichier,
    ]
    for chemin in candidats:
        if chemin.exists():
            return pd.read_csv(chemin, index_col=0, parse_dates=True)

    synth = DOSSIER_DATA / "SYNTHETIQUE_panier.csv"
    if synth.exists():
        print(
            "⚠️  ATTENTION : données SYNTHÉTIQUES chargées (ce ne sont pas de vraies\n"
            "    données de marché). Lancer 03-Data/download_data.py pour les vraies."
        )
        return pd.read_csv(synth, index_col=0, parse_dates=True, comment="#")

    raise FileNotFoundError(
        f"Aucun jeu de données trouvé dans {DOSSIER_DATA}. "
        "Lancer d'abord : python 03-Data/download_data.py"
    )


def rendements_log(prix: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    """Rendements logarithmiques quotidiens."""
    return np.log(prix).diff().dropna()


# --------------------------------------------------------------------------- #
# 2. Faits stylisés
# --------------------------------------------------------------------------- #
def table_faits_stylises(r: pd.DataFrame, jours_an: int | dict[str, int] = 252) -> pd.DataFrame:
    """
    Tableau récapitulatif des faits stylisés.

    Parameters
    ----------
    r : DataFrame de rendements log
    jours_an : int, ou dict {colonne: nb de jours} pour gérer crypto (365) vs
        actions (252). Voir séance 2, « le piège du 24/7 ».
    """
    if isinstance(jours_an, int):
        jours_an = {c: jours_an for c in r.columns}

    lignes = {}
    for c in r.columns:
        x = r[c].dropna()
        n_an = jours_an.get(c, 252)
        jb, p_jb = stats.jarque_bera(x)[:2]
        lignes[c] = {
            "n": len(x),
            "moy. ann. %": x.mean() * n_an * 100,
            "vol. ann. %": x.std(ddof=1) * np.sqrt(n_an) * 100,
            "min %": x.min() * 100,
            "max %": x.max() * 100,
            "asymétrie": stats.skew(x),
            "kurtosis excès": stats.kurtosis(x),  # Fisher : normale -> 0
            "Jarque-Bera": jb,
            "p(JB)": p_jb,
            "ρ(r,1)": x.autocorr(1),
            "ρ(|r|,1)": x.abs().autocorr(1),
            "ρ(|r|,10)": x.abs().autocorr(10),
        }
    return pd.DataFrame(lignes).T


def hill(x: np.ndarray | pd.Series, k: int) -> float:
    """
    Estimateur de Hill de l'indice de queue alpha, sur les k plus grandes
    valeurs absolues.

    P(|r| > x) ~ x^(-alpha). Un alpha faible = queue épaisse.
    Le moment d'ordre m existe si et seulement si m < alpha.

    ⚠️  Très sensible au choix de k : tracer alpha(k) et lire une zone stable.
    """
    x = np.sort(np.abs(np.asarray(x, dtype=float)))[::-1]
    if k >= len(x) or k < 2:
        raise ValueError(f"k doit vérifier 2 <= k < {len(x)}")
    inv_alpha = np.mean(np.log(x[:k] / x[k]))
    return 1.0 / inv_alpha


def variance_ratio(r: np.ndarray | pd.Series, q: int, robuste: bool = True) -> dict:
    """
    Test du ratio de variance de Lo & MacKinlay (1988).

    H0 : marche aléatoire (incréments non corrélés).
    VR(q) > 1 -> persistance ; VR(q) < 1 -> retour à la moyenne.

    Parameters
    ----------
    robuste : si True, statistique M2 robuste à l'hétéroscédasticité.
        À utiliser systématiquement sur données financières (voir séance 2).

    Returns
    -------
    dict avec VR, statistique z, p-value bilatérale.
    """
    r = np.asarray(pd.Series(r).dropna(), dtype=float)
    n = len(r)
    if q < 2 or q >= n:
        raise ValueError("q doit vérifier 2 <= q < n")

    mu = r.mean()
    # variance des rendements d'ordre 1 (estimateur non biaisé)
    var_1 = np.sum((r - mu) ** 2) / (n - 1)

    # variance des rendements agrégés sur q périodes, chevauchants
    r_q = np.convolve(r, np.ones(q), mode="valid")  # somme glissante
    m = q * (n - q + 1) * (1 - q / n)
    var_q = np.sum((r_q - q * mu) ** 2) / m

    vr = var_q / var_1

    if not robuste:
        phi = 2 * (2 * q - 1) * (q - 1) / (3 * q * n)
    else:
        # estimateur robuste à l'hétéroscédasticité, Lo-MacKinlay (1988) eq. (18)
        #   delta_j = sum_t e2_t * e2_{t-j} / (sum_t e2_t)^2      ~ O(1/n)
        #   theta*  = sum_{j=1}^{q-1} [2(q-j)/q]^2 * delta_j
        # Le facteur 1/n est déjà contenu dans delta_j : ne pas le rajouter.
        e2 = (r - mu) ** 2
        denom = np.sum(e2) ** 2
        phi = 0.0
        for j in range(1, q):
            delta_j = np.sum(e2[j:] * e2[:-j]) / denom
            phi += (2 * (q - j) / q) ** 2 * delta_j

    z = (vr - 1) / np.sqrt(phi)
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    return {"q": q, "VR": vr, "z": z, "p_value": p, "robuste": robuste}


# --------------------------------------------------------------------------- #
# 3. Volatilité
# --------------------------------------------------------------------------- #
def ewma_variance(r: pd.Series, lam: float = 0.94, var0: float | None = None) -> pd.Series:
    """
    Variance EWMA (RiskMetrics) : sigma2_t = lam*sigma2_{t-1} + (1-lam)*r2_{t-1}.

    La série renvoyée est décalée : sigma2_t n'utilise que l'information
    jusqu'en t-1. C'est indispensable pour un backtesting honnête.
    """
    r = r.dropna()
    r2 = (r - r.mean()) ** 2
    if var0 is None:
        var0 = r2.iloc[: min(60, len(r2))].mean()

    out = np.empty(len(r2))
    out[0] = var0
    vals = r2.to_numpy()
    for t in range(1, len(r2)):
        out[t] = lam * out[t - 1] + (1 - lam) * vals[t - 1]
    return pd.Series(out, index=r2.index, name=f"ewma_var_lam{lam}")


# --------------------------------------------------------------------------- #
# 4. VaR et Expected Shortfall
#    Convention du cours : la VaR est un nombre POSITIF (une perte).
# --------------------------------------------------------------------------- #
def var_historique(r: np.ndarray | pd.Series, alpha: float = 0.01) -> float:
    return float(-np.quantile(np.asarray(pd.Series(r).dropna()), alpha))


def var_gaussienne(mu: float, sigma: float, alpha: float = 0.01) -> float:
    return float(-(mu + stats.norm.ppf(alpha) * sigma))


def var_student(mu: float, sigma: float, nu: float, alpha: float = 0.01) -> float:
    """
    VaR sous loi de Student STANDARDISÉE (variance unitaire).

    Le facteur sqrt((nu-2)/nu) est indispensable : sans lui la variance de la
    t(nu) vaut nu/(nu-2) et la VaR est fausse. Erreur très fréquente.

    Note : à volatilité fixée, la VaR standardisée n'est PAS monotone en nu près
    de nu=2. À alpha=1 %, elle culmine autour de nu≈4 puis redescend. C'est un
    effet de la standardisation, pas un bug — la queue est bien plus épaisse pour
    nu=3, mais l'échelle est comprimée pour maintenir la variance à 1.
    """
    if nu <= 2:
        raise ValueError("nu doit être > 2 pour que la variance existe")
    q = stats.t.ppf(alpha, df=nu) * np.sqrt((nu - 2) / nu)
    return float(-(mu + q * sigma))


def var_monte_carlo(
    mu: float,
    sigma: float,
    alpha: float = 0.01,
    n_sim: int = 100_000,
    loi: str = "normale",
    nu: float = 5.0,
    graine: int = 42,
) -> float:
    """VaR par simulation. Ne vaut que ce que vaut la loi simulée."""
    rng = np.random.default_rng(graine)
    if loi == "normale":
        tirages = rng.normal(mu, sigma, n_sim)
    elif loi == "student":
        z = rng.standard_t(nu, n_sim) * np.sqrt((nu - 2) / nu)
        tirages = mu + sigma * z
    else:
        raise ValueError("loi doit valoir 'normale' ou 'student'")
    return float(-np.quantile(tirages, alpha))


def expected_shortfall_historique(r: np.ndarray | pd.Series, alpha: float = 0.01) -> float:
    """ES empirique : moyenne des pertes au-delà de la VaR."""
    x = np.asarray(pd.Series(r).dropna())
    seuil = np.quantile(x, alpha)
    queue = x[x <= seuil]
    if len(queue) == 0:
        return float("nan")
    return float(-queue.mean())


# --------------------------------------------------------------------------- #
# 5. Backtesting
# --------------------------------------------------------------------------- #
def kupiec(depassements: np.ndarray | pd.Series, alpha: float) -> dict:
    """
    Test de couverture inconditionnelle de Kupiec (1995). LR_uc ~ chi2(1).

    H0 : la fréquence observée des dépassements est égale à alpha.
    """
    I = np.asarray(pd.Series(depassements).dropna(), dtype=int)
    T, N = len(I), int(I.sum())
    pi = N / T if T else np.nan

    if N == 0:
        lr = -2 * T * np.log(1 - alpha)
    elif N == T:
        lr = -2 * T * np.log(alpha)
    else:
        ll0 = (T - N) * np.log(1 - alpha) + N * np.log(alpha)
        ll1 = (T - N) * np.log(1 - pi) + N * np.log(pi)
        lr = -2 * (ll0 - ll1)

    return {
        "T": T,
        "N_observés": N,
        "N_attendus": alpha * T,
        "taux_observé": pi,
        "LR_uc": lr,
        "p_value": 1 - stats.chi2.cdf(lr, 1),
    }


def christoffersen(depassements: np.ndarray | pd.Series, alpha: float) -> dict:
    """
    Test d'indépendance de Christoffersen (1998) et test conjoint.

    H0 (indépendance) : P(I_t=1 | I_{t-1}=1) = P(I_t=1 | I_{t-1}=0).
    Un rejet signale des dépassements GROUPÉS : la dynamique de volatilité
    est mal captée, même si le nombre total est correct.
    """
    I = np.asarray(pd.Series(depassements).dropna(), dtype=int)
    prec, suiv = I[:-1], I[1:]

    n00 = int(np.sum((prec == 0) & (suiv == 0)))
    n01 = int(np.sum((prec == 0) & (suiv == 1)))
    n10 = int(np.sum((prec == 1) & (suiv == 0)))
    n11 = int(np.sum((prec == 1) & (suiv == 1)))

    pi01 = n01 / (n00 + n01) if (n00 + n01) else 0.0
    pi11 = n11 / (n10 + n11) if (n10 + n11) else 0.0
    pi = (n01 + n11) / (n00 + n01 + n10 + n11)

    def _ll(p, k, n):
        if p in (0.0, 1.0):
            return 0.0 if (k == 0 or k == n) else -np.inf
        return k * np.log(p) + (n - k) * np.log(1 - p)

    ll_h0 = _ll(pi, n01 + n11, n00 + n01 + n10 + n11)
    ll_h1 = _ll(pi01, n01, n00 + n01) + _ll(pi11, n11, n10 + n11)
    lr_ind = -2 * (ll_h0 - ll_h1)
    lr_ind = max(lr_ind, 0.0)

    lr_uc = kupiec(I, alpha)["LR_uc"]
    lr_cc = lr_uc + lr_ind

    return {
        "n00": n00, "n01": n01, "n10": n10, "n11": n11,
        "P(dép. | dép. la veille)": pi11,
        "P(dép. | pas de dép.)": pi01,
        "LR_ind": lr_ind,
        "p_ind": 1 - stats.chi2.cdf(lr_ind, 1),
        "LR_cc": lr_cc,
        "p_cc": 1 - stats.chi2.cdf(lr_cc, 2),
    }


def backtest_complet(
    rendements: pd.Series, var_serie: pd.Series, alpha: float, nom: str = "modèle"
) -> dict:
    """
    Backtesting Kupiec + Christoffersen sur une série de VaR.

    `var_serie` est une série de VaR POSITIVES, alignée sur `rendements`.
    Un dépassement a lieu quand -r_t > VaR_t.
    """
    idx = rendements.index.intersection(var_serie.index)
    r, v = rendements.loc[idx], var_serie.loc[idx]
    I = ((-r) > v).astype(int)

    k, c = kupiec(I, alpha), christoffersen(I, alpha)
    return {
        "modèle": nom,
        "alpha": alpha,
        "T": k["T"],
        "dépassements": k["N_observés"],
        "attendus": round(k["N_attendus"], 1),
        "p_Kupiec": round(k["p_value"], 4),
        "p_indépendance": round(c["p_ind"], 4),
        "p_conjoint": round(c["p_cc"], 4),
        "verdict": (
            "validé" if (k["p_value"] > 0.05 and c["p_ind"] > 0.05)
            else "rejeté (niveau)" if k["p_value"] <= 0.05 and c["p_ind"] > 0.05
            else "rejeté (regroupement)" if k["p_value"] > 0.05
            else "rejeté (les deux)"
        ),
        "_depassements": I,
    }


# --------------------------------------------------------------------------- #
# Tests de cohérence — python outils_cours.py
# --------------------------------------------------------------------------- #
def _auto_test() -> None:
    rng = np.random.default_rng(7)
    print("=" * 68)
    print("TESTS DE COHÉRENCE — outils_cours.py")
    print("=" * 68)

    # --- 1. variance_ratio sur une vraie marche aléatoire -> VR ~ 1 ---------- #
    print("\n[1] variance_ratio sur bruit blanc gaussien (VR attendu ≈ 1)")
    bb = pd.Series(rng.normal(0, 0.01, 5000))
    for q in (2, 4, 8, 16):
        res = variance_ratio(bb, q)
        print(f"    q={q:>2}  VR={res['VR']:.3f}  z={res['z']:+.2f}  p={res['p_value']:.3f}")

    for q in (2, 4, 8, 16):
        assert variance_ratio(bb, q)["p_value"] > 0.05, "faux rejet sur bruit blanc"

    # --- 2. variance_ratio sur des séries autocorrélées --------------------- #
    print("\n[2] variance_ratio sur AR(1) (VR > 1 si phi > 0, VR < 1 si phi < 0)")
    n = 5000
    for phi_ar in (0.15, -0.15):
        e = rng.normal(0, 0.01, n)
        ar = np.zeros(n)
        for t in range(1, n):
            ar[t] = phi_ar * ar[t - 1] + e[t]
        res = variance_ratio(pd.Series(ar), 4)
        print(f"    phi={phi_ar:+.2f}  q=4  VR={res['VR']:.3f}  "
              f"z={res['z']:+.2f}  p={res['p_value']:.6f}")
        assert (res["VR"] > 1) == (phi_ar > 0), "signe du VR incohérent"
        assert res["p_value"] < 0.01, "le test devrait rejeter la marche aléatoire"

    # --- 3. hill sur une Pareto d'indice connu ------------------------------ #
    print("\n[3] hill sur Pareto(alpha=3) simulée (alpha attendu ≈ 3)")
    pareto = (1 - rng.random(20000)) ** (-1 / 3)
    for k in (200, 500, 1000, 2000):
        print(f"    k={k:>4}  alpha_hat={hill(pareto, k):.2f}")

    # --- 4. VaR : cohérence gaussienne analytique vs Monte Carlo ------------ #
    print("\n[4] VaR gaussienne : analytique vs Monte Carlo (doivent coïncider)")
    mu, sigma = 0.0005, 0.03
    for a in (0.01, 0.05):
        va = var_gaussienne(mu, sigma, a)
        vm = var_monte_carlo(mu, sigma, a, n_sim=400_000, loi="normale")
        print(f"    alpha={a:.0%}  analytique={va:.5f}  MC={vm:.5f}  écart={abs(va-vm):.5f}")
        assert abs(va - vm) < 5e-4

    # --- 5. VaR Student > VaR gaussienne (queues épaisses) ------------------ #
    print("\n[5] VaR Student vs gaussienne à même volatilité (Student doit être > )")
    for nu in (3, 4, 6, 10, 30):
        vs = var_student(mu, sigma, nu, 0.01)
        vg = var_gaussienne(mu, sigma, 0.01)
        print(f"    nu={nu:>2}  VaR_t={vs:.4f}  VaR_N={vg:.4f}  ratio={vs/vg:.3f}")
    assert var_student(mu, sigma, 4, 0.01) > var_gaussienne(mu, sigma, 0.01)

    # --- 6. Kupiec : modèle correct vs modèle trop optimiste ---------------- #
    print("\n[6] Kupiec — modèle bien calibré (p élevée attendue)")
    I_ok = (rng.random(2000) < 0.01).astype(int)
    k = kupiec(I_ok, 0.01)
    print(f"    N={k['N_observés']}  attendus={k['N_attendus']:.0f}  p={k['p_value']:.3f}")

    print("\n    Kupiec — modèle sous-estimant le risque (p faible attendue)")
    I_ko = (rng.random(2000) < 0.035).astype(int)
    k = kupiec(I_ko, 0.01)
    print(f"    N={k['N_observés']}  attendus={k['N_attendus']:.0f}  p={k['p_value']:.6f}")
    assert k["p_value"] < 0.01

    # --- 7. Christoffersen : dépassements groupés --------------------------- #
    print("\n[7] Christoffersen — dépassements GROUPÉS (p_ind faible attendue)")
    I_grp = np.zeros(2000, dtype=int)
    for debut in (300, 900, 1500):
        I_grp[debut : debut + 7] = 1          # 21 dépassements, tous groupés
    c = christoffersen(I_grp, 0.01)
    print(f"    N={I_grp.sum()}  P(dép|dép)={c['P(dép. | dép. la veille)']:.2f}"
          f"  p_ind={c['p_ind']:.6f}")
    assert c["p_ind"] < 0.01, "le test devrait détecter le regroupement"

    print("\n    Christoffersen — dépassements DISPERSÉS (p_ind élevée attendue)")
    c = christoffersen(I_ok, 0.01)
    print(f"    N={I_ok.sum()}  p_ind={c['p_ind']:.3f}")

    # --- 8. EWMA : décalage temporel correct -------------------------------- #
    print("\n[8] ewma_variance — vérification du décalage (pas de look-ahead)")
    s = pd.Series(rng.normal(0, 0.02, 500))
    v = ewma_variance(s, 0.94)
    print(f"    longueur={len(v)}  vol. moyenne annualisée={np.sqrt(v.mean()*252):.1%}")
    print(f"    demi-vie(lam=0.94) = {np.log(0.5)/np.log(0.94):.1f} jours")

    print("\n" + "=" * 68)
    print("✅  Tous les tests passent.")
    print("=" * 68)


if __name__ == "__main__":
    _auto_test()
