# Projet final — sujets et consignes

**M2 MBFA — Cryptomonnaies et Fintech · volet quantitatif**

---

## Format

| | |
|---|---|
| **Travail** | En binôme (trinôme accepté si effectif impair, avec exigences relevées) |
| **Livrables** | 1 notebook Jupyter reproductible + 1 note de synthèse de 3 pages + 1 soutenance de 7 min |
| **Poids** | 40 % (écrit) + 10 % (soutenance) de la note de l'enseignement |
| **Validation du sujet** | Obligatoire, **avant la fin de la séance 3** |
| **Dépôt** | Une archive `NOM1-NOM2.zip` contenant le notebook, la note en PDF, et les données si elles ne sont pas téléchargeables |

> **Trois exigences non négociables**
>
> 1. **Reproductibilité** — *Restart & Run All* doit fonctionner. Graine fixée, chemins relatifs.
> 2. **Section « limites »** obligatoire et notée.
> 3. **Aucune recommandation d'investissement.** L'objet est l'analyse du risque.

---

## Sujet 1 — L'effet des ETF au comptant sur le profil de risque du Bitcoin

**Question** — Le lancement des ETF Bitcoin au comptant aux États-Unis (11 janvier 2024)
a-t-il modifié le comportement statistique du Bitcoin ?

**Ce qu'il faut faire**

1. Découper l'échantillon avant / après le 11 janvier 2024.
2. Comparer sur les deux sous-périodes : volatilité annualisée, kurtosis, indice de
   queue de Hill, corrélation avec le S&P 500, ratio de variance $VR(q)$.
3. Tester la significativité des écarts — au minimum un test de Fisher sur les
   variances et un test de Fisher sur les corrélations transformées par la
   $z$ de Fisher.
4. Discuter l'**identification** : que d'autre a changé sur la période ?

**Les pièges à ne pas manquer**

- Le sous-échantillon « après » est court : la puissance des tests est faible.
  Un non-rejet ne prouve rien.
- La période post-2024 contient le krach de 2026. Un changement de volatilité
  peut refléter ce seul épisode.
