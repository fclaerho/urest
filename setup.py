# copyright (c) 2015 fclaerhout.fr, released under the MIT license.

import setuptools, os

open("bottle.py", "w")

import rest

os.remove("bottle.py")

setuptools.setup(
	name = "rest",
	version = rest.__version__,
	license = "MIT",
	py_modules = ["rest"],
	test_suite = "selftest",
	description = rest.__doc__.splitlines()[0],
	tests_require = ["bottle>=0.12.7"],
	install_requires = ["bottle>=0.12.7"])
