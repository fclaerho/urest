# copyright (c) 2015 fclaerhout.fr, released under the MIT license.

from setuptools import setup

import rest

setup(
	name = "rest",
	version = rest.__version__,
	license = "MIT",
	py_modules = ["rest"],
	test_suite = "selftest",
	description = path.__doc__.splitlines()[0],
	install_requires = ['bottle>=0.12.7'],
	tests_require = ['bottle>=0.12.7'])
