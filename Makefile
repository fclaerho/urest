export PYTHONPATH := .:vendor

test:
	python test.py
	find . -name '*.pyc' -delete
