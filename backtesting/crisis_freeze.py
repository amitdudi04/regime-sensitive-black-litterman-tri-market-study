import pandas as pd

def define_crisis_intervals():
    """
    Returns strict timestamps tracing historical crisis liquidity freezes.
    """
    return {
        '2008_US_GFC': ('2008-08-01', '2009-03-09'),
        '2015_China_Crash': ('2015-06-01', '2016-02-01'),
        '2020_India_Covid': ('2020-02-15', '2020-05-01')
    }

def execute_crisis_freeze(full_weights_df, crisis_start, crisis_end):
    """
    Freeze portfolio weights precisely before crisis events and lock them throughout
    the duration of the structural dislocation to observe static drawdown profiles.
    """
    # Extract the static vector generated exactly prior to the crash trigger
    pre_crash_weights = full_weights_df.loc[:crisis_start].iloc[-1]
    
    # Broadcast that static vector across the full crisis timeline (no rebalancing)
    crisis_weights = pd.DataFrame(
        [pre_crash_weights.values] * len(full_weights_df.loc[crisis_start:crisis_end]),
        index=full_weights_df.loc[crisis_start:crisis_end].index,
        columns=full_weights_df.columns
    )
    
    return crisis_weights
