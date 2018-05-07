# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
"""Assess the scenarios."""

import sys

from plan_baseline import baseline
from plan_with_ccs import withCCS
from parameter_reference import reference

from Run import RunPair


if __name__ == '__main__':
    if (len(sys.argv) == 2) and (sys.argv[1] == "summarize"):
        PAIR = RunPair(baseline, withCCS, reference)
        print(PAIR.summary(["Baseline", "High CCS", "difference"]))
