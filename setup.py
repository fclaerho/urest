# copyright (c) 2015 fclaerhout.fr, released under the MIT license.

from setuptools import setup

setup(
	name = "rest",
	version = "1.0.0",
	license = "MIT",
	py_modules = ["rest"],
	test_suite = "selftest",
	description = "Bottle wrapper implementing REST design recommended practices",
	tests_require = ["bottle>=0.12.7"],
	install_requires = test_requires)
