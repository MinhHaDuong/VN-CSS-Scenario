# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#

import hashlib
from init import pd, sources, start_year


class Parameter():

    def __init__(self,
                 docstring,
                 discount_rate,
                 plant_accounting_life,
                 construction_cost,
                 fixed_operating_cost,
                 variable_operating_cost,
                 heat_rate,
                 heat_price,
                 emission_factor):
        self.docstring = docstring
        self.discount_rate = discount_rate
        self.plant_accounting_life = plant_accounting_life
        self.construction_cost = construction_cost[sources]
        self.fixed_operating_cost = fixed_operating_cost[sources]
        self.variable_operating_cost = variable_operating_cost[sources]
        self.heat_rate = heat_rate
        self.heat_price = heat_price
        self.emission_factor = emission_factor

    def __str__(self):
        return ("Parameters #" + self.digest() + ": " + self.docstring)

    def summarize(self):
        print(self)
        print()
        summary = pd.DataFrame()
        s = self.plant_accounting_life[sources]
        s.name = "Plant accounting life (year)"
        summary = summary.append(s)
        s = self.emission_factor[sources]
        s.name = "Emission factor (gCO2eq/kWh)"
        summary = summary.append(s)
        s = self.construction_cost.loc[start_year].round()
        s.name = "Overnight construction costs ($/kW)"
        summary = summary.append(s)
        s = self.construction_cost.diff().loc[start_year + 1].round(2)
        s.name = "Overnight construction costs trend ($/kW/y)"
        summary = summary.append(s)
        s = self.fixed_operating_cost.loc[start_year].round(2)
        s.name = "Fixed operating costs ($/kW)"
        summary = summary.append(s)
        s = self.fixed_operating_cost.diff().loc[start_year + 1].round(2)
        s.name = "Fixed operating costs trend ($/kW/yr)"
        summary = summary.append(s)
        s = self.variable_operating_cost.loc[start_year].round(2)
        s.name = "Variable operating costs ($/kWh)"
        summary = summary.append(s)
        s = self.heat_rate.loc[start_year]
        s.name = "Heat rate (Btu/kWh)"
        summary = summary.append(s)
        s = self.heat_price.loc[start_year]
        s.name = "Heat price ($/MBtu)"
        summary = summary.append(s)
        print(summary[sources])
        print()
        print("Discount rate:", self.discount_rate)

    def __repr__(self):
        return ("Parameters: " + self.docstring + "\n"
                + "\n\n"
                + "Discount rate:" + str(self.discount_rate)
                + "\n\n"
                + "Plant accounting life (year)"
                + repr(self.plant_accounting_life[sources])
                + "\n\n"
                + "Emission factor (gCO2eq/kWh)"
                + repr(self.emission_factor[sources])
                + "\n\n"
                + "Overnight construction costs ($/kW)"
                + repr(self.construction_cost.round())
                + "\n\n"
                + "Fixed operating costs ($/kW)"
                + repr(self.fixed_operating_cost.round(2))
                + "\n\n"
                + "Variable operating costs ($/kWh)"
                + repr(self.variable_operating_cost.round(2))
                + "\n\n"
                + "Heat rate (Btu/kWh)"
                + repr(self.heat_rate)
                + "\n\n"
                + "Heat price ($/MBtu)"
                + repr(self.heat_price)
                )

    def digest(self):
        return hashlib.md5(repr(self).encode('utf-8')).hexdigest()[0:6]
