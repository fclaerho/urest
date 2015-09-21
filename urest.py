# copyright (c) 2014-2015 fclaerhout.fr, released under the MIT license.
# coding: utf-8

import xml.etree.ElementTree as ET, json, yaml, abc

import bottle # 3rd-party

##############
# exceptions #
##############

class Error(Exception):

	def __str__(self):
		return ": ".join(map(str, self.args))

class SyntaxError(Error): pass

class FormatError(Error): pass

class ResourceExists(Error): pass

class NoSuchResource(Error): pass

class ValidationError(Error): pass

class MethodNotAllowed(Error): pass

class RangeNotSatisfiable(Error): pass

class LockedResourceError(Error): pass

#############
# interface #
#############

class Resources(object):

	__metaclass__ = abc.ABCMeta

	@abc.abstractmethod
	def select(self, limit, offset, fields, **kwargs): pass

	@abc.abstractmethod
	def create(self, body): pass

	@abc.abstractmethod
	def update(self, body): pass

	@abc.abstractmethod
	def delete(self, body): pass

	@abc.abstractmethod
	def __len__(self): pass

##################
# implementation #
##################

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

	class XMLDict(object):

		def __init__(self, elem):
			self.elem = elem

		def __iter__(self):
			return (child.tag for child in self.elem)

		def values(self):
			return (XMLDict(child) for child in self.elem)

		def items(self):
			return ((child.tag, XMLDict(child)) for child in self.elem)

		def keys(self):
			return (child.tag for child in self.elem)

	@classmethod
	def loads(cls, string):
		return XMLDict(ET.fromstring(string)) # FIXME

