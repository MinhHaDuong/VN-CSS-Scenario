# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
"""Parameter  describes a technical and economic environment."""

from collections import namedtuple
import hashlib

from init import pd, SOURCES, START_YEAR


class Parameter(namedtuple('Parameter',
                           ['DISCOUNT_RATE',
                            'plant_accounting_life',
                            'construction_cost',
                            'fixed_operating_cost',
                            'variable_operating_cost',
                            'heat_rate',
                            'heat_price',
                            'EMISSION_FACTOR',
                            'capture_factor',
                            'CARBON_PRICE'])):
    """Parameter  describes a technical and economic environment.

    Bundle a power generation technology database, carbon price trajectory and discount rate.
    digest      content digest, a short checksum
    summary()   contents summary, time series represented by initial level and trend.
    __new__()   constructor, default not extended
    __repr__()  detailed representation as  string, default not extended

    """

    @property
    def digest(self):
        return hashlib.md5(self.__repr__().encode('utf-8')).hexdigest()[0:6]

    def __str__(self):
        return "Parameters #" + self.digest + ": " + self.__doc__

    def summary(self):
        """Summarize object contents, time series are defined by initial level and trend."""
        summary = pd.DataFrame()
        s = self.plant_accounting_life[SOURCES]
        s.name = "Plant accounting life (year)"
        summary = summary.append(s)
        s = self.EMISSION_FACTOR[SOURCES]
        s.name = "Emission factor (gCO2eq/kWh)"
        summary = summary.append(s)
        s = self.capture_factor.loc[START_YEAR, SOURCES]
        s.name = "Capture factor (gCO2/kWh)"
        summary = summary.append(s)
        s = self.construction_cost.loc[START_YEAR]
        s.name = "Overnight construction costs ($/kW)"
        summary = summary.append(s)
        s = self.construction_cost.diff().loc[START_YEAR + 1]
        s.name = "Overnight construction costs trend ($/kW/y)"
        summary = summary.append(s)
        s = self.fixed_operating_cost.loc[START_YEAR]
        s.name = "Fixed operating costs ($/kW)"
        summary = summary.append(s)
        s = self.fixed_operating_cost.diff().loc[START_YEAR + 1]
        s.name = "Fixed operating costs trend ($/kW/yr)"
        summary = summary.append(s)
        s = self.variable_operating_cost.loc[START_YEAR]
        s.name = "Variable operating costs ($/kWh)"
        summary = summary.append(s)
        s = self.heat_rate.loc[START_YEAR]
        s.name = "Heat rate (Btu/kWh)"
        summary = summary.append(s)
        s = self.heat_price.loc[START_YEAR]
        s.name = "Heat price ($/MBtu)"
        summary = summary.append(s)

        return (
            str(self) + '\n\n'
            + str(summary[SOURCES].round(1)) + '\n\n'
            + "Carbon price ($/tCO2eq)\n"
            + str(self.CARBON_PRICE.loc[[START_YEAR, 2030, 2040, 2050]]) + '\n\n'
            + "Discount rate: " + str(self.DISCOUNT_RATE))

    def summarize(self):
        """Print object's summary."""
        print(self.summary())
