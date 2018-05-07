# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#


"""Define a power plan with CCS.

Coal-fired power plants do dominate the generation sector of Vietnam from 2020 onward.
The total capacity of coal-fired power plants would increase to 55 GW by 2030.
CCS finally takes off in the international context, as China, Australia, South Africa
and a few other countries consider it a Nationally Appropriate Mitigation Action.
This reduces the technical barriers, and drives down the costs of CCS technology to a point where
an affluent Vietnam can afford it by 2040.
Vietnam and other countries in the region benefits CCS capacity building programs
from IEA, ASEAN, APEC and industry associations.

In this scenario, storage activities are still initially driven by the oil industry,
who seeks to extend the end life of offshore oilfield by CO2 flooding.
But the government plays a central role early on. Incentive systems (e.g. taxes, subsidy ...)
are implemented, as soon as 2020 for R&D, to setup a pilot project, with the goal to have
a commercial scale demonstrator by 2035. In parallel, the government announces that
coal fired power plants build after 2020 will have to be capture-ready.
The electricity generation sector is an active player for CO2 transport activities.

Usage:

python3 plan_with_ccs.py summarize
python3 plan_with_ccs.py plot filename.[pdf|png|...]
"""

import sys

from init import pd, END_YEAR, technologies
from Plan import Plan

from plan_baseline import baseline

# %%

additions, retirement = baseline.additions.copy(), baseline.retirement.copy()

# %%

PILOT1_YEAR = 2024
PILOT1_SIZE = 250  # MW of gas-fired generation
assert(additions.at[PILOT1_YEAR, "Gas"] > PILOT1_SIZE)
additions.at[PILOT1_YEAR, "Gas"] -= PILOT1_SIZE
additions.at[PILOT1_YEAR, "GasCCS"] += PILOT1_SIZE

PILOT2_YEAR = 2029
PILOT2_SIZE = 750  # MW of gas-fired generation
assert(additions.at[PILOT2_YEAR, "Gas"] > PILOT2_SIZE)
additions.at[PILOT2_YEAR, "Gas"] -= PILOT2_SIZE
additions.at[PILOT2_YEAR, "GasCCS"] += PILOT2_SIZE

# %%

RETROFIT_START_YEAR = 2035
assert RETROFIT_START_YEAR > PILOT2_YEAR

RETROFIT_PERIOD = range(RETROFIT_START_YEAR, END_YEAR + 1)

# Convert all other coal capacity to Coal CCS on 2035 - 2050
retrofit_rate_coal = baseline.capacities.at[END_YEAR, "Coal"] / len(RETROFIT_PERIOD)
retirement.loc[RETROFIT_PERIOD, "Coal"] += retrofit_rate_coal
additions.loc[RETROFIT_PERIOD, "CoalCCS"] = retrofit_rate_coal

# Convert all other Gas capacity to Gas CCS on 2035 - 2050
retrofit_rate_gas = ((baseline.capacities.at[END_YEAR, "Gas"] - PILOT1_SIZE - PILOT2_SIZE
                     - additions.loc[RETROFIT_PERIOD, "Gas"].sum()
                      ) / len(RETROFIT_PERIOD))
retirement.loc[RETROFIT_PERIOD, "Gas"] += retrofit_rate_gas
additions.loc[RETROFIT_PERIOD, "GasCCS"] = retrofit_rate_gas

# Install new Gas CCS plants instead of simple Gas
additions.loc[RETROFIT_PERIOD, "GasCCS"] += additions.loc[RETROFIT_PERIOD, "Gas"]
additions.loc[RETROFIT_PERIOD, "Gas"] = 0

# Ramp up some BioCCS, quadratically
BIOCCS_TREND = 10    # The increase of annual capacity installed (MW / yr)
bioCCS_2050 = BIOCCS_TREND * len(RETROFIT_PERIOD)
bioCCS_ramp = pd.Series(range(0, bioCCS_2050, BIOCCS_TREND),
                        RETROFIT_PERIOD)
additions.loc[RETROFIT_PERIOD, "BioCCS"] = bioCCS_ramp

# Save a bit on Gas CCS, keeping the END_YEAR generation unchanged
savedGasCCS = (bioCCS_ramp
               * baseline.capacity_factor.at[END_YEAR, "BioCCS"]
               / baseline.capacity_factor.at[END_YEAR, "GasCCS"])
additions.loc[RETROFIT_PERIOD, "GasCCS"] -= savedGasCCS


withCCS = Plan(additions, retirement[technologies],
               baseline.capacity_factor, baseline.net_import)
withCCS.__doc__ = "With CCS"

if __name__ == '__main__':
    if (len(sys.argv) == 2) and (sys.argv[1] == "summarize"):
        withCCS.summarize()
    if (len(sys.argv) == 3) and (sys.argv[1] == "plot"):
        withCCS.plot_plan(sys.argv[2])

#print(withCCS)
#
#withCCS.summarize()
#print(repr(withCCS))

#withCCS.plot_plan("withCCS.pdf")
