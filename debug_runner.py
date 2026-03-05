import traceback
try:
    import run_soe_pipeline
    run_soe_pipeline.main()
except Exception as e:
    with open('results/trace.txt', 'w') as f:
        f.write(traceback.format_exc())
