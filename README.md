	  ___        _
	 | _ \___ __| |_
	 |   / -_|_-<  _|
	 |_|_\___/__/\__|

**Tiny REST Framework for Python**
built as a Bottle wrapper implementing REST design recommended practices.
Of course you'll need Bottle as dependency,
get it from your usual python package retailer
or use the version bundled with rest in the `vendor/` subdirectory.

**HTTP STATUS CODES**

  * 201: Successful resource creation
  * 204: Idem, empty response body
  * 406: Unsupported output formats (Accept header)
  * 415: Unsupported input formats (Content-Type header)
  * 422: Invalid input
  * 409: Resource exists
  * 404: No such resource
  * 501: Not implemented

**I/O FORMAT**

At the moment, two formats are supported: `application/json` and `application/xml`
  * The HTTP `Content-Type` header defines the request body format
  * The HTTP `Accept` header defines the response body formats

**HTTP CRUD**

  * Selection: GET /%resource%s?[&fields=][&limit=][&offset=]…
  * Creation:
    POST /%resource%s and body contains the payload
    On successful creation, the response `Location` header is set
  * Update: PUT /%resource%s and body contains the payload
  * Deletion: DELETE /%resource%s {"name": %string%}

**RESPONSE BODY STRUCTURE**

In JSON (equivalent in XML):
  * On success: {"success": true, "result": %any%}
  * On failure: {"success": false, "exception": %string%}

**USAGE**

  * `import rest`
  * Implement the `Model()` base class for each of your resources.
    * `select()`, `update()` and `delete()` return the response body.
    * `create()` returns a pair (body, query) where query is used to build the `Location` header.
  * Instantiate a `Server([hostname="0.0.0.0"], [port=8080])`
  * `.register([path], [model])` each URL path againts a model instance
  * Start the server with `.run()`, press ^C to stop
  * Connect to your endpoint at http://[hostname]:[port]

**EXAMPLE**

	import rest
	class Hello(rest.Model):
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
	server.serve()

**RUN TESTS**

	$ make
