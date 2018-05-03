# encoding: utf-8
#
# (c) Minh Ha-Duong  2017-2018
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
# With contribution from Alice Duval, CIRED
#


"""Define a power development plan with generating as much from gas as from coal.

Each year, the new capacity from gas and from coal are the same.
The electricity produced per year is the less than in the baseline scenario,
because capacity factor is lower and plant lifetime is shorter for gas than for coal.
"""

import sys

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
moreGas.__doc__ = "Install as much gas power new capacity as coal power new capacity."

if __name__ == '__main__':
    if (len(sys.argv) == 2) and (sys.argv[1] == "summarize"):
        moreGas.summarize()
    if (len(sys.argv) == 3) and (sys.argv[1] == "plot"):
        moreGas.plot_plan(sys.argv[2])