class Server(object):

	def __init__(self, json_encoder_cls = None, post_filtering = False, hostname = "0.0.0.0", port = 8080):
		self.json_encoder_cls = json_encoder_cls
		self.post_filtering = post_filtering
		self.hostname = hostname
		self.port = port

	def _Response(self, obj, status, headers):
		"configure bottle response and return data"
		# RFC 2616 §14.1: If no Accept header field is present, then is is assumed
		# that the client accepts all media types. […] If an Accept header field is
		# present, and if the server cannot send a response which is acceptable
		# according to the combined Accept field value, then the server SHOULD send
		# a 406 (not acceptable) response.
		accepted_ct = bottle.request.headers.get("Accept")
		for ct, dump in (
			("application/json", lambda obj: json.dumps(obj, cls = self.json_encoder_cls)),
			("application/yaml", yaml.dump),
			("application/xml", xml.dumps)):
			if accepted_ct in (None, ct): 
				bottle.response.status = status
				bottle.response.headers.update(headers)
				bottle.response.content_type = ct
				return dump(obj)
		else:
			bottle.response.status = 406
			return None

	def Success(self, result = None, status = 200, headers = None, **kwargs):
		return self._Response(
			dict({"success": True, "result": result}, **kwargs),
			status = status,
			headers = headers or {})

	def Failure(self, exception, status = 400):
		return self._Response({
				"success": False,
				"exception": "%s: %s" % (type(exception).__name__, exception),
			},
			status = status,
			headers = {})

	def select(self, resources):
		try:
			# parse query string:
			fields = bottle.request.query.fields.split(",") if bottle.request.query.fields else ()
			offset = 0
			limit = None 
			kwargs = {}
			for key, value in bottle.request.query.items():
				if key == "range": # shortcut
					offset, ubound = value.split("-")
					if ubound:
						limit = ubound - offset
				elif key == "limit":
					limit = int(value)
				elif key == "offset":
					offset = int(value)
				elif key == "fields":
					fields = value.split(",")
				else:
					kwargs[key] = value
			rows = resources.select(
				limit = limit,
				offset = offset,
				fields = fields,
				**kwargs)
			if self.post_filtering:
				# select range of rows:
				if offset:
					rows = rows[offset:]
				if limit:
					rows = rows[:limit]
				# select matching rows:
				for key, value in kwargs.items():
					rows = filter(
						lambda row: key in row and type(row[key])(value) == row[key],
						rows)
				# filter fields:
				rows = map(
					lambda row: {key: value for key,value in row.items() if not fields or key in fields},
					rows)
			count = len(resources)
			if limit <= count:
				return self.Success(rows)
			else:
				return self.Success(
					result = rows,
					status = 206,
					headers = {
						"Content-Range": "resource %i-%i/%i" % (offset, offset + limit, count),
						"Accept-Range": "resource",
					})
		except MethodNotAllowed as exc:
			return self.Failure(exc, status = 405)
		except RangeNotSatisfiable as exc:
			return self.Failure(exc, status = 416)
		except ValidationError as exc:
			return self.Failure(exc, status = 422)
		except NotImplementedError as exc:
			return self.Failure(exc, status = 501)
		except Exception as exc:
			return self.Failure(exc, status = 500)

	def parse_body(self):
		"return parsed object on success, raise FormatError or SyntaxError on failure"
		content_type = bottle.request.headers.get("Content-Type")
		for ct, load in (
			("application/json", json.loads),
			("application/yaml", yaml.load),
			("application/xml", xml.loads)):
			if content_type == ct:
				return load(bottle.request.body.read())
		else:
			raise FormatError(content_type, "unsupported input content-type")

	def create(self, resources):
		try:
			body = self.parse_body()
		except FormatError as exc:
			return self.Failure(exc, status = 415)
		except Exception as exc:
			return self.Failure(exc, status = 400)
		try:
			result, querystring, asynchronous = resources.create(body)
			return self.Success(
				result = result,
				status = 202 if asynchronous else 201,
				headers = {"Location": "%s?%s" % (bottle.request.url, querystring)})
		except MethodNotAllowed as exc:
			return self.Failure(exc, status = 405)
		except ResourceExists as exc:
			return self.Failure(exc, status = 409)
		except ValidationError as exc:
			return self.Failure(exc, status = 422)
		except NotImplementedError as exc:
			return self.Failure(exc, status = 501)
		except Exception as exc:
			return self.Failure(exc, status = 500)

	def update(self, resources):
		try:
			body = self.parse_body()
		except FormatError as exc:
			return self.Failure(exc, status = 415)
		except Exception as exc:
			return self.Failure(exc, status = 400)
		try:
			return self.Success(
				result = resources.update(body),
				status = 200 if result else 204)
		except NoSuchResource as exc:
			return self.Failure(exc, status = 404)
		except MethodNotAllowed as exc:
			return self.Failure(exc, status = 405)
		except ValidationError as exc:
			return self.Failure(exc, status = 422)
		except LockedResourceError as exc:
			return self.Failure(exc, status = 423)
		except NotImplementedError as exc:
			return self.Failure(exc, status = 501)
		except Exception as exc:
			return self.Failure(exc, status = 500)

	def delete(self, model):
		try:
			body = self.parse_body()
		except FormatError as exc:
			return self.Failure(exc, status = 415)
		except Exception as exc:
			return self.Failure(exc, status = 400)
		try:
			return self.Success(
				result = model.delete(body),
				status = 200 if result else 204)
		except NoSuchResource as exc:
			return self.Failure(exc, status = 404)
		except MethodNotAllowed as exc:
			return self.Failure(exc, status = 405)
		except ValidationError as exc:
			return self.Failure(exc, status = 422)
		except LockedResourceError as exc:
			return self.Failure(exc, status = 423)
		except NotImplementedError as exc:
			return self.Failure(exc, status = 501)
		except Exception as exc:
			return self.Failure(exc, status = 500)

	def register(self, path, resources):
		bottle.route(path, "GET", lambda: self.select(resources))
		bottle.route(path, "PUT", lambda: self.update(resources))
		bottle.route(path, "POST", lambda: self.create(resources))
		bottle.route(path, "DELETE", lambda: self.delete(resources))

	def run(self, verbose = False):
		bottle.run(
			host = self.hostname,
			port = self.port,
			quiet = not verbose,
			debug = verbose)
