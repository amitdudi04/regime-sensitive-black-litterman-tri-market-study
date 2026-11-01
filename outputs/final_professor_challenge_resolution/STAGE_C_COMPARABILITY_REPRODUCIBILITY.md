# Stage C comparability and reproducibility

## C1 common-calendar robustness

stage_c_common_period.csv intersects actual stored return dates: 2014-11-07 through 2024-12-31, 2553 sessions, net 10 bps per L1. Strategies and original training schedules remain unchanged. Wealth is rebased to 1 immediately before the evaluation slice; original trade charges inside the slice are retained, without a newly imposed initial deployment. This is a conditional common-period comparison, not a new deploy-on-start strategy. ASI includes changes whose current decision falls within the interval, using its actual previous target even if earlier; turnover is the actual in-period trade excluding original initial deployment. Each metric has its decision count. Cross-market calendar matching does not equalize exposures or establish country causality. RESOLVED_WITH_LIMITATIONS.

## C2 ETF and currency interpretation

All assets are US-listed USD-traded ETFs. Labels describe underlying national exposures; USD investor returns include any embedded currency translation and fund design. They are not local-currency national index returns. Constituent overlaps remain. No isolated currency factor or domestic market-efficiency effect is identified. Existing manuscript caveats are correct and should remain. INHERENT_RESEARCH_LIMITATION; RESOLVED_WITH_LIMITATIONS.

## C3 turnover and fees

At rebalance k, drifted pretrade holdings h have sum 1; target w has sum 1. L1 T=sum abs(w-h); purchases equal sales, so one-way turnover=T/2. Initial cash deployment is special: purchases=1, sales=0, T_initial=1; do not halve that charge mechanically. Current net growth=(1+r_gross)(1-c_L1 T). To charge the identical rebalance fee using half-L1 q=T/2 requires c_oneway=2 c_L1. A quoted 10 bps per L1 equals 20 bps per half-L1 on fully invested rebalances. This is a proportional weight-cost convention, not an implicit dollar fee-funding solver.

Analytical implementation check: pretrade [0.6,0.4] to target [0.5,0.5] gives T=0.2, purchases=sales=0.1. At c=0.001 fee fraction=0.0002. Gross return .02 gives net growth 1.019796 (net return .019796). Initial deployment turnover=1. All assertions passed against actual _l1_turnover and apply_costs. Direct fees sum pretrade net NAV times fee fraction. Terminal wealth impact also includes foregone future growth and differs from total direct fees. No model change. RESOLVED.

## C4 frozen inputs

All four snapshots exist privately and match archived hashes. Exact identifiers, provider, retrieval timestamps and SHA-256 are in stage_c_input_availability.csv. No raw datasets are included in this public package. Redistribution permission is not established. Independent researchers must obtain access under provider terms; this audit does not certify a license or legal right to redistribute. No new data downloaded.

Reproduction: use pinned requirements-phase1-lock.txt, exact archived source commits and configurations in the run manifests; acquire Yahoo Finance adjusted-close observations for the stated ETFs and Kenneth French daily FF3/momentum factors through authorized access. Align common observed dates within each basket; do not fill missing observations. Factor source percentages convert once to decimals. Compare acquired bytes and metadata with archived hashes before claiming exact reproduction. Later provider vintages can differ. Equivalent newly acquired data can test the revised specification but cannot by themselves reproduce the frozen experiment. March price vintages, priors and ownership inputs remain unavailable; revised-specification reproducibility and March reproduction are separate claims. RESOLVED_WITH_LIMITATIONS.
