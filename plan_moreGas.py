# encoding: utf-8
#
# (c) Minh Ha-Duong  2017-2018
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
# With contribution from Alice Duval, CIRED
#


"""Define a power development plan with generating as much from gas as from coal.

Each year, the same amount of new capacity from gas and from coal are the same.
The electricity produced per year is the less than in the baseline scenario,
because for gas capacity factor is lower and plant lifetime shorter.
"""

import sys

from init import pd, VERBOSE, show
from init import fuels, addcol_Renewable4

from data_past import capacity_past, capacity_factor_past, capacity_2015_EVN

from data_PDP7A import (capacities_PDP7A, capacity_total_plan, capacity_factor_PDP7A)

from PowerPlan import PowerPlan
from plan_baseline import (additions as baseline_additions,
                           retirement as baseline_retirement,
                           capacityfactor, net_import)

# %%

additions = baseline_additions.copy()
additions["Coal"] = (additions["Coal"] + additions["Gas"]) / 2
additions["Gas"] = additions["Coal"]

retirement = baseline_retirement.copy()
retirement["Coal"] = (retirement["Coal"] + retirement["Gas"]) / 2
retirement["Gas"] = retirement["Coal"]

#%% Main statement

moreGas = PowerPlan(additions, retirement, capacityfactor, net_import)
moreGas.__doc__ = "As much gas power as coal power."

if __name__ == '__main__':
    if (len(sys.argv) == 2) and (sys.argv[1] == "summarize"):
        moreGas.summarize()
    if (len(sys.argv) == 3) and (sys.argv[1] == "plot"):
        moreGas.plot_plan(sys.argv[2])

# %% Validation: compares to PDP7A

show("""
*****************************************************
***     Comparing our baseline with PDP7          ***
*****************************************************
""")

compared = ["Coal", "Gas", "BigHydro", "Renewable4", "Nuclear"]

tocompare = moreGas.capacities.loc[[2020, 2025, 2030]]
tocompare["Gas"] = tocompare.Gas + tocompare.Oil
tocompare["Nuclear"] = 0
addcol_Renewable4(tocompare)
tocompare = tocompare[compared]

relerror = (tocompare - capacities_PDP7A) / capacities_PDP7A
relerror = relerror[compared]

show("PDP7A")
show(capacities_PDP7A[compared])
show()
show("Baseline scenario, Gas includes Oil")
show(tocompare)
show()
show("Relative error")
show(relerror)
show("Note: Gas 2030 is larger in baseline because we replace nuclear with gas")


#%% Compares PDP7A

cap_2015_implicit = capacities_PDP7A.loc[2030] - capacity_total_plan

cap_2015_implicit.dropna(inplace=True)

comparison = pd.DataFrame([capacity_2015_EVN, cap_2015_implicit],
                          index=["Total from EVN report", "Implicit in PDP7A decision"])

capacity_closed = pd.Series(comparison.iloc[0] - comparison.iloc[1], name="Diff ?Closed capacity?")

comparison = comparison.append(capacity_closed)

capacity_old = pd.Series(capacity_past.cumsum().loc[1980], name="Installed before 1980")

comparison = comparison.append(capacity_old)

show("Coherence of 2015 Generation capacity numbers")
show(comparison[fuels])

show("""
Some coal, gas, oil and hydro capacities listed in the EVN report historical table are
not accounted for in the PDP7A current capacity total
The order of magnitude corresponds to capacities installed before 1985,
which in all probability are already closed or will be before 2030.

Gas capacity in EVN report includes the Tu Duc and Can Tho oil-fired gas turbines (264 MW)
""")


if VERBOSE:
    cf = pd.concat([capacity_factor_past, capacity_factor_PDP7A])
    cf = cf.where(cf < 1)
    cf = cf[["Coal", "Gas", "Hydro", "Renewable"]]
    ax = cf.plot(ylim=[0, 1], xlim=[1995, 2030],
                 title="Power generation capacity factors by fuel type")
    ax.axvline(2015, color="k")


#b = production_past[fuels].astype("int64")
#
#show("Past - Electricity production (GWh)")
#show(b)
#show()
#
#
#relerr = ((production_baseline - b) / b).loc[1990:2015]
#show("Relative error")
#show(relerr)

#%% Fuel use
#
#MtCoal_per_GWh = fuel_use_PDP7A.Coal / production_PDP7A.Coal
#
#show(MtCoal_per_GWh)
#
#a = MtCoal_per_GWh[2020]
#b = MtCoal_per_GWh[2025]
#da = (b - a) / 5
#c = MtCoal_per_GWh[2030]
#db = (c - b) / 5
#s = pd.Series(name="Coal",
#              data=np.concatenate([np.arange(a - 10 * da, b, da),
#                                   np.arange(b, c + 21 * db, db)]),
#              index=range(2010, 2051))
#
#show(s)
#
#coal_use_baseline = s * production_baseline.Coal.loc[2010:]
#
#show(fuel_use_PDP7A.Coal)
#show(coal_use_baseline)
#
