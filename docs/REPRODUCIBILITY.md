# Reproducibility

Python 3.12 and requirements-phase1-lock.txt record the executed numerical environment. Existing LICENSE is retained. No vendor dataset license is inferred.

## Public checks

From repository root, install the lock and run the commands in README. `python -m scripts.validate_publication` checks public evidence hashes, labels and principal-value checkpoints. `python -m scripts.phase3_final_results --validate-only` validates the frozen tables/figures using committed source records. Unit tests use synthetic fixtures and mocks; they do not reproduce the historical manuscript.

## Frozen inputs and restricted reproduction

[Four exact identifiers and hashes](../outputs/final_professor_challenge_resolution/stage_c_input_availability.csv) describe the three Yahoo Finance adjusted-price snapshots and processed Kenneth French factor cache. They are retained locally under ignored results/generated paths, excluded from the public tree. `python -m scripts.validate_publication --private-inputs` verifies their bytes without downloading data. Obtain provider observations through authorized access; public access does not establish redistribution permission. Later vintages may differ. The factor cache is decimal, not source percent.

The original revised-study execution entry point is `python -m pipelines.phase2_experiments --help`. It documents its output-directory option; actual execution requires private hash-matched snapshots and will refuse to overwrite an existing run. The full original backtests are not repeated during publication validation. Main configuration is config/project_config.yaml. The Phase 1 pipeline can download if caches are missing; do not invoke it to pretend to reproduce absent frozen inputs.

## Tables and figures without research reruns

`python -m scripts.phase3_final_results --output-dir results/generated/publication-rebuild` rebuilds publication CSVs and figures from committed evidence; it does not download prices or optimize portfolios. Choose a new directory on subsequent runs. The current authoritative files remain in results/phase3_final to preserve manifest references. Final professor diagnostics remain in outputs/final_professor_challenge_resolution with source scripts under scripts/final_audit. These scripts are archival stage entry points with sequential assumptions, not a single idempotent public build command; do not rerun them merely to confirm a reported value.

The verified baseline is e666afabe596e88973a67b3bbf7ff2be3c938af4. Phase 3 manifests identify source commits, Phase 1/2 run IDs and output fingerprints. Internal frozen-input reproduction, independently acquired later data, and exact reproduction of the original March working paper are three different claims. Missing original March priors, vintages and ownership inputs prevent the last claim. [Research history](RESEARCH_HISTORY.md).
