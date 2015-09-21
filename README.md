
**Urest** is a tiny Python REST Framework built over [Bottle](http://bottlepy.org/docs/dev/index.html).
It offers a simple resource abstraction to API developers
and takes care of implementing the REST best practices behind the scene.


Developer's Guide
-----------------

### EXAMPLE

	import urest
	class Employees(urest.Resources):
		def select(self, *args, **kwargs):
			return [{"firstname": "john", "lastname": "doe", "position": "hr"}]
		def create(self, body):
			raise urest.MethodNotAllowed
		def update(self, body):
			raise urest.MethodNotAllowed
		def delete(self, body):
			raise urest.MethodNotAllowed
		def __len__(self):
			return 1
	server = urest.Server(filtering = True)
	server.register("/employees", Employees())
	server.run()

You can then cURL http://localhost:8080/hello to get the response:

	$ curl -H "Content-Type: application/json" http://localhost:8080/hello

### INSTALLATION

	$ pip install --user urest

or, if the PyPI repository is not available:

	$ pip install --user git+https://github.com/fclaerho/urest.git

To uninstall:

	$ pip uninstall urest

### RESOURCES INTERFACE

  * `select(self, limit, offset, fields, **kwargs)`
    Returns an iterable object that will be encoded as the response body.
  * `create(self, body)`
    Returns a tuple `(body, querystring, asynchronous)`
    * querystring: used to build the response `Location` header, e.g. `?id=1`
    * asynchronous: if True, use 202 as response status code, 201 otherwise
  * `update(self, body)`
    Returns an object that will be encoded as the response body.
  * `delete(self, body)`
    Returns an object that will be encoded as the response body.

### FILTERING

For performance reasons, the `.select()` implementation is expected to handle the filtering.
However, if this is not done, you can enable post-filtering when instantiating the server.

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


REST Implementation
-------------------

### HTTP CRUD

  * Selection:
    `GET /<resources>?[offset=][&limit=100][&fields=][&key=value]…`;
    NOTICE! GET has a default limit of 100 to prevent unwanted DDOS.
    Expect 200 on success.
    Any additional pair key=value is considered to be an exact matching.
  * Creation:
    `POST /<resources>` and `body` contains the payload.
    On successful creation, the response `Location` header is set.
    Expect 201 (or 202 if async) on success.
  * Update: `PUT /<resources>` and `body` contains the payload;
    expect 200 (or 204 on empty body) on success.
  * Deletion: `DELETE /<resources>` and `body` contains `{"name": <string>}`;
    expect 200 (or 204 on empty body) on success.

### HTTP STATUS CODES

  * 200: OK — returned if no specific 2xx status code fits
  * 201: Created — the resource has been created
  * 202: Accepted — the resource creation is ongoing
  * 204: No Content — the request succeeded but there's no response body
	* 206: Partial Content — paging on GET
  * 404: Not Found — no such resource
  * 405: Method Not Allowed - http method not allowed on the resource
  * 406: Not Acceptable — unsupported output formats (Accept header)
  * 409: Conflict — the resource already exists
  * 415: Unsupported Media Type — unsupported input formats (Content-Type header)
  * 422: Unprocessable Entity — request input is invalid
  * 423: Locked — the resource is in use and cannot be updated/deleted
  * 501: Not Implemented

### I/O FORMAT

At the moment, two body formats are supported: `application/json` and `application/xml`.
On request:
  * the HTTP `Content-Type` header defines the request body format
  * The HTTP `Accept` header defines the expected response body format

### RESPONSE STRUCTURE

In JSON (equivalent in XML):
  * On success: `{"success": true, "result": %any%}`
  * On failure: `{"success": false, "exception": %string%}`


References
----------

  * http://blog.octo.com/designer-une-api-rest/ (in French)
  * http://www.restapitutorial.com
  * https://bourgeois.me/rest/