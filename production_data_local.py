# -*- coding: utf-8 -*-
"""Initialize local coal and gas production time series.

Created on Mon Jan  8 11:31:01 2018

@author: Alice Duval

Productions are in 1000t for Coal and in Million M3 for Gas.
"""

import numpy as np
from scipy.interpolate import lagrange
from init import pd, START_YEAR, END_YEAR, CALORIFIC_POWER, kt, MM3

#Collect of data
local_production_data = pd.read_csv(
    "data/Oil_Gas_prices/data_production_local.csv",
    index_col=0)
local_production_data.columns = ["Coal", "Gas"]

x = np.array(local_production_data.index)
y_coal = np.array(local_production_data.Coal) * kt * CALORIFIC_POWER["Coal_local"]
y_gas = np.array(local_production_data.Gas) * MM3 * CALORIFIC_POWER["Gas_local"]

#interpolation of data with a langrangian polynom

function_production_coal = lagrange(x, y_coal)
function_production_gas = lagrange(x, y_gas)

interpol_coal_production = []
interpol_gas_production = []

#Saving interpolating data

for i in range(START_YEAR, END_YEAR + 1):
    if i <= 2030:
        interpol_coal_production.append(round(function_production_coal(i), 0))
        interpol_gas_production.append(round(function_production_gas(i), 0))
    else:
        interpol_coal_production.append(interpol_coal_production[-1])
        interpol_gas_production.append(interpol_gas_production[-1])

local_production = pd.DataFrame({
    'Coal': interpol_coal_production,
    'Gas': interpol_gas_production},
    index=range(START_YEAR, END_YEAR + 1))
