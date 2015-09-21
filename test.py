# copyright (c) 2015 fclaerhout.fr, released under the MIT license.

import unittest, json, re

import bottle, urest, fckit # 3rd-party

MSG = ["Hello, World!", "blah", "lorem ipsum"]
DATA = [{"id": i, "msg": MSG[min(i, len(MSG) - 1)]} for i in xrange(200)]

class Messages(urest.Resources):

	def select(self, **kwargs):
		return DATA

	def create(self, obj):
		raise MethodNotAllowed

	def update(self, obj):
		raise MethodNotAllowed

	def delete(self, obj):
		raise MethodNotAllowed

	def __len__(self):
		return len(DATA)

PROXYPORT = None # set this to debug with a local proxy
PATH = "/messages"
PORT = 9999

class Test(unittest.TestCase):

	def setUp(self):
		server = urest.Server(port = PORT, post_filtering = True)
		server.register(PATH, Messages())
		self.process = fckit.async(server.run, threaded = False)

	def tearDown(self):
		self.process.terminate()

	def _get(self, querystring = None):
		res = fckit.http_request(
			hostname = "localhost",
			port = PROXYPORT or PORT,
			method = "GET",
			headers = {"Accept": "application/json"},
			path = "%s%s%s" % (("http://localhost:%i" % PORT) if PROXYPORT else "", PATH, querystring or ""))  
		self.assertIn(res.status, (200, 206))
		if res.status == 206:
			content_range = res.getheader("Content-Range")
			lbound, ubound, count = map(int, re.match(r"(\d+)-(\d+)/(\d+)", content_range).groups())
			self.assertLessEqual(lbound, ubound)
			self.assertLessEqual(ubound, count)
			accept_range = res.getheader("Accept-Range")
			name, maxcount = re.match(r"(\w+) (\d+)", accept_range).groups()
			maxcount = int(maxcount)
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