- Il n'y a **pas de contrefactuel**. On ne peut pas conclure causalement.
  Une bonne copie le dit explicitement et propose un placebo (l'or ? l'ETH,
  dont l'ETF est arrivé plus tard ?).

**Ce qui distingue une excellente copie** — la proposition d'une stratégie
d'identification crédible, même imparfaite, plutôt qu'un simple avant/après.

---

## Sujet 2 — Quelle VaR pour un portefeuille 80 / 20 ?

**Question** — Un gérant détient 80 % d'actions (S&P 500) et 20 % de crypto
(à répartir). Quelle méthode de VaR retenir, et à quel coût en fonds propres ?

**Ce qu'il faut faire**

1. Construire la série de rendements du portefeuille (rendements **arithmétiques**
   pour l'agrégation — justifier ce choix).
2. Calculer au moins quatre VaR et les ES associées, en fenêtre glissante.
3. Backtester chacune (Kupiec, Christoffersen, test conjoint).
4. Comparer avec un portefeuille 100 % actions : de combien la poche crypto
   augmente-t-elle la VaR ? Y a-t-il un bénéfice de diversification ?
5. Traduire en euros sur un portefeuille de 50 M€.

**Les pièges à ne pas manquer**

- Le rééquilibrage. Un portefeuille 80/20 dérive. Rééquilibrage quotidien,
  mensuel, ou pas de rééquilibrage ? Le choix change les résultats — le justifier.
- Les calendriers. Les cryptos cotent le week-end, pas le S&P 500. Quelle
  convention retenez-vous pour les rendements du portefeuille le samedi ?
- La VaR n'est pas sous-additive : vérifiez-le sur vos propres chiffres.

**Ce qui distingue une excellente copie** — le calcul de la contribution marginale
de la poche crypto au risque total, et la mise en évidence d'un point où
l'augmentation de la VaR devient disproportionnée.

---

## Sujet 3 — Couverture, diversification, ou simple actif de risque ?

**Question** — Appliquer au Bitcoin le cadre de Baur & Lucey (2010), conçu pour l'or.

**Le cadre**

Un actif est un **diversificateur** s'il est faiblement corrélé en moyenne ;
une **couverture** s'il est décorrélé ou négativement corrélé en moyenne ;
une **valeur refuge** s'il est décorrélé ou négativement corrélé **en période de
stress**. La régression :

$$r_t^{\text{BTC}} = a_0 + a_1 r_t^{\text{SP}} + \big(b_0 + b_1 D_t\big) r_t^{\text{SP}} + \varepsilon_t$$

où $D_t = 1$ si $r_t^{\text{SP}}$ est dans le quantile inférieur (1 %, 5 %, 10 %).

**Ce qu'il faut faire**

1. Estimer la régression, avec erreurs standard robustes (HAC).
2. Faire le même exercice sur l'or, comme point de comparaison.
3. Refaire l'exercice sur sous-périodes (avant/après 2024).
4. Conclure : que peut-on dire, et que ne peut-on pas dire ?

**Les pièges à ne pas manquer**

- Conditionner sur les extrêmes biaise mécaniquement les corrélations
  (Boyer, Gibson & Loretan, 1999). Le mentionner est un prérequis.
- Les erreurs standard OLS sont invalides ici (hétéroscédasticité, autocorrélation).
- « Non significatif » ≠ « nul ».

---

## Sujet 4 — Anatomie du *peg* d'un stablecoin

**Question** — Les décrochages d'un stablecoin sont-ils prévisibles, et que
révèlent-ils sur la qualité de ses réserves ?

**Ce qu'il faut faire**

1. Récupérer la série de prix d'un ou deux stablecoins (USDT, USDC, DAI) contre USD.
2. Caractériser l'écart au *peg* : distribution, asymétrie, persistance
   (autocorrélation, test de racine unitaire sur l'écart).
3. Identifier les épisodes de décrochage et les rattacher à un événement.
4. Comparer un stablecoin adossé à un stablecoin décentralisé/sur-collatéralisé.
5. Discuter ce que MiCA et le GENIUS Act changent à ce risque.

**Les pièges à ne pas manquer**

- La qualité des données est le vrai problème : selon la source, le prix d'un
  stablecoin est une moyenne pondérée qui lisse les décrochages. Documentez
  votre source et sa méthode.
- Un stablecoin bien tenu a une variance quasi nulle en régime normal : les
  tests statistiques standard se comportent mal. C'est une difficulté à traiter,
  pas à ignorer.

**Ce qui distingue une excellente copie** — l'articulation entre le fait empirique
(le décrochage) et le mécanisme de bilan (la composition des réserves).

---

## Sujet 5 — Sujet libre

**Conditions de validation**

Votre question doit :

1. être formulée de façon à recevoir une réponse **chiffrée** ;
2. être traitable avec les données du panier ou des données librement accessibles ;
3. mobiliser au moins **deux** des trois séances ;
4. ne pas être une prédiction de prix.

**Exemples déjà validés les années précédentes**

- Les journées de forte sortie d'ETF sont-elles suivies de rendements négatifs ?
- La volatilité crypto du week-end diffère-t-elle de celle de la semaine ?
- L'effet de levier est-il inversé en régime haussier sur le Bitcoin ?
- Le taux de financement des contrats perpétuels prédit-il les retournements ?

**Exemples refusés**

- « Prédire le prix du Bitcoin en 2027 » *(pas de réponse chiffrable et vérifiable)*
- « Comparer 50 cryptomonnaies » *(descriptif, sans question)*
- « Construire une stratégie de trading rentable » *(dragage de données garanti)*

---

## Calendrier

| Étape | Échéance |
|---|---|
| Validation du sujet | Fin de la séance 3 |
| Question de méthode par courriel | Jusqu'à J−7 |
| Dépôt du notebook + note | J (à fixer, ≈ 3 semaines après la séance 3) |
| Soutenances | Semaine suivante |

---

## Format de la note de synthèse (3 pages)

| Section | Longueur indicative |
|---|---|
| 1. Question et enjeu | ¼ page |
| 2. Données et méthode | ¾ page |
| 3. Résultats | 1 page — tableaux et graphiques inclus |
| 4. Interprétation | ½ page |
| 5. **Limites** | ½ page — **notée** |

Police 11 pt, interligne simple, bibliographie hors quota.
