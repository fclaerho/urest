# copyright (c) 2015 fclaerhout.fr, released under the MIT license.

import unittest, json, time

import bottle, urest, fckit # 3rd-party

MSG = ["Hello, World!", "blah", "lorem ipsum"]
DATA = [{"id": i, "msg": MSG[min(i, len(MSG) - 1)]} for i in xrange(200)]

class Hello(urest.Resources):

	def select(self, **kwargs):
		return DATA

	def create(self, body):
		raise MethodNotAllowed

	def update(self, body):
		raise MethodNotAllowed

	def delete(self, body):
		raise MethodNotAllowed

PORT = 12345

class Test(unittest.TestCase):

	def setUp(self):
		server = urest.Server(port = PORT)
		server.register("/hello", Hello())
		self.process = fckit.async(server.run, threaded = False)

	def tearDown(self):
		self.process.terminate()

	def _get(self, querystring = None):
		res = fckit.http_request(
			hostname = "localhost",
			port = PORT,
			method = "GET",
			headers = {"Accept": "application/json"},
			path = "/hello%s" % (querystring or ""))  
		self.assertEqual(res.status, 200)
		return json.loads(res.read())

	def test_get_default_limit(self):
		body = self._get()
		self.assertEqual(body["success"], True)
		self.assertEqual(body["result"], DATA[:100])

	def test_get_limit(self):
		body = self._get("?limit=1")
		self.assertEqual(body["success"], True)
		self.assertEqual(body["result"], DATA[:1])

	def test_get_id(self):
		body = self._get("?id=1")
		self.assertEqual(body["success"], True)
		self.assertEqual(body["result"], [DATA[1]])

	def test_get_msg(self):
		body = self._get("?msg=%s" % MSG[1])
		self.assertEqual(body["success"], True)
		self.assertEqual(body["result"], [DATA[1]])

	def test_get_offset_and_default_limit(self):
		body = self._get("?offset=2")
		self.assertEqual(body["success"], True)
		self.assertEqual(body["result"], DATA[2:][:100])

	def test_get_offset_and_limit(self):
		body = self._get("?offset=5&limit=10")
		self.assertEqual(body["success"], True)
		self.assertEqual(body["result"], DATA[5:][:10])

	def test_get_offset_and_default_limit_and_fields(self):
		body = self._get("?offset=7&fields=msg")
		self.assertEqual(body["success"], True)
		self.assertEqual(body["result"], [{"msg": _dict["msg"]} for _dict in DATA[7:][:100]])

if __name__ == "__main__": unittest.main(verbosity = 2)
