# -*- coding: utf-8 -*-
"""Read in the list of future power plants from PDPD7A annex 1.

Created on Tue Feb 13 21:02:36 2018

@author: Alice Principal

FIXME: This file duplicate data_PDP7A.py, except it uses a patched version of annex1.txt
"""

from init import pd, show
# %%  List of planned new plants

PDP7A_annex1 = pd.read_fwf("data/PDP7A/annex1_alt3.txt")

PDP7A_annex1.replace({"fuel": {"ND": "Coal",
                               "NDHD": "Oil",
                               "TBKHH": "Gas",
                               "TD": "BigHydro",
                               "TDTN": "PumpedStorage",
                               "NLTT": "Renewable4",   # Renewable energy (agregate)
                               "TDN": "Renewable4",    # Small hydro
                               "NMDSK": "Renewable4",  # Biomass
                               "DG": "Renewable4",     # Wind
                               "DMT": "Renewable4",    # Solar
                               "DHN": "Nuclear",
                               }},
                     inplace=True
                     )

# show(PDP7A_annex1)

capacity_total_plan = PDP7A_annex1.groupby("fuel").capacity_MW.sum()
show("""
Summary of 2016-2030 new capacity listed in PDP7A annex 1, MW
""")
show(capacity_total_plan)
show("""
*: Backup coal units in case all the renewable sources do not meet the set target (27GW by 2030).
Small hydro not specified, included in Renewable4
Wind, Solar, Biomass not specifed after 2020
""")
