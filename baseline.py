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
from data import fuel_types, PDP7A_annex1, capacities_PDP7A, capacity_past, addcol_Renewable4
from data import production_past, capacity_factor_past, capacity_factor_PDP7A, production_PDP7A

#%%  Capacities

# 2016 - 2030 capacity additions for Coal, Gas, Oil, BigHydro

additions = PDP7A_annex1.replace({"fuel": {"Nuclear": "Gas"}})

additions = additions.groupby(["year", "fuel"]).capacity_MW.sum()
additions = additions.unstack()
additions.drop("ND*", axis=1, inplace=True)

# 2016 - 2030 capacity additions for the four renewable technologies


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


additions["Solar"] = fill_in(capacities_PDP7A.Solar)
additions["Wind"] = fill_in(capacities_PDP7A.Wind)
additions["Biomass"] = fill_in(capacities_PDP7A.Biomass)
additions["SmallHydro"] = fill_in(capacities_PDP7A.SmallHydro)

# 1974 - 2015 capacity additions and cleanup

additions = pd.concat([capacity_past, additions])

additions = additions[fuel_types + ["PumpedStorage"]].fillna(0)

# 2031 - 2050 scenario definition

increment = {"Coal": 0, "Gas": 750, "Oil": 0, "BigHydro": 0,
             "SmallHydro": 50, "Biomass": 50, "Wind": 900, "Solar": 1000,
             "PumpedStorage": 50}

for y in range(2031, 2051):
    additions.loc[y] = increment

print("Vietnam annual generation capacity addition by fuel type (MW)")
print(additions[fuel_types + ["PumpedStorage"]])
print()

#%% Old plant retirement program

life = {"Coal": 40, "Gas": 25, "Oil": 30, "BigHydro": 100,
        "SmallHydro": 60, "Biomass": 25, "Wind": 20, "Solar": 25,
        "PumpedStorage": 100}

retirement = pd.DataFrame()

for tech in life:
    retirement[tech] = additions[tech].shift(life[tech])

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

print("Old capacity retirement by fuel type (MW)")
print(retirement[fuel_types])
print()
retirement[fuel_types].plot(title="Retired capacity (MW)")

#%%

capacity_baseline = additions - retirement
capacities_baseline = capacity_baseline.cumsum()

print("Vietnam generation capacity by fuel type (MW)")
print(capacities_baseline[fuel_types + ["PumpedStorage"]])
print()

mix = (capacities_baseline[fuel_types] / 1000).drop("Oil", axis=1)
ax = mix.plot(title="Baseline scenario\nVietnam generation capacity by fuel type (GW)")
ax.axvline(2015, color="k")
ax.axvline(2030, color="k")

#%% Check the capacity numbers vs. PDP7A objectives

compared = ["Coal", "Gas", "BigHydro", "Renewable4", "Nuclear"]

tocompare = capacities_baseline.loc[[2020, 2025, 2030]]
tocompare["Gas"] = tocompare.Gas + tocompare.Oil
tocompare["Nuclear"] = 0
addcol_Renewable4(tocompare)
tocompare = tocompare[compared]

relerror = (tocompare - capacities_PDP7A) / capacities_PDP7A
relerror = relerror[compared]

print("PDP7A")
print(capacities_PDP7A[compared])
print()
print("Baseline scenario, Gas includes Oil")
print(tocompare)
print()
print("Relative error")
print(relerror)
print("Note: Gas 2030 is larger in baseline because we replace nuclear with gas")

#
#%% Electricity production


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

print(capacityfactor)
print()

#%%

production_baseline = capacities_baseline.loc[1990:] * capacityfactor * 8760 / 1000

production_baseline["Import"] = extend("Import", 7000, "Import", production_past, production_PDP7A)

a = production_baseline[fuel_types + ["Import"]].fillna(0).astype("int64")
print("Baseline scenario - Electricity production (GWh)")
print(a)
print()

#b = production_past[fuel_types].astype("int64")
#
#print("Past - Electricity production (GWh)")
#print(b)
#print()
#
#
#relerr = ((a - b) / b).loc[1990:2015]
#print("Relative error")
#print(relerr)
