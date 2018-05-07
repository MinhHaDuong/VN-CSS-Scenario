# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#

"""Read the prepared data files.

There are 3 data sources (PDP7A, EVN 2016 report, IEA statistics)
so we need to clarify column names.

1/ Some include Imports in electricity "Production"
Here we don't --it's clearly wrong-- and use these column names:
      Supply = Production + Imports

2/ Another ambiguity is whether SmallHydro is included in "Hydro" or "Renewable"
Here we do the former and use these column names:
      Hydro = BigHydro + SmallHydro
      BigHydro = LargeHydro + InterHydro
      Renewable = Wind + Solar + Biomass
      Renewable4 = Renewable + Small hydro

3/ We do NOT include PumpedStorage in Hydro capacities

4/ We define Import as net of Exports

5/ In VN capacity stats, generation from fuel oil and from diesel is not clearly accounted for

6/ Column "capacities" means nameplate capacity.
Adding up capacities across columns is generally misleading,
since the capacity factors are not comparable, neither are the investment costs

7/ Column "capacities" is in terms of net electric power.
"Coal CCS" has a lower efficiency (higher heat rate) than "Coal" of same capacity
"""

from init import pd, show, PLANT_TYPE, SOURCES, addcol_Renewable, addcol_Renewable4


# %% Read data from EVN 2016 activity report
# Historical capacity addition

CAPACITY_ADDITIONS_PAST = pd.read_fwf("data/capacity_additions_past.txt")

show(CAPACITY_ADDITIONS_PAST)

capacity_2015_EVN = CAPACITY_ADDITIONS_PAST.groupby(["fuel"]).capacity_MW.sum()
# show("SummaryCapacity in 2015")
# show(capacity_2015)

# Comparision with EVN Annual Report 2016, page 11.
capacity_2015_EVN["BigHydro"] = capacity_2015_EVN.LargeHydro + capacity_2015_EVN.InterHydro
assert capacity_2015_EVN.BigHydro == 14636
assert capacity_2015_EVN.Coal == 12903
assert capacity_2015_EVN.Oil == 875
assert capacity_2015_EVN.Gas == 7998
assert capacity_2015_EVN.Wind == 135
assert capacity_2015_EVN.Biomass + capacity_2015_EVN.SmallHydro == 2006
capacity_2015_EVN["Renewable4"] = (capacity_2015_EVN.SmallHydro
                                   + capacity_2015_EVN.Wind
                                   + capacity_2015_EVN.Biomass)


CAPACITY_PAST = CAPACITY_ADDITIONS_PAST.groupby(["year", "fuel"]).capacity_MW.sum()
CAPACITY_PAST = CAPACITY_PAST .unstack().fillna(0)
CAPACITY_PAST.drop("Dummy", axis=1, inplace=True)


