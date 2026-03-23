# Regime-Sensitive Black–Litterman Portfolio Allocation  
### A Cross-Market Empirical Framework for Stability, Turnover, and Crisis Resilience

**Author:** Amit Kumar Dudi  
**Affiliation:** Independent Quantitative Finance Researcher  
**Date:** March 2026  

---

## 1. Research Overview

This repository implements a fully reproducible quantitative research framework designed to evaluate the structural limitations of classical mean–variance portfolio optimization and to assess the effectiveness of the Black–Litterman Bayesian allocation model under realistic market conditions.

The study is motivated by a well-documented limitation in portfolio theory: the Markowitz optimizer behaves as an **error-amplifying mechanism**, producing unstable and economically infeasible allocations when exposed to estimation noise in expected returns.

To address this instability, the Black–Litterman model introduces **Bayesian equilibrium shrinkage**, anchoring expected returns to a market-implied prior and thereby stabilizing portfolio weights.

This research evaluates these competing frameworks across three structurally distinct markets:

- United States (developed, highly efficient)
- China (policy-driven emerging market)
- India (high-growth emerging market)

The empirical framework integrates **allocation stability, transaction costs, and crisis recovery dynamics** into a unified evaluation system.

---

## 2. Research Objectives

The study is designed to address the following fundamental questions:

- Does Bayesian shrinkage improve out-of-sample portfolio stability?
- Can allocation instability be formally measured and controlled?
- Do transaction costs eliminate the apparent performance advantage of unstable optimizers?
- Are crisis outcomes driven by optimization methodology or underlying asset exposure?

---

## 3. Hypotheses

The empirical analysis evaluates four core hypotheses:

- **H1 — Performance Robustness:**  
  Black–Litterman improves risk-adjusted performance under realistic estimation uncertainty.

- **H2 — Allocation Stability (ASI):**  
  Bayesian equilibrium anchoring significantly reduces weight instability.

- **H3 — Transaction Cost Efficiency:**  
  Lower turnover leads to superior net-of-cost performance.

- **H4 — SOE Stability Hypothesis:**  
  State ownership does not provide statistically significant downside protection in Chinese equity markets.

---

## 4. Data and Market Representation

To ensure scalability and eliminate idiosyncratic noise, the study employs **Exchange-Traded Funds (ETFs)** as proxies for broad asset classes.

### Dataset Characteristics

- Frequency: Daily  
- Period: 2010–2025  
- Data Type: Adjusted Close Prices  

### Market Coverage

**United States (Developed Market)**
- SPY, QQQ, IWM, XLF, XLK  

**China (Emerging Market)**
- ASHR, KWEB, MCHI, FXI  

**India (Emerging Market)**
- INDA, EPI, SMIN, INDY  

---

## 5. Methodological Framework

The research pipeline follows a strictly chronological, bias-free structure:

```text
Market Data Acquisition
        ↓
Log Returns Calculation
        ↓ 
Covariance Estimation (Ledoit–Wolf)
        ↓
Black–Litterman Posterior Estimation
        ↓ 
Portfolio Optimization
        ↓
Rolling Out-of-Sample Backtest
        ↓ 
Allocation Stability Index (ASI)
        ↓ 
Crisis Stress Testing
        ↓ 
Fama–French Factor Regression
        ↓ 
Regime Detection (Markov Switching)
        ↓ 
Empirical Results Export
````

---

## 6. Key Methodological Components

### 6.1 Covariance Estimation

Ledoit–Wolf shrinkage is employed to ensure a well-conditioned covariance matrix and to mitigate sampling noise.

### 6.2 Black–Litterman Framework

Expected returns are constructed using Bayesian updating:

* Prior: Market-implied equilibrium returns
* Views: Historical return signals
* Confidence: Controlled via τ parameter

### 6.3 Allocation Stability Index (ASI)

The study introduces a formal instability metric:

[
ASI_t = \sum |w_t - w_{t-1}|
]

This captures **period-to-period allocation drift**, directly linking optimization behavior to turnover.

### 6.4 Transaction Cost Modeling

Portfolio turnover is explicitly mapped into implementation costs, converting gross performance into realistic net returns.

### 6.5 Crisis Stress Testing

Recovery dynamics are measured using a corrected definition:

* Peak reference = portfolio value at crisis start
* Recovery = first return to initial value
* Duration = trading days (not calendar days)

### 6.6 Factor Decomposition

Portfolio returns are decomposed using the Fama–French + Momentum model to distinguish:

* True alpha
* Systematic factor exposure

Factor data is obtained from the **Kenneth French Data Library via pandas_datareader**.

### 6.7 Regime Detection

A Markov-switching model identifies high- and low-volatility states, enabling regime-dependent performance evaluation.

---

## 7. Empirical Findings (Summary)

### 7.1 Risk-Adjusted Performance

| Market | Black–Litterman | Markowitz |
| ------ | --------------- | --------- |
| US     | 0.650           | 0.614     |
| China  | 0.042           | 0.088     |
| India  | 0.356           | 0.440     |

### 7.2 Allocation Stability (ASI)

Black–Litterman consistently produces an **order-of-magnitude reduction in instability**, confirming its structural robustness.

### 7.3 Transaction Costs

High turnover in Markowitz portfolios results in substantial performance erosion, eliminating apparent gross-return advantages.

### 7.4 Crisis Recovery

| Market | BL (Days) | MV (Days) |
| ------ | --------- | --------- |
| US     | 1093      | 1056      |
| China  | 458       | 459       |
| India  | 176       | 176       |

Recovery dynamics are primarily driven by **market exposure**, not optimization methodology.

### 7.5 Factor Exposure

Markowitz exhibits statistically significant **momentum loading**, while Black–Litterman remains factor-neutral.

---

## 8. Repository Structure

```text
config/
core/
models/
backtesting/
analysis/
pipelines/
experiments/
results/
    v1_final_results/
visualization/
tests/
docs/
legacy/
```

---

## 9. Execution Instructions

Install dependencies:

```bash
pip install -r requirements.txt
```

Run full pipeline:

```bash
python -m pipelines.run_tri_market_pipeline
python -m pipelines.run_soe_pipeline
python -m pipelines.run_crisis_analysis
```

---

## 10. Reproducibility

The research pipeline is fully deterministic and reproducible:

* No forward-looking bias
* Chronological execution enforced
* All outputs generated programmatically

All computations are reproducible given identical inputs and parameters.

---

## 11. Runtime Environment

Python Version: 3.11

Core Libraries:

* NumPy
* Pandas
* SciPy
* PyQt6
* yfinance
* pandas_datareader

Data Sources:

* Yahoo Finance (ETF price data)
* Kenneth French Data Library (factor data)

---

## 12. Research Contribution

This study contributes to the literature by:

* Formalizing the Allocation Stability Index (ASI)
* Correcting crisis recovery measurement methodology
* Integrating stability, costs, and regime dynamics into a unified framework
* Providing cross-market empirical validation of Bayesian allocation

---

## 13. Documentation

All supporting material is located in:

```text
docs/
```
* `FINAL_PROJECT_IMPLEMENTATION.md`
* `FINAL_RESEARCH_RESULTS_COMPENDIUM.docx` 
* `Research_Pipeline_Architecture_Documentation.docx`


---

## 14. Citation

Dudi, A. K. (2026).
*Regime-Sensitive Black–Litterman Portfolio Allocation: A Cross-Market Empirical Analysis of Stability, Turnover, and Crisis Resilience.*

---

## 15. License

This project is intended for academic and research use.

```
