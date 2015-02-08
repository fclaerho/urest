export PYTHONPATH := .:vendor

.PHONY: check

check:
	@python selftest.py

clean:
	@rm -f nosetests.xml
	@find . -name "*.pyc" -delete

nosetests.xml:
	@nosetests --with-xunit selftest.py
