# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#


"""
Defines the baseline scenario

Up to 2015-12-31, based on historical installed capacity listed in EVN 2016 report
From 2016 onwards, based on future capacity additions listed in PDP7A
  not including coal plants listed as backup for renewables
Nuclear replaced by Coal

Renewable4 includes small hydro
"""

import pandas as pd
# import numpy as np
from init import show, VERBOSE, sources
from parameters import plant_life
from data import fuels, PDP7A_annex1, capacities_PDP7A, capacity_past, addcol_Renewable4
from data import production_past, capacity_factor_past, capacity_factor_PDP7A, production_PDP7A
# from data import fuel_use_PDP7A


#%%

class PowerPlan:

    def __init__(self, additions, retirement, capacity_factor, net_import):
        self.additions = additions
        self.retirement = retirement
        self.capacity_factor = capacity_factor
        self.net_imports = net_import

        self.capacities = (additions - retirement).cumsum()
        self.production = self.capacities.loc[1990:] * capacity_factor * 8760 / 1000
        self.production["Import"] = net_import
        self.production = self.production[sources].fillna(0)

    def __str__(self):
        return ("Power development program #" + str(hash(self)))

    def print_details(self):
        print(self)
        print()
        print("Annual generation capacity addition by fuel type (MW)")
        print(self.additions[sources + ["PumpedStorage"]].round())
        print()
        print("Old capacity retirement by fuel type (MW)")
        print(self.retirement[fuels].round())
        print()
        print("Generation capacity by fuel type (MW)")
        print(self.capacities[sources + ["PumpedStorage"]].round())
        print()
        print("Electricity production (GWh)")
        print(self.production.round())
        print()
        print("Capacity factors")
        print(capacityfactor.round(2))
        print()

#        print(str(self) + "\n\ntotal electricity produced by fuel type")
#        print("Period: 2016 - 2050, discount rate:", discount_rate, "per year")
#        for fuel in fuels:
#            value = present_value(production_baseline[fuel], discount_rate)
#            value = int(value / 1000)
#            print(fuel + ": " + str(value) + " TWh")

    def plot_additions(self):
        self.additions[fuels].plot(title=str(self) + "\n\nAdded capacity (MW)")

    def plot_retirement(self):
        self.retirement[fuels].plot(title=str(self) + "\n\nRetired capacity (MW)")

    def plot_capacity_mix(self):
        mix = (self.capacities[fuels] / 1000).drop("Oil", axis=1)
        ax = mix.plot(title=str(self) + "\n\nVietnam generation capacity by fuel type (GW)")
        ax.axvline(2015, color="k")
        ax.axvline(2030, color="k")


def fill_in(serie):
    """Returns the investments needed to reach the capacity objectives
    approximately because cast as integer
    """
    capacity_2015 = capacity_past.cumsum().loc[2015, serie.name]
    a = (serie[2020] - capacity_2015) / 15
    b = (serie[2025] - serie[2020]) / 15
    c = (serie[2030] - serie[2025]) / 15
    return pd.Series(name=serie.name,
                     data=[a, 2 * a, 3 * a, 4 * a, 5 * a,
                           b, 2 * b, 3 * b, 4 * b, 5 * b,
                           c, 2 * c, 3 * c, 4 * c, 5 * c],
                     index=range(2016, 2031),
                     dtype="int64")


#%%  Capacity additions

# 2016 - 2030 capacity additions for Coal, Gas, Oil, BigHydro

additions = PDP7A_annex1.replace({"fuel": {"Nuclear": "Gas"}})

additions = additions.groupby(["year", "fuel"]).capacity_MW.sum()
additions = additions.unstack()
additions.drop("ND*", axis=1, inplace=True)

# 2016 - 2030 capacity additions for the four renewable technologies

additions["Solar"] = fill_in(capacities_PDP7A.Solar)
additions["Wind"] = fill_in(capacities_PDP7A.Wind)
additions["Biomass"] = fill_in(capacities_PDP7A.Biomass)
additions["SmallHydro"] = fill_in(capacities_PDP7A.SmallHydro)
additions["Import"] = fill_in(capacities_PDP7A.Import)

# 1974 - 2015 capacity additions and cleanup

additions = pd.concat([capacity_past, additions])

additions = additions[fuels + ["PumpedStorage", "Import"]].fillna(0)

# 2031 - 2050 scenario definition

increment = {"Coal": 0, "Gas": 750, "Oil": 20, "BigHydro": 0,
             "SmallHydro": 50, "Biomass": 50, "Wind": 900, "Solar": 1000,
             "PumpedStorage": 50, "Import": 50}

for y in range(2031, 2051):
    additions.loc[y] = increment


#%% Old plant retirement program

retirement = pd.DataFrame()

for tech in plant_life:
    retirement[tech] = additions[tech].shift(plant_life[tech])

