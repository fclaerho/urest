
Tiny Python REST Framework built over [Bottle](http://bottlepy.org/docs/dev/index.html) and implementing REST good practices:
  * http://www.restapitutorial.com
  * https://bourgeois.me/rest/


Example
-------

	import urest
	class Hello(urest.Resources):
		def select(self, **kwargs):
			return [{"msg": "hello world!"}]
		def create(self, body):
			raise urest.MethodNotAllowed
		def update(self, body):
			raise urest.MethodNotAllowed
		def delete(self, body):
			raise urest.MethodNotAllowed
	server = urest.Server()
	server.register("/hello", Hello())
	server.run()


Installation
------------

	$ pip install --user urest

or, if the PyPI repository is not available:

	$ pip install --user git+https://github.com/fclaerho/urest.git

The package will be installed in your [user site-packages](https://www.python.org/dev/peps/pep-0370/#specification) directory; make sure its `bin/` sub-directory is in your shell lookup path.

To uninstall:

	$ pip uninstall urest


Usage
-----

### OVERVIEW

  * In your code:
    * `import urest`
    * Implement the `Resources()` base class for each of your resources.
      * `select()`, `update()` and `delete()` return the response body.
      * `create()` returns a tuple (body, querystring, asynchronous)
        * querystring: used to build the response `Location` header
        * asynchronous: if True, use 202 as response status code, 201 otherwise
    * Instantiate a `Server([hostname="0.0.0.0"], [port=8080])`
    * `.register([path], [resources])` each URL path againts a Resources instance
  * Start the server with `.run([quiet=False],[debug=False])`, press ^C to stop
  * Connect to your endpoint at http://%hostname%[:%port%]

### HTTP STATUS CODES

  * 200: OK — returned if no specific 2xx status code fits
  * 201: Created — the resource has been created
  * 202: Accepted — the resource creation is ongoing
  * 204: No Content — the request succeeded but there's no response body
  * 404: Not Found — no such resource
  * 405: Method Not Allowed - http method not allowed on the resource
  * 406: Not Acceptable — unsupported output formats (Accept header)
  * 409: Conflict — the resource already exists
  * 415: Unsupported Media Type — unsupported input formats (Content-Type header)
  * 422: Unprocessable Entity — request input is invalid
  * 423: Locked — the resource is in use and cannot be updated/deleted
  * 501: Not Implemented

### I/O FORMAT

At the moment, two formats are supported: `application/json` and `application/xml`
  * The HTTP `Content-Type` header defines the request body format
  * The HTTP `Accept` header defines the response body formats

### HTTP CRUD

  * Selection: `GET /%resources%?[&fields=][&limit=][&offset=]…`;
    expect 200 on success.
    Any additional pair key=value is considered to be an exact matching;
    Any additional pair x-key=value is forwarded as argument to the Resources.select() method.
  * Creation:
    `POST /%resources%` and `body` contains the payload.
    On successful creation, the response `Location` header is set.
    Expect 201 (or 202 if async) on success.
  * Update: `PUT /%resources%` and `body` contains the payload;
    expect 200 (or 204 on empty body) on success.
  * Deletion: `DELETE /%resources%` and `body` contains `{"name": %string%}`;
    expect 200 (or 204 on empty body) on success.

### RESPONSE STRUCTURE

In JSON (equivalent in XML):
  * On success: `{"success": true, "result": %any%}`
  * On failure: `{"success": false, "exception": %string%}`

### EXCEPTIONS

For a proper handling of the HTTP status codes:

  * `select()` must raise:
    * `NotImplementedError` if a method or a part of it is not implemented
    * `MethodNotAllowed` if the method is not allowed
    * `ValidationError` on an invalid input
  * `create()` must raise:
    * `NotImplementedError` if a method or a part of it is not implemented
    * `MethodNotAllowed` if the method is not allowed
    * `ValidationError` on an invalid input
    * `ResourceExists` on resource conflict
  * `update()` must raise:
    * `NotImplementedError` if a method or a part of it is not implemented
    * `MethodNotAllowed` if the method is not allowed
    * `ValidationError` on an invalid input
    * `NoSuchResource` on missing resource
    * `LockedError` on resource in use
  * `delete()` must raise:
    * `NotImplementedError` if a method or a part of it is not implemented
    * `MethodNotAllowed` if the method is not allowed
    * `ValidationError` on an invalid input
    * `NoSuchResource` on missing resource
    * `LockedError` on resource in use

Any other exception will be handled as 500.
