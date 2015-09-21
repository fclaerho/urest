
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

  * Method `select(limit[=100], offset[=0], fields, **kwargs)`:
    1. Returns an iterable object that will be encoded as the response body.
    2. The parameters `limit` and `offset` allow to control pagination.
    3. `fields` allow to select a subset of resulting fields.
    4. `kwargs` allow to select a subset of resulting rows.
    5. Raisable exceptions:
       * `NotImplementedError` if the method or a part of it is not implemented
       * `MethodNotAllowed` if the method is not allowed
       * `ValidationError` on an invalid input
  * Method `create(body)`:
    1. `body` is the decoded request body.
    2. Returns a tuple `(body, querystring, asynchronous)`
    3. `querystring` is used to build the response `Location` header.
    4. `asynchronous`, a boolean. If set, returns *202*, otherwise *201*.
    5. Raisable exceptions:
       * `NotImplementedError` if the method or a part of it is not implemented
       * `MethodNotAllowed` if the method is not allowed
       * `ValidationError` on an invalid input
       * `ResourceExists` on resource conflict
  * Method `update(body)`:
    1. `body` is the decoded request body.
    2. Returns an object that will be encoded as the response body.
    3. Raisable exceptions:
       * `NotImplementedError` if the method or a part of it is not implemented
       * `MethodNotAllowed` if the method is not allowed
       * `ValidationError` on an invalid input
       * `NoSuchResource` on missing resource
       * `LockedError` on resource in use
  * Method `delete(body)`:
    1. `body` is the decoded request body.
    2. Returns an object that will be encoded as the response body.
    3. Raisable exceptions:
       * `NotImplementedError` if the method or a part of it is not implemented
       * `MethodNotAllowed` if the method is not allowed
       * `ValidationError` on an invalid input
       * `NoSuchResource` on missing resource
       * `LockedError` on resource in use

Any other raised exception will be handled as a generic server error.

### FILTERING

For performance reasons, the `.select()` implementation is expected to handle the filtering.
However, if this is not done, you can enable `post-filtering` when instantiating the server.
The post-filtering feature handles the pagination, the field selection and expression matching.


REST Implementation
-------------------

### HTTP CRUD

  * Selection: `GET /<resources>?[offset=][&limit=100][&fields=][&key=value]…`
    1. NOTICE! GET has a default limit of 100 to prevent unwanted DDOS.
    2. On success, returns *200* or *204*.
    3. Any additional pair key=value is considered to be an exact matching.
  * Creation: `POST /<resources>` and `body` contains the payload.
    1. On success, the response `Location` header is set.
    2. On success, returns *201* or *202*.
  * Update: `PUT /<resources>` and `body` contains the payload;
    1. On success, returns *200* or *204*.
  * Deletion: `DELETE /<resources>` and `body` contains `{"name": <string>}`;
    1. On success, returns *200* or *204*.

### HTTP STATUS CODES

  * On success:
    * *201*: Created — a resource has been created
    * *202*: Accepted — a resource creation is ongoing
    * *204*: No Content — the request succeeded but there's no response body
    * *206*: Partial Content — a part of the content has been returned, i.e. paging on GET
    * otherwise *200*: OK — returned if no specific 2xx status code fits
  * On request error:
    * *404*: Not Found — no such resource
    * *405*: Method Not Allowed - http method not allowed on the resource
    * *406*: Not Acceptable — unsupported output formats (Accept header)
    * *409*: Conflict — the resource already exists
    * *415*: Unsupported Media Type — unsupported input formats (Content-Type header)
    * *422*: Unprocessable Entity — request input is invalid
    * *423*: Locked — the resource is in use and cannot be updated/deleted
  * On internal error:
    * *501*: Not Implemented
    * otherwise *500*: Unexpected error

### I/O FORMAT

At the moment, two body formats are supported: `application/json` and `application/xml`.
On request:
  * the HTTP `Content-Type` header defines the request body format
  * The HTTP `Accept` header defines the expected response body format

### RESPONSE STRUCTURE

In JSON (equivalent in XML):
  * On success: `{"success": true, "result": <any>}`
  * On failure: `{"success": false, "exception": <string>}`


References
----------

  * http://blog.octo.com/designer-une-api-rest/ (in French)
  * http://www.restapitutorial.com
  * https://bourgeois.me/rest/