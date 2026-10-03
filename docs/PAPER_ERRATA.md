# Working-Paper Errata and Reconciliation Notes

These notes refer to the pre-reconciliation working paper preserved in Git history and the historical branch. The unreconciled paper binary is intentionally not part of the research-facing main branch.

The purpose is to identify statements that should be interpreted more narrowly until the paper is formally revised.

## 1. Equilibrium prior

The working paper describes a market-capitalization-weighted Black-Litterman equilibrium prior.

The public repository does not contain a defensible historical ETF market-capitalization/AUM series for the full study horizon. Earlier code approximated “market cap” with price × volume; that approximation is not market capitalization and has been removed from the canonical research path.

The cleaned reconciliation implementation therefore uses an explicitly labelled equal-weight equilibrium proxy unless a justified prior-weight series is supplied.

## 2. Crisis-language correction

The paper contains wording suggesting superior downside mitigation across developed and emerging markets.

The reported US 2008 crisis table does not support universal Black-Litterman dominance:

- BL max drawdown: -62.57%
- Markowitz max drawdown: -62.18%
- BL recovery: 1093 trading days
- Markowitz recovery: 1056 trading days

The defensible interpretation is that crisis behavior is broadly comparable in some episodes, with modest BL advantages in selected emerging-market metrics but no universal dominance.

## 3. Factor interpretation

A statistically significant momentum loading is evidence of factor exposure. It does not, by itself, prove that momentum uniquely caused all observed Markowitz outperformance.

The appropriate wording is “consistent with greater momentum exposure.”

## 4. Published results versus reproducibility

The paper-reported 12.99% / 0.650 US BL result family is preserved as a published reference.

An older public repository result family reported materially different values, including US BL Sharpe 1.208. Those stale result files were removed from the research-facing main branch.

The cleaned pipeline writes new results to results/recomputed/. Until an end-to-end rerun with the intended prior specification is validated, the repository does not claim independent reproduction of the paper table.

## 5. Research figures

Earlier repository code generated several “realistic-looking” time-series illustrations using random data. Those images and the old generator were removed from the research-facing evidence chain.

The current figure generator reads only saved empirical series. If the required empirical output is absent, figure generation fails rather than fabricating a trajectory.

## 6. Tau sensitivity

The paper reports a modest change in Sharpe across tau values, while a later stale repository table showed an identical Sharpe across all tau values.

That stale table has been removed from main. Tau sensitivity remains a reconciliation item until regenerated from the final parameterization.

## 7. SOE/private interpretation

The reported p-value near 0.572 means the study fails to find statistically significant evidence of a risk-adjusted performance difference at conventional levels.

It should not be described as proof that ownership can never matter.

## 8. Status

These notes do not erase the earlier research history. Historical code and outputs remain available through Git history and the historical branch.

The research-facing main branch is intentionally narrower and more conservative.
