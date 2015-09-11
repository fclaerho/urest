# copyright (c) 2015 fclaerhout.fr, released under the MIT license.

import setuptools

setuptools.setup(
	name = "pyrest",
	author = "fclaerhout.fr",
	license = "MIT",
	version = "1.6.0",
	py_modules = ["rest"],
	test_suite = "test",
	author_email = "contact@fclaerhout.fr",
	tests_require = [
		"bottle>=0.12.7",
		"pyutils>=9,<10a0",
	],
	install_requires = [
		"bottle>=0.12.7",
	],
	dependency_links = [
		"https://pypi.fclaerhout.fr/simple/pyutils",
	])
