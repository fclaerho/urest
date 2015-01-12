# copyright (c) 2015 fclaerhout.fr, released under the MIT license.

import unittest, json

import bottle, rest

def http_request(
	hostname,
	port,
	method,
	path,
	username = None,
	password = None,
	timeout = 2,
	headers = None,
	body = None):
	import httplib, base64
	headers = headers or {}
	assert username and password or (not username and not password), "missing username or password"
	if username and password:
		auth = base64.encodestring("%s:%s" % (username, password)).rstrip()
		headers.update({"Authorization": "Basic %s" % auth})
	cnx = httplib.HTTPConnection(
		host = hostname,
		port = port,
		timeout = timeout)
	cnx.request(
		method = method,
		url = path,
		headers = headers,
		body = body or "")
	res = cnx.getresponse()
	return res

MSG = "hello, world!"

class Hello(rest.Model):

	def select(self, **kwargs):
		return {"msg": MSG}

	def create(self, body):
		raise NotImplementedError()

	def update(self, body):
		raise NotImplementedError()

	def delete(self, body):
		raise NotImplementedError()

class Test(unittest.TestCase):

	def setUp(self):
		self.server = rest.Server()
		self.server.register("/hello", Hello())
		self.server.start()
		self.server.wait_up()

	def tearDown(self):
		self.server.stop()

	def test_get(self):
		res = http_request(
			hostname = "localhost",
			port = 8080,
			method = "GET",
			path = "/hello")
		self.assertEqual(res.status, 200)
		body = json.loads(res.read())
		self.assertEqual(body["success"], True)
		self.assertEqual(body["result"], {"msg": MSG})

if __name__ == "__main__": unittest.main(verbosity = 2)
