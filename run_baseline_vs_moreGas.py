# encoding: utf-8
#
# (c) Minh Ha-Duong  2018
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
"""Compare the baseline vs. the more gas scenario.

Coal and gas are costed at domestic prices."""

import sys

from plan_baseline import baseline
from plan_moreGas import moreGas
from parameter_reference import reference

from Run import RunPair


if __name__ == '__main__':
    if (len(sys.argv) == 2) and (sys.argv[1] == "summarize"):
        print("""
******************************************
***             Results                ***
******************************************
""")
        PAIR = RunPair(baseline, moreGas, reference)
        print(PAIR.summary(["Baseline", "More gas", "difference"]))