def smooth(s):
    """Redistribute over time equally a mass concentrated in the last period.

    Argument  s  is a numerical series with a numerical value in last position.
    Values are and remain integers;

    Metaphor: the benjamin shares apples with all his previous siblings.
    Assume for example there are 4 brothers and the last one has 10 apples.
    Then he should give each brother 2 apples, keeping 4 for himself.

    >>> smooth(pd.Series([0, 0, 0, 10]))
    0    2
    1    2
    2    2
    3    4
    dtype: int64
    """
    n = len(s)
    total = s.iloc[-1]
    annual = int(total // n)
    final = int(total - annual * (n - 1))
    data = [annual] * (n - 1) + [final]
    assert sum(data) == total
    return pd.Series(data, s.index)


CAPACITY_PAST.InterHydro = smooth(CAPACITY_PAST.InterHydro)
CAPACITY_PAST.SmallHydro = smooth(CAPACITY_PAST.SmallHydro)
CAPACITY_PAST.Oil = smooth(CAPACITY_PAST.Oil)

CAPACITY_PAST["Solar"] = 0
CAPACITY_PAST["Import"] = 0
CAPACITY_PAST["PumpedStorage"] = 0
CAPACITY_PAST["CoalCCS"] = 0
CAPACITY_PAST["GasCCS"] = 0
CAPACITY_PAST["BioCCS"] = 0

CAPACITY_PAST["BigHydro"] = (CAPACITY_PAST.LargeHydro
                             + CAPACITY_PAST.InterHydro)

CAPACITY_PAST["Hydro"] = (CAPACITY_PAST.BigHydro
                          + CAPACITY_PAST.SmallHydro)

addcol_Renewable(CAPACITY_PAST)
addcol_Renewable4(CAPACITY_PAST)

show("""
Vietnam historical capacity additions by fuel type (MW)
Source: Capacities listed in EVN activity report 2016, dated by internet search
""")
show(CAPACITY_PAST[PLANT_TYPE])
show()

show("""
Vietnam historical generation capacity by fuel type (MW)
Source: Capacities listed in EVN activity report 2016, dated by internet search
""")
show(CAPACITY_PAST[PLANT_TYPE].cumsum())
show()

show("""
Vietnam historical generation capacity by fuel type (MW)
Small hydro included in Renewable4
""")

show(CAPACITY_PAST[["Coal", "Gas", "Oil", "BigHydro", "Renewable4"]].cumsum())
show()

show("""
Vietnam historical generation capacity by fuel type (MW)
Small hydro included in Hydro
""")
show(CAPACITY_PAST[["Coal", "Gas", "Oil", "Hydro", "Renewable"]].cumsum())
show()


# %% read data from International Energy Agency

PRODUCTION_PAST = pd.read_csv("data/IEA/ElectricityProduction.csv", header=5, index_col=0)

PRODUCTION_PAST["Solar"] = 0
addcol_Renewable(PRODUCTION_PAST)
PRODUCTION_PAST["SmallHydro"] = (PRODUCTION_PAST.Hydro *
                                 CAPACITY_PAST.SmallHydro / CAPACITY_PAST.Hydro)
PRODUCTION_PAST["SmallHydro"] = PRODUCTION_PAST["SmallHydro"].astype(int)
PRODUCTION_PAST["BigHydro"] = PRODUCTION_PAST.Hydro - PRODUCTION_PAST.SmallHydro
PRODUCTION_PAST["Import"] = PRODUCTION_PAST.Imports + PRODUCTION_PAST.Exports

PRODUCTION_PAST["CoalCCS"] = 0
PRODUCTION_PAST["GasCCS"] = 0
PRODUCTION_PAST["BioCCS"] = 0


# %% Estimates 2015 production by fuel type
# Source Institute of Energy cited in
# http://gizenergy.org.vn/en/knowledge-resources/power-sector-vietnam
"""The annual electricity production increased to 164.31 TWh in 2015.
In 2015, coal accounted for the largest share of electricity production (34.4%),
followed by hydropower (30.4%) and gas (30%). Apart from large-scale hydropower,
renewable energy - including small-scale hydropower - represented only a minor part
of the electricity production (3.7%).
The figure adds that: Imports represented 1.5%, we infer that the production number is the total
domestic supply.
The Gas cheese slice label is "Gas Turbine" which includes Oil fueled gas turbines.
"""
# This implies a total production of 164310 * 0.985 = 161.8 TWh
# which compares to  159.7 TWh given in EVN 2016 report page 16

domestic_supply_2015 = 164310  # GWh

production_2015 = pd.Series(name=2015,
                            data={"Coal": round(0.344 * domestic_supply_2015),
                                  "BigHydro": round(0.304 * domestic_supply_2015),
                                  "GasTurbine": round(0.300 * domestic_supply_2015),
                                  "Renewable4": round(0.037 * domestic_supply_2015),
                                  "Import": round(0.015 * domestic_supply_2015)})

production_2015["Oil"] = 450  # Source: Own estimate, same as 2015, we have no idea
production_2015["Gas"] = production_2015["GasTurbine"] - production_2015["Oil"]
production_2015["Wind"] = 240         # Source: Own estimate, 2014 + Bac Lieu 1 online
production_2015["Biomass"] = 60       # Continuity with 2014 level and trend
production_2015["Solar"] = 0          # Commercial solar power not allowed by law yet
addcol_Renewable(production_2015)
production_2015["SmallHydro"] = production_2015["Renewable4"] - production_2015["Renewable"]
production_2015["Hydro"] = production_2015["BigHydro"] + production_2015["SmallHydro"]

production_2015.drop(["GasTurbine", "Renewable4"], inplace=True)

production_2015["CoalCCS"] = 0
production_2015["GasCCS"] = 0
production_2015["BioCCS"] = 0

PRODUCTION_PAST = PRODUCTION_PAST.append(production_2015)

show("""
Vietnam electricity production by fuel type (GWh)
Source IEA 1990-2014
Source GiZ citing Institute of Energy for 2015
Hydro production divided between small and big proportional to capacity
Imports are net of exports
""")
show(PRODUCTION_PAST[SOURCES])
show()

# %%

capacity_factor_past = PRODUCTION_PAST / CAPACITY_PAST.cumsum() * 1000 / 8760
capacity_factor_past = capacity_factor_past.loc[1990:]

show("""
Vietnam historical capacity factors by fuel type
Source: author
""")
show(capacity_factor_past[PLANT_TYPE].drop("Solar", axis=1))
