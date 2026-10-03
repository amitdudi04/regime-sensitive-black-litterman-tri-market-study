# Canonical Research Architecture

## Objective

The canonical path is designed so that a reviewer can trace any recomputed result from input data through the exact transformation that produced it.

## Pipeline

Observed ETF prices  
→ core/data_loader.py  
→ common observed dates, no price forward-fill  
→ core/return_calculations.py  
→ simple returns for portfolio P&L  
→ backtesting/paper_backtest.py  
→ 252-day rolling training window  
→ Ledoit-Wolf covariance  
→ BL posterior / historical-mean Markowitz  
→ same optimizer and constraints  
→ drift-adjusted turnover  
→ proportional transaction cost  
→ pipelines/paper_v1_pipeline.py  
→ market summaries, dataset manifest, US factor analysis  
→ results/recomputed/  
→ scripts/generate_research_figures.py

## Supporting analysis

- analysis/factor_regression.py: Kenneth French US MKT/SMB/HML/MOM regression with HAC inference.
- analysis/regime_detection.py: two-state Markov-switching classification for ex-post conditional analysis.
- analysis/statistical_tests.py: bootstrap and Sharpe-difference diagnostics.
- analysis/soe_private_analysis.py: ownership-segmentation/descriptive helper.
- backtesting/crisis_freeze.py: freezes the last pre-crisis target-weight vector across a specified crisis window.

## Output policy

- results/reference/ contains values reported in the existing working paper.
- results/recomputed/ contains machine-generated outputs from the cleaned code.
- Reference and recomputed outputs are not silently mixed.

## Historical code policy

The old GUI, old dual-market engine, archived experiment snapshots and legacy modules were removed from the default branch because they used different assumptions and, in some cases, indefensible fallbacks or stale result families.

They remain recoverable in Git history and the dedicated historical branch.
