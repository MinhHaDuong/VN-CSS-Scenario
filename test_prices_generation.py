# -*- coding: utf-8 -*-
"""Test the functions determining coal and gas prices.

Created on Sat Feb 10 22:18:16 2018

@author: Alice Duval
"""
from random import randint
import numpy as np

from price_fuel import price_fuel
from prices_data_local import local_prices
from plan_baseline import baseline
from prices_data_international import price_gas, price_coal
from production_data_local import local_production
from parameter_reference import heat_rate
from init import pd, START_YEAR, END_YEAR


def test_international_dependency():
    """Check that if all the production is imported, the average price is equal to the
    international price."""

    # Local production is null
    production = [0] * (END_YEAR + 1 - START_YEAR)
    nul_production = pd.DataFrame({
        'Coal': production,
        'Gas': production},
        index=range(START_YEAR, END_YEAR + 1))

    # Generate random local prices to test the independence of the result
    local_price_gas = []
    local_price_coal = []
    for _ in range(START_YEAR, END_YEAR + 1):
        local_price_gas.append(randint(0, 100))
        local_price_coal.append(randint(0, 100))

    local_prices_compare = pd.DataFrame({
        'Coal': local_price_coal,
        'Gas': local_price_gas},
        index=range(START_YEAR, END_YEAR + 1))

    #Create the two objects to compare
    np.random.seed(0)
    fuel_1 = price_fuel(local_prices, price_gas, price_coal, nul_production, baseline)
    np.random.seed(0)
    fuel_2 = price_fuel(local_prices_compare, price_gas, price_coal, nul_production, baseline)

    assert fuel_1.average_price["Coal"].all() == fuel_2.average_price["Coal"].all()
    assert fuel_1.average_price["Gas"].all() == fuel_2.average_price["Gas"].all()


def test_local_dependency():
    """Check that if all the production is local, the average price is equal to the
    local price."""
    # Local production is equal to energy needs. There is no importation
    electric_production = baseline.production[['Coal', 'Gas']].loc[START_YEAR:END_YEAR + 1]
    useful_heat_rate = heat_rate[['Coal', 'Gas']]

    needed_production = pd.DataFrame(
        electric_production.values * useful_heat_rate.values,
        columns=useful_heat_rate.columns,
        index=useful_heat_rate.index)
    # Generate random international prices to test the independence of the result
    past_price_gas = []
    past_price_coal = []
    for _ in range(1970, 2016):
        past_price_coal.append(randint(1, 100))
    for _ in range(1977, 2016):
        past_price_gas.append(randint(1, 100))
    price_gas_compare = pd.DataFrame({'Price_Gas': past_price_gas}, index=range(1977, 2016))
    price_coal_compare = pd.DataFrame({'Price_Coal': past_price_coal}, index=range(1970, 2016))

    #Create the two objects to compare
    np.random.seed(0)
    fuel_1 = price_fuel(local_prices, price_gas, price_coal, needed_production, baseline)
    np.random.seed(0)
    fuel_2 = price_fuel(local_prices, price_gas_compare, price_coal_compare, needed_production,
                        baseline)
    assert fuel_1.average_price["Gas"].all() == fuel_2.average_price["Gas"].all()
    assert fuel_1.average_price["Coal"].all() == fuel_2.average_price["Coal"].all()


def test_between_two_values():
    """Check that the averaged price is between the local value and the international value."""
    fuel_1 = price_fuel(local_prices, price_gas, price_coal, local_production, baseline)
    averaged = fuel_1.average_price["Gas"].all()
    prices = pd.concat([fuel_1.import_prices["Gas"], local_prices["Gas"]], axis=1)
    lower = prices.min(axis=1).all()
    upper = prices.max(axis=1).all()
    assert lower <= averaged <= upper
