export PYTHONPATH := .:vendor

testclean: test clean

test:
	python test.py

clean:
	find . -name '*.pyc' -delete
