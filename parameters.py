# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#
import pandas as pd
from data import PDP7A_annex1, capacities_PDP7A, past_capacity_added


#%%

past_capacity_added["Renewable"] = (past_capacity_added.Biofuel
                                    + past_capacity_added.SmallHydro
                                    + past_capacity_added.Wind)

past_capacity_added.drop(["Biofuel", "SmallHydro", "Wind"], axis=1, inplace=True)

#print("""
#Vietnam historical generation capacity by fuel type (MW)
#Renewable includes small hydro, biofuel, wind (there is no solar capacity)
#""")
#print(past_capacity_added.cumsum())
#print()

#
# define the baseline scenario
#


print("""
***** Baseline scenario *****
Based on PDP7A for 2016 onwards
Renewable includes small hydro
Nuclear replaced by Coal
Coal plants proposed as backup for renewables not included
""")

# The National Assembly voted to cancel the nuclear program
# ASSUMPTION: Planned Nuclear electricity generation capacity is replaced by Coal
baseline = PDP7A_annex1.replace({"fuel": {"Nuclear": "Coal"}})

baseline = baseline.groupby(["year", "fuel"]).capacity_MW.sum()
baseline = baseline.unstack()
baseline = pd.concat([past_capacity_added, baseline])
baseline = baseline.fillna(0)
# ASSUMPTION: no need for the backup thermal, renewables will be installed as per the plan
baseline.drop("ND*", axis=1, inplace=True)

print("Vietnam annual generation capacity addition by fuel type (MW)")
print(baseline)
print()

print("Vietnam generation capacity by fuel type (MW)")
print(baseline.cumsum())
print()

#%% Check the capacity numbers vs. PDP7A objectives

print(baseline.cumsum().loc[[2020, 2025, 2030]])

print(capacities_PDP7A)

print("""
Relative error""")
print((baseline.cumsum().loc[[2020, 2025, 2030]] - capacities_PDP7A) / capacities_PDP7A)

#FIXME: The relative error on Hydro is big

#%%

"""Input parameters of the model"""

discount_rate = {0, 0.05, 0.08, 0.12}
