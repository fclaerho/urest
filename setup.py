# copyright (c) 2015 fclaerhout.fr, released under the MIT license.

import setuptools

setuptools.setup(
	name = "urest",
	author = "florent claerhout",
	license = "MIT",
	version = "1.6.0",
	py_modules = ["urest"],
	test_suite = "test",
	author_email = "code@fclaerhout.fr",
	tests_require = [
		"bottle>=0.12.7",
		"fckit==11.0.2",
	],
	install_requires = [
		"bottle>=0.12.7",
	])
