# -*- coding: utf-8 -*-
"""Initialize local coal and gas prices time series.

Created on Fri Dec 15 14:46:03 2017

@author: Alice Duval

Prices are in $/T (in 2017 US dollars) for Coal and in $/MM3 for Gas.

"""

import numpy as np
from scipy.interpolate import lagrange
from init import pd, START_YEAR, END_YEAR, MBtu, t, CALORIFIC_POWER

#Collect of data
local_prices_data = pd.read_csv("data/Oil_Gas_prices/data_prices_local.csv", index_col=0)

local_prices_data.columns = ["Coal", "Gas"]

x_coal = np.array(local_prices_data.index)
y_coal = np.array(local_prices_data.Coal) / (CALORIFIC_POWER["Coal_local"] * t)

#Gas plannification is until 2025: 2030 gas price is assumed to be the same than in 2025. To find
#Gas price langrangian polynomn coefficients, we consider the period 2015 - 2025
x_gas = np.delete(x_coal, -1)
y_gas = np.array(local_prices_data.Gas) / (MBtu)
y_gas = np.delete(y_gas, -1)

#interpolation of data with a langrangian polynom
FUNCTION_PRICE_COAL = lagrange(x_coal, y_coal)
function_price_gas = lagrange(x_gas, y_gas)
interpol_coal_price = []
interpol_gas_price = []
index = []

#Saving interpolating data
#for i in range(2030-START_YEAR+1):
for i in range(START_YEAR, END_YEAR + 1):
    if i <= 2025:
        interpol_coal_price.append(FUNCTION_PRICE_COAL(i))
        interpol_gas_price.append(function_price_gas(i))
    elif i <= 2030:
        interpol_coal_price.append(FUNCTION_PRICE_COAL(i))
        interpol_gas_price.append(interpol_gas_price[-1])
    else:
        interpol_coal_price.append(interpol_coal_price[-1])
        interpol_gas_price.append(interpol_gas_price[-1])

local_prices = pd.DataFrame({'Coal': interpol_coal_price,
                             'Gas': interpol_gas_price},
                            index=range(START_YEAR, END_YEAR + 1))