retirement.fillna(0, inplace=True)

# Fix to meet PDP7A objective more precisely
retirement.loc[2017, "BigHydro"] = 200
retirement.loc[2018, "BigHydro"] = 200
retirement.loc[2019, "BigHydro"] = 200

retirement.loc[2017, "Oil"] = 100
retirement.loc[2018, "Oil"] = 100
retirement.loc[2019, "Oil"] = 100

# Smooth the retirement program a bit, especially Gas 2025
retirement = pd.rolling_mean(retirement, 2)
retirement.loc[1974] = 0

#%%


def extend(serie, endpoint, newname, past=capacity_factor_past, future=capacity_factor_PDP7A):
    """Extends the  past   series
       going through the 2020, 2025, 2030 values defined in the  future  series
       and then to the 2050 endpoint value
    """
    r = past[serie]
    a = (r.loc[2013] + r.loc[2014] + r.loc[2015]) / 15
    b = future.loc[2020, serie] / 5
    c = future.loc[2025, serie] / 5
    d = future.loc[2030, serie] / 5
    s = pd.Series(name=newname,
                  data=[4 * a + b, 3 * a + 2 * b, 2 * a + 3 * b, a + 4 * b, 5 * b,
                        4 * b + c, 3 * b + 2 * c, 2 * b + 3 * c, b + 4 * c, 5 * c,
                        4 * c + d, 3 * c + 2 * d, 2 * c + 3 * d, c + 4 * d, 5 * d],
                  index=range(2016, 2031))
    r = r.append(s)
    d *= 5
    e = endpoint
    s = pd.Series(name=newname,
                  data=[d + (e - d) * (i + 1) / 20 for i in range(20)],
                  index=range(2031, 2051))
    return r.append(s)


#%% Electricity production

capacityfactor = pd.DataFrame()

capacityfactor["Coal"] = extend("Coal", 0.6, "Coal")
capacityfactor["Gas"] = extend("Gas", 0.6, "Gas")
capacityfactor["Oil"] = 0.25
capacityfactor["BigHydro"] = extend("BigHydro", 0.4, "BigHydro")
capacityfactor["SmallHydro"] = extend("SmallHydro", 0.6, "SmallHydro")
capacityfactor["Biomass"] = extend("Renewable", 0.3, "Biomass")
capacityfactor["Wind"] = extend("Renewable", 0.3, "Wind")
capacityfactor["Solar"] = extend("Renewable", 0.23, "Solar")

capacityfactor = capacityfactor.where(capacityfactor < 1)

net_import = extend("Import", 7000, "Import", production_past, production_PDP7A)


#%% Main statement

baseline = PowerPlan(additions, retirement, capacityfactor, net_import)

if VERBOSE:
    baseline.print_details()
    baseline.plot_additions()
    baseline.plot_retirement()
    baseline.plot_capacity_mix()


#%% Check the capacity numbers vs. PDP7A objectives

show("""
*****************************************************
***     Comparing our baseline with PDP7          ***
*****************************************************
""")

compared = ["Coal", "Gas", "BigHydro", "Renewable4", "Nuclear"]

tocompare = baseline.capacities.loc[[2020, 2025, 2030]]
tocompare["Gas"] = tocompare.Gas + tocompare.Oil
tocompare["Nuclear"] = 0
addcol_Renewable4(tocompare)
tocompare = tocompare[compared]

relerror = (tocompare - capacities_PDP7A) / capacities_PDP7A
relerror = relerror[compared]

show("PDP7A")
show(capacities_PDP7A[compared])
show()
show("Baseline scenario, Gas includes Oil")
show(tocompare)
show()
show("Relative error")
show(relerror)
show("Note: Gas 2030 is larger in baseline because we replace nuclear with gas")

#b = production_past[fuels].astype("int64")
#
#show("Past - Electricity production (GWh)")
#show(b)
#show()
#
#
#relerr = ((production_baseline - b) / b).loc[1990:2015]
#show("Relative error")
#show(relerr)

#%% Fuel use
#
#MtCoal_per_GWh = fuel_use_PDP7A.Coal / production_PDP7A.Coal
#
#show(MtCoal_per_GWh)
#
#a = MtCoal_per_GWh[2020]
#b = MtCoal_per_GWh[2025]
#da = (b - a) / 5
#c = MtCoal_per_GWh[2030]
#db = (c - b) / 5
#s = pd.Series(name="Coal",
#              data=np.concatenate([np.arange(a - 10 * da, b, da),
#                                   np.arange(b, c + 21 * db, db)]),
#              index=range(2010, 2051))
#
#show(s)
#
#coal_use_baseline = s * production_baseline.Coal.loc[2010:]
#
#show(fuel_use_PDP7A.Coal)
#show(coal_use_baseline)
#
##TODO: Check against statistics
