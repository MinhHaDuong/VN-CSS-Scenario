# encoding: utf-8
#
# (c) Minh Ha-Duong, 2017
#     minh.haduong@gmail.com
#     Creative Commons Attribution-ShareAlike 4.0 International
#
#
"""Plot Generation capacity by technology, 1975 - 2050 for both scenarios.

Usage:
   python3 figure-capacities.py plot filename.[pdf|png|...]

The output formats available depend on the backend being used.
"""

import sys
import matplotlib.pyplot as plt

from init import MW, GW, plant_type
from plan_baseline import baseline
from plan_with_ccs import withCCS


def plot_capacity_mix(plan, ax, sources_toshow):
    """Line plot a power development history.

    History includes past <2015, plan up to 2030 and scenario up to 2050.
    """
    mix = (plan.capacities[sources_toshow] * MW / GW)
    colors = ["k", '0.75', "y", "b", "c", "g", "m", "r", "k", "0.75", "g"]
    lines = ["-", '-', "-", "-", "-", "-", "-", "-", "--", "--", "--"]
    plt.ylabel('GW')
    mix.plot(ax=ax, title=str(plan), color=colors, style=lines, linewidth=4.0)
    ax.axvline(2015, color="k")
    ax.axvline(2030, color="k")


fig, axarr = plt.subplots(2, 1, figsize=[8, 12])
fig.suptitle("Generation capacity by plant type, 1975 - 2050", fontsize=15)

plot_capacity_mix(baseline, axarr[0], plant_type[0:8])

plot_capacity_mix(withCCS, axarr[1], plant_type)

fig.tight_layout()
plt.subplots_adjust(top=0.94)

if __name__ == '__main__':
    if (len(sys.argv) == 3) and (sys.argv[1] == "plot"):
        fig.savefig(sys.argv[2])
