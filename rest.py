# copyright (c) 2014-2015 fclaerhout.fr, released under the MIT license.

import json, abc

import bottle # 3rd-party

class LockedResourceError(Exception): pass

class MethodNotAllowed(Exception): pass

class ValidationError(Exception): pass

class NoSuchResource(Exception): pass

class ResourceExists(Exception): pass

class FormatError(Exception): pass

class SyntaxError(Exception): pass

class Resources(object):

	__metaclass__ = abc.ABCMeta

	@abc.abstractmethod
	def select(self, **kwargs):
		raise NotImplementedError("select not implemented")

	@abc.abstractmethod
	def create(self, body):
		raise NotImplementedEror("create not implemented")

	@abc.abstractmethod
	def update(self, body):
		raise NotImplementedEror("update not implemented")

	@abc.abstractmethod
	def delete(self, body):
		raise NotImplementedEror("delete not implemented")

class xml:
	"poorman xml serializer"

	@classmethod
	def _list_to_xml(cls, obj):
		body = "\n".join(map(lambda value: "<value>%s</value>" % cls._object_to_xml(value), obj))
		return "<list>%s</list>" % body

	@classmethod
	def _dict_to_xml(cls, obj):
		body = "\n".join(map(lambda key: "<value name='%s'>%s</value>" % (key, cls._object_to_xml(obj[key])), obj))
		return "<dict>%s</dict>" % body

	@classmethod
	def _object_to_xml(cls, obj):
		if obj is None:
			return "<None/>"
		elif isinstance(obj, (str, unicode)):
			return ("<str>%s</str>" % obj)
		elif isinstance(obj, (int, float)):
			return ("<number>%s</number>" % obj)
		elif isinstance(obj, bool):
			return ("<bool>%s</bool>" % obj)
		elif isinstance(obj, (list, tuple)):
			return cls._list_to_xml(obj)
		elif isinstance(obj, dict):
			return cls._dict_to_xml(obj)
		else:
			raise NotImplementedError("%s: unsupported type" % type(obj).__name__)

	@classmethod
	def dumps(cls, obj):
		return "<?xml version='1.0'?>\n%s" % cls._object_to_xml(obj)

	@classmethod
	def loads(cls, string):
		raise NotImplementedError("cannot load string yet")

class Server(object):

	def __init__(self, hostname = "0.0.0.0", port = 8080, json_encoder_cls = None):
		self.json_encoder_cls = json_encoder_cls
		self.hostname = hostname
		self.thread = None
		self.port = port

	def Response(self, obj, status, headers):
		accepted = bottle.request.headers.get("Accept")
		supported = ("application/json", "application/xml")
		if not accepted or any(map(lambda ct: ct in accepted, supported)):
			bottle.response.status = status
			bottle.response.headers.update(headers)
			if not accepted or "application/json" in accepted:
				bottle.response.content_type = "application/json"
				return json.dumps(obj, cls = self.json_encoder_cls)
			elif "application/xml" in accepted:
				bottle.response.content_type = "application/xml"
				return xml.dumps(obj)
		else:
			bottle.response.status = 406 # unsupported accepted content-types
			return None

	def Success(self, result = None, status = 200, headers = None, **kwargs):
		return self.Response(
			dict({"success": True, "result": result}, **kwargs),
			status = status,
			headers = headers or {})

	def Failure(self, exception, status = 400):
		return self.Response({
				"success": False,
				"exception": "%s: %s" % (type(exception).__name__, exception),
			},
			status = status,
			headers = {})

	def select(self, resources):
		try:
			fields = bottle.request.query.fields.split(",") if bottle.request.query.fields else None
			limit = int(bottle.request.query.limit or 20)
			offset = int(bottle.request.query.offset or 0)
			rows = resources.select(**bottle.request.query)
			if len(rows) > limit:
				rows = rows[offset:offset + limit]
			if fields:
				def filtered(row):
					res = {}
					for key in row:
						if key in fields:
							res[key] = row[key]
					return res
				rows = map(filtered, rows)
			return self.Success(rows, status = 200)
		except NotImplementedError as e:
			return self.Failure(e, status = 501)
		except MethodNotAllowed as e:
			return self.Failure(e, status = 405)
		except ValidationError as e:
			return self.Failure(e, status = 400)
		except Exception as e:
			return self.Failure(e, status = 500)

	def parse_body(self):
		"return parsed object on success, raise FormatError or SyntaxError on failure"
		content_type = bottle.request.headers.get("Content-Type")
		if content_type == "application/json":
			return json.loads(bottle.request.body.read())
		elif content_type == "application/xml":
			return xml.loads(bottle.request.body.read())
		else:
			raise FormatError("%s: unsupported input content-type" % content_type)

	def create(self, resources):
		try:
			body = self.parse_body()
		except FormatError as e:
			return self.Failure(e, status = 415)
		except Exception as e:
			return self.Failure(e, status = 422)
		try:
			result, querystring, asynchronous = resources.create(body)
			assert result, "create result cannot be null"
			return self.Success(
				result,
				status = 202 if asynchronous else 201,
				headers = {"Location": "%s?%s" % (bottle.request.url, querystring)})
		except NotImplementedError as e:
			return self.Failure(e, status = 501)
		except MethodNotAllowed as e:
			return self.Failure(e, status = 405)
		except ValidationError as e:
			return self.Failure(e, status = 422)
		except ResourceExists as e:
			return self.Failure(e, status = 409)
		except Exception as e:
			return self.Failure(e, status = 500)

	def update(self, resources):
		try:
			body = self.parse_body()
		except FormatError as e:
			return self.Failure(e, status = 415)
		except Exception as e:
			return self.Failure(e, status = 422)
		try:
			result = resources.update(body)
			return self.Success(result, status = 200 if result else 204)
		except NotImplementedError as e:
			return self.Failure(e, status = 501)
		except MethodNotAllowed as e:
			return self.Failure(e, status = 405)
		except ValidationError as e:
			return self.Failure(e, status = 422)
		except NoSuchResource as e:
			return self.Failure(e, status = 404)
		except LockedResourceError as e:
			return self.Failure(e, status = 423)
		except Exception as e:
			return self.ailure(e, status = 500)

	def delete(self, model):
		try:
			body = self.parse_body()
		except FormatError as e:
			return self.Failure(e, status = 415)
		except Exception as e:
			return self.Failure(e, status = 422)
		try:
			result = model.delete(body)
			return self.Success(result, status = 200 if result else 204)
		except NotImplementedError as e:
			return self.Failure(e, status = 501)
		except MethodNotAllowed as e:
			return self.Failure(e, status = 405)
		except ValidationError as e:
			return self.Failure(e, status = 422)
		except NoSuchResource as e:
			return self.Failure(e, status = 404)
		except LockedResourceError as e:
			return self.Failure(e, status = 423)
		except Exception as e:
			return self.Failure(e, status = 500)

	def register(self, path, resources):
		bottle.route(path, "GET", lambda: self.select(resources))
		bottle.route(path, "PUT", lambda: self.update(resources))
		bottle.route(path, "POST", lambda: self.create(resources))
		bottle.route(path, "DELETE", lambda: self.delete(resources))

	def run(self, quiet = False, debug = False):
		bottle.run(host = self.hostname, port = self.port, quiet = quiet, debug = debug)
