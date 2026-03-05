import traceback
import empirical_study

try:
    empirical_study.run_market_pipeline('CHINA', empirical_study.MARKET_CONFIG['CHINA'])
except Exception as e:
    with open('error_log.txt', 'w') as f:
        traceback.print_exc(file=f)
    print("Error written to error_log.txt")
