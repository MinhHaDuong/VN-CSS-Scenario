# Assessment of power development plans for Vietnam
# The model is a recursive simulation based on OSEMOSYS equations
#
# (c) Minh Ha-Duong, An Ha Truong 2016, 2017, 2018
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#

PYTHON = python3
COVERAGE = python3-coverage
PYTEST = py.test-3

# Tables and figures for the paper on CCS
tables-CCS = table-parameters.fwf table-comparison.fwf
figures-CCS = plan_baseline.pdf plan_withCCS.pdf figure-capacities.pdf figure-capacities.png

# Tables and figures for the paper on sensitivity analysis to international prices of coal and gas
tables-moreGas = price_fuel.txt prices_data_international.txt price_LCOE_run.txt
figures-moreGas = plan_moreGas.pdf  figure_prices.pdf price_fuel.pdf price_LCOE_run.pdf


all-parallel:
	make all -j

all: $(all-CCS) $(all-moreGas)

all-CCS: $(tables-CCS) $(figures-CCS)

all-moreGas: $(tables-moreGas) $(figures-moreGas)


table-parameters.fwf: parameter_reference.txt
	head -13 $< | tail -11 > $@

table-comparison.fwf: Run.txt
	head -26 $< | tail -16 > $@

%.txt: %.py
	@-sed -i "s/VERBOSE = True/VERBOSE = False/" init.py
	$(PYTHON) $< summarize > $@

%.pdf: %.py
	$(PYTHON) $< plot $@

%.png: %.py
	$(PYTHON) $< plot $@

test: cleaner
	$(PYTEST) --doctest-modules

coverage: coverage.xml
	$(COVERAGE) html
	see htmlcov/index.html

coverage.xml:
	$(PYTEST) --doctest-modules --cov=. --cov-report term-missing --cov-report xml

regtest-reset:
	$(PYTEST) --regtest-reset

lint:
	pylint3 *py

docstyle:
	# Ignored messages:
	# D102: Missing docstring in public method                              too many positives
	# D105: Missing docstring in magic method                               why does it need a docstring ?
	# D203: 1 blank line required before class docstring                    bug in the tool
	# D213: Multi-line docstring summary should start at the second line    """We choose D212 ;)
	pydocstyle --ignore=D102,D105,D203,D213 *py

codestyle:
	pycodestyle *py

.PHONY: test regtest-reset lint docstyle codestyle clean cleaner


clean:
	rm -f $(tables-CCS) $(tables-moreGas)
	rm -f $(figures-CCS) $(figures-moreGas)
	rm -f Run.txt parameter_reference.txt

cleaner: clean
	find . -type f -name '*.pyc' -delete
	rm -f table-price-run.txt tmp.ps
	rm -rf __pycache__
	rm -f *.bak
	rm -rf .coverage coverage.xml htmlcov

