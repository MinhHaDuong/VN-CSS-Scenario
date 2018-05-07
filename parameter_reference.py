# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
"""reference is a Parameter  describing the reference technical and economic environment."""

import sys
import numpy as np

from init import pd, show, YEARS, START_YEAR, END_YEAR, N_YEARS, SOURCES
from Parameter import Parameter

from data_OpenEI import (construction_cost, fixed_operating_cost, variable_operating_cost,
                         heat_rate, heat_price)

from data_IPCC import EMISSION_FACTOR

from plan_baseline import plant_life as plant_accounting_life


# %% CCS technologies

START_PENALTY = 0.30
END_PENALTY = 0.20
energy_penalty = np.linspace(START_PENALTY, END_PENALTY, N_YEARS)
heat_rate["CoalCCS"] = heat_rate["Coal"] * (1 + energy_penalty)
heat_rate["GasCCS"] = heat_rate["Gas"] * (1 + energy_penalty)
heat_rate["BioCCS"] = heat_rate["Biomass"] * (1 + energy_penalty)

show("Heat rate  (Btu/kWh)")
show(heat_rate.round())
show()

heat_price["CoalCCS"] = heat_price["Coal"]
heat_price["GasCCS"] = heat_price["Gas"]
heat_price["BioCCS"] = heat_price["Biomass"]


# %%
"""
Without CCS:
   CO2_emitted = EMISSION_FACTOR_noCCS * production

   CO2_produced = CO2_factor_of_heat * heat_used
   heat_used = production * heat_rate_noCCS
   CO2_produced = CO2_factor_of_heat * production * heat_rate_noCCS

   CO2_produced = CO2_emitted
   CO2_factor_of_heat * production * heat_rate_noCCS = EMISSION_FACTOR_noCCS * production
   CO2_factor_of_heat = EMISSION_FACTOR_noCCS / heat_rate_noCCS

Assume the CO2_factor_of_heat deponds on the fuel only. It is the same with or without CCS.

With CCS:
   CO2_captured = CO2_produced - CO2_emitted

   CO2_emitted = EMISSION_FACTOR_withCCS * production

   CO2_produced = CO2_factor_of_heat * heat_used
   CO2_produced = CO2_factor_of_heat * production * heat_rate_CCS
   CO2_produced = CO2_factor_of_heat * production * heat_rate_noCCS * (1 + energy_penalty)
   CO2_produced = production * EMISSION_FACTOR_noCCS * (1 + energy_penalty)

   CO2_captured = production * capture_factor
   capture_factor = EMISSION_FACTOR_noCCS * (1 + energy_penalty) - EMISSION_FACTOR_withCCS
"""

capture_factor = pd.DataFrame(index=YEARS)
for fuel in SOURCES:
    capture_factor[fuel] = pd.Series(0, index=YEARS)   # gCO2/ kWh

capture_factor["CoalCCS"] = (EMISSION_FACTOR["Coal"] * (1 + energy_penalty)
                             - EMISSION_FACTOR["CoalCCS"])

capture_factor["GasCCS"] = (EMISSION_FACTOR["Gas"] * (1 + energy_penalty)
                            - EMISSION_FACTOR["GasCCS"])

capture_factor["BioCCS"] = (EMISSION_FACTOR["Biomass"] * (1 + energy_penalty)
                            - EMISSION_FACTOR["BioCCS"])

# %%

DISCOUNT_RATE = 0.06

START_CARBON_PRICE = 0
MID1_YEAR = 2020
MID1_CARBON_PRICE = 0
MID2_YEAR = 2030
MID2_CARBON_PRICE = 50
END_CARBON_PRICE = 100

CARBON_PRICE = np.concatenate([np.linspace(START_CARBON_PRICE,
                                           MID1_CARBON_PRICE,
                                           MID1_YEAR - START_YEAR,
                                           endpoint=False),
                               np.linspace(MID1_CARBON_PRICE,
                                           MID2_CARBON_PRICE,
                                           MID2_YEAR - MID1_YEAR,
                                           endpoint=False),
                               np.linspace(MID2_CARBON_PRICE,
                                           END_CARBON_PRICE,
                                           END_YEAR - MID2_YEAR + 1)])

CARBON_PRICE = pd.Series(data=CARBON_PRICE, index=YEARS)


# %%

reference = Parameter(DISCOUNT_RATE,
                      plant_accounting_life,
                      construction_cost[SOURCES],
                      fixed_operating_cost[SOURCES],
                      variable_operating_cost[SOURCES],
                      heat_rate,
                      heat_price,
                      EMISSION_FACTOR,
                      capture_factor,
                      CARBON_PRICE)

reference.__doc__ = ("Reference - median values from OpenEI and IPCC reviews, "
                     + "d=" + str(round(100 * DISCOUNT_RATE)) + "%, "
                     + "CO2=" + str(END_CARBON_PRICE) + "$ in 2050")

if __name__ == '__main__':
    if (len(sys.argv) == 2) and (sys.argv[1] == "summarize"):
        reference.summarize()
