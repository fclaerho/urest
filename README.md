	  ___        _
	 | _ \___ __| |_
	 |   / -_|_-<  _|
	 |_|_\___/__/\__|

[![Build Status](https://secure.travis-ci.org/fclaerho/rest.png?branch=master)](http://travis-ci.org/fclaerho/rest)

**Tiny REST Framework for Python**
built as a Bottle wrapper implementing REST design recommended practices.
Of course you'll need Bottle as dependency,
get it from your usual python package retailer
or use the version bundled with rest in the `vendor/` subdirectory.

HTTP STATUS CODES
-----------------

  * 201: Created — the resource has been created
  * 202: Accepted — the resource creation is ongoing
  * 204: No Content — the request succeeded but there's no response body
  * 404: Not Found — no such resource
  * 406: Not Acceptable — unsupported output formats (Accept header)
  * 409: Conflict — the resource already exists
  * 415: Unsupported Media Type — unsupported input formats (Content-Type header)
  * 422: Unprocessable Entity — request input is invalid
  * 501: Not Implemented

I/O FORMAT
----------

At the moment, two formats are supported: `application/json` and `application/xml`
  * The HTTP `Content-Type` header defines the request body format
  * The HTTP `Accept` header defines the response body formats

HTTP CRUD
---------

  * Selection: GET /%resources%?[&fields=][&limit=][&offset=]…
  * Creation:
    POST /%resources% and body contains the payload
    On successful creation, the response `Location` header is set
  * Update: PUT /%resources% and body contains the payload
  * Deletion: DELETE /%resources% {"name": %string%}

RESPONSE BODY STRUCTURE
-----------------------

In JSON (equivalent in XML):
  * On success: {"success": true, "result": %any%}
  * On failure: {"success": false, "exception": %string%}

USAGE
-----

  * `import rest`
  * Implement the `Resources()` base class for each of your resources.
    * `select()`, `update()` and `delete()` return the response body.
    * `create()` returns a tuple (body, querystring, asynchronous)
      * querystring: used to build the response `Location` header
      * asynchronous: if True, use 202 as response status code, 201 otherwise
  * Instantiate a `Server([hostname="0.0.0.0"], [port=8080])`
  * `.register([path], [model])` each URL path againts a model instance
  * Start the server with `.run([quiet=False],[debug=False])`, press ^C to stop
  * Connect to your endpoint at http://%hostname%[:%port%]

EXCEPTIONS
----------

For a proper handling of the HTTP status codes:

  * `select()` must raise:
    * `ValidationError` on an invalid input
  * `create()` must raise:
    * `ValidationError` on an invalid input
    * `ResourceExists` on resource conflict
  * `update()` must raise:
    * `ValidationError` on an invalid input
    * `NoSuchResource` on missing resource
  * `delete()` must raise:
    * `ValidationError` on an invalid input
    * `NoSuchResource` on missing resource

Raise `NotImplementedError` if a method is not implemented.
Any other exception will be handled as 500.

EXAMPLE
-------

	import rest
	class Hello(rest.Resources):
		def select(self, **kwargs):
			return {"msg": "hello world!"}
		def create(self, body):
			raise NotImplementedError("cannot create")
		def update(self, body):
			raise NotImplementedError("cannot update")
		def delete(self, body):
			raise NotImplementedError("cannot delete")
	server = rest.Server()
	server.register("/hello", Hello())
	server.run()
