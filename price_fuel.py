# -*- coding: utf-8 -*-
"""Generate a model parameter object, with a random trajectory of coal and gas prices.

Created on Mon Jan  8 16:54:44 2018

@author: Alice Duval
price_fuel class deals with different prices and quantity of ressources needed, and generate new
prices parameters for the model.

FIXME: This approach breaks the independence between parameters and scenarios,
since it weights imported and domestic fuel price to compute an average price.
Better to have explicit fuels types in the model.
"""
import sys

import numpy as np
import matplotlib.pyplot as plt
from init import pd, start_year, end_year, sources, MBtu

from plan_baseline import baseline
from plan_moreGas import moreGas

from param_reference import discount_rate, plant_accounting_life, construction_cost
from param_reference import fixed_operating_cost, variable_operating_cost, heat_rate, heat_price
from param_reference import emission_factor, capture_factor, carbon_price

from prices_data_local import local_prices
from prices_data_international import import_prices_path, price_coal, price_gas
from production_data_local import local_production

from Parameter import Parameter


class price_fuel():
    """An average price for fuels."""

    def __init__(self, loc_prices, past_price_gas, past_price_coal, loc_production, scenario):

        self.index = list(range(start_year, end_year + 1))
        self.loc_prices = loc_prices
        self.import_prices = import_prices_path(past_price_gas, past_price_coal).import_prices
        self.loc_production = loc_production
        self.scenario = scenario   # TODO: pass as argument then disgard

        #Qualify what importation have to be done (in Btu)
        self.needed_production = self.needed_energy()
        self.needed_importation = self.importation()
        self.average_price = self.price_calculation()
        self.parameters = self.generate_parameters()

    def needed_energy(self):
        """Return the amount of heat energy from gas and coal needed for the scenario (MBtu)."""
        electric_energy = self.scenario.production[['Coal', 'Gas']].loc[start_year:end_year + 1]
        useful_heat_rate = heat_rate[['Coal', 'Gas']]
        needed_production = pd.DataFrame(
            electric_energy.values * useful_heat_rate.values,
            columns=useful_heat_rate.columns,
            index=useful_heat_rate.index)
        needed_production["Coal"] = needed_production["Coal"] * MBtu
        needed_production["Gas"] = needed_production["Gas"] * MBtu
        return needed_production

    def importation(self):
        """Calculate fuel quantities that have to be imported for the electric system."""
        importation = pd.DataFrame(columns=['Coal', 'Gas'], index=self.index)
        importation["Coal"] = self.needed_production["Coal"] - self.loc_production["Coal"]
        importation["Gas"] = self.needed_production["Gas"] - self.loc_production["Gas"]
        #Importation needs < 0 means that there is not any importation.
        #Negative values are replaced by 0
        importation[importation < 0] = 0
        return importation

    def price_calculation(self):
        """Return Coal and Gas cost in USD/Btu, by weight-averaged domestic and import costs."""
        #If there is not any importation, local price is considered
        average_price = pd.DataFrame(columns=['Coal', 'Gas'], index=self.index, dtype=float)
        average_price['Coal'] = np.where(
            self.needed_importation['Coal'] == 0,
            self.loc_prices['Coal'],
            (self.loc_production['Coal'] * self.loc_prices['Coal'] +
             self.needed_importation['Coal'] * self.import_prices['Coal']) /
            (self.needed_production['Coal']))
        average_price['Gas'] = np.where(
            self.needed_importation['Gas'] == 0,
            self.loc_prices['Gas'],
            (self.loc_production['Gas'] * self.loc_prices['Gas'] +
             self.needed_importation['Gas'] * self.import_prices['Gas']) /
            (self.needed_production['Gas']))
        return average_price

    def generate_parameters(self):
        """Generate parameters with different international prices forecasts at each run."""
        updated_heat_price = pd.DataFrame(columns=heat_price.columns, index=heat_price.index)

        for fuel in sources:
            if fuel == "Coal" or fuel == "Gas":
                updated_heat_price[fuel] = self.average_price[fuel] * MBtu
            else:
                updated_heat_price[fuel] = heat_price[fuel]

        updated_parameter = Parameter(discount_rate,
                                      plant_accounting_life,
                                      construction_cost[sources],
                                      fixed_operating_cost[sources],
                                      variable_operating_cost[sources],
                                      heat_rate,
                                      updated_heat_price,
                                      emission_factor,
                                      capture_factor,
                                      carbon_price)
        return updated_parameter

    def plot_coal_supply(self, ax):
        """Describe Coal supply of the electric system."""
        (self.needed_production['Coal'] / MBtu).plot(
            ax=ax,
            title="Coal supply for the electric system (MMBTu) in \n" + str(self.scenario) + '\n',
            label="Coal needs")
        (self.loc_production["Coal"] / MBtu).plot(ax=ax, label="Coal producted in Vietnam")
        (self.needed_importation["Coal"] / MBtu).plot(ax=ax, label="Coal imported")

    def plot_coal_price(self, ax):
        """Describe Coal price of the electric system."""
        (self.average_price['Coal'] * MBtu).plot(
            ax=ax,
            title="Coal price (USD/MMBTu) in \n" + str(self.scenario) + '\n',
            label="Average price of Coal for the electric system")
        (self.loc_prices['Coal'] * MBtu).plot(ax=ax, label="Coal produced in Vietnam")
        (self.import_prices["Coal"] * MBtu).plot(ax=ax, label="Imported Coal (Australia)")

    def plot_gas_supply(self, ax):
        """Describe Gas supply of the electric system."""
        (self.needed_production['Gas'] / MBtu).plot(
            ax=ax,
            title="Gas supply for the electric system (MMBTu) in \n" + str(self.scenario) + '\n',
            label="Gas needs")
        (self.loc_production["Gas"] / MBtu).plot(ax=ax, label="Gas producted in Vietnam")
        (self.needed_importation["Gas"] / MBtu).plot(ax=ax, label="Gas imported")

    def plot_gas_price(self, ax):
        """Describe Gas price of the electric system."""
        (self.average_price['Gas'] * MBtu).plot(
            ax=ax, title="Gas price (USD/MMBTu) in \n" + str(self.scenario) + '\n',
            label="Average price of Gas for the electric system")
        (self.loc_prices['Gas'] * MBtu).plot(ax=ax, label="Gas produced in Vietnam")
        (self.import_prices["Gas"] * MBtu).plot(ax=ax, label="Imported Gas (Japan)")

    def plot_information(self, filename):
        """Gather gas and coal information of the electric system."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2,
                                                     sharex='row', sharey='none',
                                                     figsize=[15, 10])
        self.plot_gas_price(ax1)
        ax1.legend(loc='upper left')
        ax1.set_ylabel('2010 USD / MMBtu')
        self.plot_gas_supply(ax2)
        ax2.legend(loc='upper left')
        ax2.set_ylabel('MMBtu')
        ax2.set_ylim([0, 1.6 * 10**9])
        self.plot_coal_price(ax3)
        ax3.legend(loc='upper left')
        ax3.set_ylabel('2010 USD / MMBtu')
        self.plot_coal_supply(ax4)
        ax4.legend(loc='upper left')
        ax4.set_ylabel('MMBtu')
        ax4.set_ylim([0, 3 * 10**9])
        fig.savefig(filename)

    def summarize(self):
        """Print object's summary."""
        print(self.summary())

    def summary(self):
        """Summary of Coal and Gas supply and prices."""
        milestones = [start_year, 2020, 2025, 2030, 2040, 2050]

        supply_coal = pd.DataFrame({
            'Domestic': self.loc_production['Coal'] / (10**8 * MBtu),
            'Imported': self.needed_importation['Coal'] / (10**8 * MBtu),
            'Total': self.needed_production['Coal'] / (10**8 * MBtu)},
            columns=['Domestic', 'Imported', 'Total'])

        prices_coal = pd.DataFrame({
            'Domestic': self.loc_prices['Coal'] * MBtu,
            'Imported': self.import_prices["Coal"] * MBtu,
            'Average': self.average_price['Coal'] * MBtu},
            columns=['Domestic', 'Imported', 'Average'])

        supply_gas = pd.DataFrame({
            'Domestic': self.loc_production['Gas'] / (10**8 * MBtu),
            'Imported': self.needed_importation['Gas'] / (10**8 * MBtu),
            'Total': self.needed_production['Gas'] / (10**8 * MBtu)},
            columns=['Domestic', 'Imported', 'Total'])

        prices_gas = pd.DataFrame({
            'Domestic': self.loc_prices['Gas'] * MBtu,
            'Imported': self.import_prices["Gas"] * MBtu,
            'Average': self.average_price['Gas'] * MBtu},
            columns=['Domestic', 'Imported', 'Average'])

        return (
            "\n Coal and Gas origin and prices for " + str(self.scenario) + '\n\n'
            "Coal supply (in E+8 MMBtu)\n"
            + str(supply_coal.loc[milestones].round(1)) + '\n\n'
            + "Coal prices (in $/MMBtu)\n"
            + str(prices_coal.loc[milestones].round(1)) + '\n\n'
            + "Gas supply (in E+8 MMBtu)\n"
            + str(supply_gas.loc[milestones].round(1)) + '\n\n'
            + "Gas prices (in $/MMBtu)\n"
            + str(prices_gas.loc[milestones].round(1)) + '\n\n')


if __name__ == '__main__':
    np.random.seed(0)
    new_param = price_fuel(local_prices, price_gas, price_coal, local_production, baseline)
    np.random.seed(0)
    new_param_moreGas = price_fuel(
        local_prices,
        price_gas,
        price_coal,
        local_production,
        moreGas)
    if (len(sys.argv) == 2) and (sys.argv[1] == "summarize"):
        new_param.summarize()
        new_param_moreGas.summarize()

    if (len(sys.argv) == 3) and (sys.argv[1] == "plot"):
        new_param.plot_information(sys.argv[2])
