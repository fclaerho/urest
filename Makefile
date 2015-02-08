export PYTHONPATH := .:vendor

.PHONY: check clean

check:
	@python selftest.py

clean:
	@rm -f nosetests.xml
	@find . -name "*.pyc" -delete

nosetests.xml: selftest.py
	@nosetests --with-xunit $^

