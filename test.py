# copyright (c) 2015 fclaerhout.fr, released under the MIT license.

import unittest, json

import bottle, rest, utils # 3rd-party

MSG = "Hello, World!"

class Hello(rest.Resources):

	def select(self, **kwargs):
		return {"msg": MSG}

	def create(self, body):
		raise MethodNotAllowed

	def update(self, body):
		raise MethodNotAllowed

	def delete(self, body):
		raise MethodNotAllowed

SERVER = None
PORT = 12345

class Test(unittest.TestCase):

	def setUp(self):
		global SERVER
		if not SERVER:
			SERVER = rest.Server(port = PORT)
			SERVER.register("/hello", Hello())
			utils.background(None, SERVER.run, verbose = False)

	def test_get(self):
		res = utils.http_request(
			hostname = "localhost",
			port = PORT,
			method = "GET",
			path = "/hello")
		self.assertEqual(res.status, 200)
		body = json.loads(res.read())
		self.assertEqual(body["success"], True)
		self.assertEqual(body["result"], {"msg": MSG})

if __name__ == "__main__": unittest.main(verbosity = 2)
