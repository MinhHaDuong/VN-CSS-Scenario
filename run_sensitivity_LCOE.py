# -*- coding: utf-8 -*-
"""Multiple Run to calculate LCOE for different international prices trajectories.

Created on Tue Feb  6 09:08:21 2018

@author: Alice Duval
"""

import sys
import numpy as np
import matplotlib.pyplot as plt

from plan_baseline import baseline
from plan_moreGas import moreGas
from price_fuel import price_fuel
from prices_data_international import price_gas, price_coal
from prices_data_local import local_prices
from production_data_local import local_production

from Run import Run


class multiple_LCOE():
    """Multiple runs of the model for different international coal and gas prices parameters.

    Compare LCOE of each run, one to another
    """

    def __init__(self, plan, number_run):
        self.plan = plan
        self.number_run = number_run

    def one_run(self):
        """Generate parameters and run the model with these newly defined parameters."""
        reference = price_fuel(
            local_prices,
            price_gas,
            price_coal,
            local_production,
            baseline).parameters
        run_model = Run(self.plan, reference)
        return run_model.lcoe

    def multiple_run(self):
        """Run the Monte Carlo sensitivy analysis.

        Initialize the random factor.
        Store LCOE generated for each run of the model in a sorted list
        """
        lcoe_list = []
        for i in range(self.number_run):
            np.random.seed(i)
            lcoe_list.append(self.one_run() * 100)
        lcoe_list.sort(reverse=True)
        return lcoe_list

    def summary(self):
        """Summarize of LCOE prices."""
        lcoe_values = self.multiple_run()
        mean_value = np.mean(lcoe_values)
        median_value = np.median(lcoe_values)
        perc_value = np.percentile(lcoe_values, 95)
        return ("\n LCOE for " +
                str(self.number_run) +
                " gas and coal international prices forecasts in " +
                str(self.plan) + " plan \n\n" +
                " Mean value : " + str(round(mean_value, 2)) + "\n" +
                " Median value : " + str(round(median_value, 2)) + "\n" +
                " 95 percentile value : " + str(round(perc_value, 2))
                )

    def summarize(self):
        """Print object's summary."""
        print(self.summary())

    def plot(self, filename):
        """Plot generated LCOE."""
        lcoe = self.multiple_run()
        fig = plt.figure()
        fig.suptitle('LCOE for ' + str(self.number_run) +
                     ' gas and coal international prices forecasts in\n' + str(self.plan))
        ax = fig.add_subplot(111)
        ax.bar(np.arange(len(lcoe)), lcoe, width=1)
        ax.set_ylabel('LCOE in US cent / kWh')
        ax.set_xticks([])
        ax.set_ylim([0, 10.5])
        fig.savefig(filename)


if __name__ == '__main__':
    if (len(sys.argv) == 2) and (sys.argv[1] == "summarize"):
        LCOE_list = multiple_LCOE(baseline, 100)
        LCOE_list.summarize()
        LCOE_list_alt = multiple_LCOE(moreGas, 100)
        LCOE_list_alt.summarize()

    if (len(sys.argv) == 3) and (sys.argv[1] == "plot"):
        LCOE_list = multiple_LCOE(baseline, 100)
        LCOE_list.plot(sys.argv[2])
