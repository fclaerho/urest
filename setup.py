# copyright (c) 2015 fclaerhout.fr, released under the MIT license.

import setuptools

setuptools.setup(
	name = "urest",
	url = "https://github.com/fclaerho/urest",
	author = "florent claerhout",
	description = "Tiny Python REST framework",
	license = "MIT",
	version = "2.2.0",
	py_modules = ["urest"],
	test_suite = "test",
	author_email = "code@fclaerhout.fr",
	install_requires = [
		"bottle>=0.12.7",
	],
	tests_require = [
		"bottle>=0.12.7",
		"fckit",
	])
