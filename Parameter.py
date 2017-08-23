# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
"""Parameter  describes a technical and economic environment."""


from init import pd, sources, start_year, digest


class Parameter():
    """Parameter  describes a technical and economic environment.

    Bundle a power generation technology database, carbon price trajectory and discount rate.
    __str__     content digest, a short checksum
    summary()   contents summary, time series represented by initial level and trend.
    string()    contents, time series fully shown.
    """

    def __init__(self,
                 docstring,
                 discount_rate,
                 plant_accounting_life,
                 construction_cost,
                 fixed_operating_cost,
                 variable_operating_cost,
                 heat_rate,
                 heat_price,
                 emission_factor,
                 capture_factor,
                 carbon_price):
        self.docstring = docstring
        self.discount_rate = discount_rate
        self.plant_accounting_life = plant_accounting_life
        self.construction_cost = construction_cost[sources]
        self.fixed_operating_cost = fixed_operating_cost[sources]
        self.variable_operating_cost = variable_operating_cost[sources]
        self.heat_rate = heat_rate
        self.heat_price = heat_price
        self.emission_factor = emission_factor
        self.capture_factor = capture_factor
        self.carbon_price = carbon_price

    def __str__(self):
        return "Parameters #" + digest(self, 6) + ": " + self.docstring

    def string(self):
        """Detail object contents as a string."""
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
                + "Capture factor (gCO2/kWh)"
                + repr(self.capture_factor[sources])
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
                + "\n\n"
                + "Carbon price ($/tCO2eq)"
                + repr(self.carbon_price)
                )

    def summary(self):
        """Summarize object contents, time series are defined by initial level and trend."""
        summary = pd.DataFrame()
        s = self.plant_accounting_life[sources]
        s.name = "Plant accounting life (year)"
        summary = summary.append(s)
        s = self.emission_factor[sources]
        s.name = "Emission factor (gCO2eq/kWh)"
        summary = summary.append(s)
        s = self.capture_factor.loc[start_year, sources]
        s.name = "Capture factor (gCO2/kWh)"
        summary = summary.append(s)
        s = self.construction_cost.loc[start_year]
        s.name = "Overnight construction costs ($/kW)"
        summary = summary.append(s)
        s = self.construction_cost.diff().loc[start_year + 1]
        s.name = "Overnight construction costs trend ($/kW/y)"
        summary = summary.append(s)
        s = self.fixed_operating_cost.loc[start_year]
        s.name = "Fixed operating costs ($/kW)"
        summary = summary.append(s)
        s = self.fixed_operating_cost.diff().loc[start_year + 1]
        s.name = "Fixed operating costs trend ($/kW/yr)"
        summary = summary.append(s)
        s = self.variable_operating_cost.loc[start_year]
        s.name = "Variable operating costs ($/kWh)"
        summary = summary.append(s)
        s = self.heat_rate.loc[start_year]
        s.name = "Heat rate (Btu/kWh)"
        summary = summary.append(s)
        s = self.heat_price.loc[start_year]
        s.name = "Heat price ($/MBtu)"
        summary = summary.append(s)

        return (
            str(self) + '\n\n'
            + str(summary[sources].round(1)) + '\n\n'
            + "Carbon price ($/tCO2eq)\n"
            + str(self.carbon_price.loc[[start_year, 2030, 2040, 2050]]) + '\n\n'
            + "Discount rate: " + str(self.discount_rate))

    def summarize(self):
        """Print object's summary."""
        print(self.summary())
