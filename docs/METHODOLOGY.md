# Methodology

## Market universe

The study uses liquid ETF baskets representing three equity markets:

- US: SPY, QQQ, IWM, XLF, XLK
- China: ASHR, KWEB, MCHI, FXI
- India: INDA, EPI, SMIN, INDY

The requested sample is 2010-2025. Because some ETFs have shorter listing histories, each market uses the common observed history available across its basket.

## Rolling design

The backtest uses:

- 252 trading days for estimation;
- 63 trading days between rebalances;
- Ledoit-Wolf covariance shrinkage;
- long-only weights;
- full investment;
- 10 bps proportional transaction cost per unit of turnover.

No future observation is used when estimating a rebalance-date portfolio.

## Markowitz portfolio

Expected returns are estimated from the historical mean inside each rolling training window.

The same covariance matrix, optimizer and weight constraints used for Black-Litterman are also used for Markowitz.

## Black-Litterman portfolio

Equilibrium-implied expected returns are:

[
Pi = lambda Sigma w_{eq}
]

The public implementation defaults to equal equilibrium weights. A different equilibrium-weight series can be supplied directly when historical capitalization or AUM data are available.

Absolute ETF views use:

[
Q = Pi + 0.10(mu_{hist} - Pi)
]

with an identity view matrix and diagonal view uncertainty.

The prior scaling parameter (	au) is conditioned using realized volatility observed inside the training window.

## Turnover and transaction costs

Before every rebalance, the previous portfolio is drifted using the realized asset returns from the preceding holding period.

Turnover is then calculated from the difference between drifted pre-trade weights and new target weights. Transaction cost is charged once at the rebalance.

## Allocation Stability Index

ASI measures the mean L1 change in target weights between consecutive rebalances:

[
ASI_t = sum_i |w_{i,t} - w_{i,t-1}|
]

ASI is used as a stability measure; it is separate from trading turnover.

## Factor analysis

For the US portfolio, excess returns are regressed on MKT, SMB, HML and MOM factors from the Kenneth French Data Library.

Inference uses Newey-West/HAC standard errors.

## Regime analysis

A two-state Markov-switching model is used to classify high- and low-volatility observations for conditional analysis.

The model's smoothed probabilities are used for ex-post evaluation, not as a live portfolio signal.

## Crisis analysis

The crisis helper freezes the last portfolio weights observed before a specified crisis start date and holds those weights fixed through the crisis window.

The study considers the 2008 US Global Financial Crisis, the 2015 China equity crash and the 2020 India COVID shock.
