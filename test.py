# copyright (c) 2015 fclaerhout.fr, released under the MIT license.

import unittest, json

import bottle, urest, fckit # 3rd-party

MSG = ["Hello, World!", "blah", "lorem ipsum"]

class Hello(urest.Resources):

	def select(self, **kwargs):
		return [{"id": i, "msg": MSG[i]} for i in range(len(MSG))]

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
			SERVER = urest.Server(port = PORT)
			SERVER.register("/hello", Hello())
			fckit.background(None, SERVER.run, verbose = False)

	def _get(self, querystring):
		res = fckit.http_request(
			hostname = "localhost",
			port = PORT,
			method = "GET",
			headers = {"Accept": "application/json"},
			path = "/hello%s" % querystring)
		self.assertEqual(res.status, 200)
		return json.loads(res.read())

	def test_get_limit(self):
		body = self._get("?limit=1")
		self.assertEqual(body["success"], True)
		self.assertEqual(body["result"], [{"id": 0, "msg": MSG[0]}])

	def test_get_id(self):
		body = self._get("?id=1")
		self.assertEqual(body["success"], True)
		self.assertEqual(body["result"], [{"id": 1, "msg": MSG[1]}])

	def test_get_msg(self):
		body = self._get("?msg=%s" % MSG[1])
		self.assertEqual(body["success"], True)
		self.assertEqual(body["result"], [{"id": 1, "msg": MSG[1]}])

	def test_get_offset(self):
		body = self._get("?offset=2")
		self.assertEqual(body["success"], True)
		self.assertEqual(body["result"], [{"id": 2, "msg": MSG[2]}])

	def test_get_limit_offset(self):
		body = self._get("?offset=1&limit=1")
		self.assertEqual(body["success"], True)
		self.assertEqual(body["result"], [{"id": 1, "msg": MSG[1]}])

	def test_get_offset_fields(self):
		body = self._get("?offset=2&fields=msg")
		self.assertEqual(body["success"], True)
		self.assertEqual(body["result"], [{"msg": MSG[2]}])

if __name__ == "__main__": unittest.main(verbosity = 2)
