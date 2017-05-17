# Economic of co-firing in two power plants in Vietnam
#
# (c) Minh Ha-Duong, An Ha Truong 2016, 2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#

PYTHON = python3


tablepyfiles = plan_baseline.py plan_withCCS.py param_reference.py Run.py
tables = $(patsubst %.py,%.txt,$(tablepyfiles))
diffs  = $(patsubst %.py,%.diff,$(tablepyfiles))

figures = plan_baseline.pdf plan_withCCS.pdf

all: $(tables) $(figures)

%.py: %-generator.py
	$(PYTHON) $< > $@

%.txt: %.py
	@-sed -i "s/VERBOSE = True/VERBOSE = False/" init.py
	$(PYTHON) $< summarize > $@

%.pdf: %.py
	$(PYTHON) $< plot > $@

%.diff: %.txt tables.tocompare/%.txt
	@diff $^  > $@
	@if [ -s $@ ]; then exit 1; fi;

%.doctest: %.py
	$(PYTHON) -m doctest -v $< > $@

.PHONY: test reg_tests reg_tests_reset clean cleaner

test: $(doc_tests) $(script_tests) reg_tests

reg_tests: $(diffs)
	@cat $^

reg_tests_reset: $(tables)
	cp $^ tables.tocompare

clean:
	rm -f $(tables)
	rm -f $(figures)
	rm -f $(doc_tests)
	rm -f $(script_tests)
	rm -f $(diffs)

cleaner: clean
	find . -type f -name '*.pyc' -delete
	rm -f data.py
	rm -rf __pycache__
