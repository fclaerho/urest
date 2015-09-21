
**Urest** is a tiny Python REST Framework built over [Bottle](http://bottlepy.org/docs/dev/index.html).
It offers a simple resource abstraction to API developers
and takes care of implementing the REST best practices behind the scene.


API Developer's Guide
---------------------

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
	server = urest.Server(post_filtering = True)
	server.register("/employees", Employees())
	server.run()

You can then cURL http://localhost:8080/hello to get the response:

	$ curl -H "Content-Type: application/json" http://localhost:8080/hello

### INSTALLATION

Do not install urest directly, register it as a requirement of your package instead.

In your package's `setup.py`:
  * Add `urest` to the `install_requires` list
  * Add `urest` to the `tests_require` list 

### RESOURCES INTERFACE

  * Method `select(limit[=100], offset[=0], fields, **kwargs)`:
    1. Input:
       * The parameters `limit` and `offset` allow to control pagination.
       * `fields` allow to select a subset of resulting fields.
       * `kwargs` allow to select a subset of resulting rows.
    2. Output: **iterable** object that will be encoded as the response body.
    3. Raisable exceptions:
       * `NotImplementedError` if the method or a part of it is not implemented
       * `MethodNotAllowed` if the method is not allowed
       * `ValidationError` on an invalid input
  * Method `create(body)`:
    1. Input: `body` is the decoded request body.
    2. Output: tuple `result, querystring, asynchronous`
       * `result` will be encoded as the response body
       * `querystring` is used to build the response `Location` header.
       * `asynchronous`, a boolean. If set, returns **202**, otherwise **201**.
    3. Raisable exceptions:
       * `NotImplementedError` if the method or a part of it is not implemented
       * `MethodNotAllowed` if the method is not allowed
       * `ValidationError` on an invalid input
       * `ResourceExists` on resource conflict
  * Method `update(body)`:
    1. Input: `body` is the decoded request body.
    2. Output: object that will be encoded as the response body.
    3. Raisable exceptions:
       * `NotImplementedError` if the method or a part of it is not implemented
       * `MethodNotAllowed` if the method is not allowed
       * `ValidationError` on an invalid input
       * `NoSuchResource` on missing resource
       * `LockedError` on resource in use
  * Method `delete(body)`:
    1. Input: `body` is the decoded request body.
    2. Output: object that will be encoded as the response body.
    3. Raisable exceptions:
       * `NotImplementedError` if the method or a part of it is not implemented
       * `MethodNotAllowed` if the method is not allowed
       * `ValidationError` on an invalid input
       * `NoSuchResource` on missing resource
       * `LockedError` on resource in use

Any other exception will be handled as a generic server error.

### FILTERING

For performance reasons, the `.select()` implementation is expected to handle the filtering.
However, if this is not done, you can enable `post-filtering` when instantiating the server.
The post-filtering feature handles the pagination, the field selection and expression matching.


REST Implementation: Client's Guide
-----------------------------------

### HTTP CRUD

  * Selection: `GET /<resources>?[offset=0][&limit=100][&fields=][&key=value]…`
    - On success:
      * returns **200** or **206** on a partial content.
      * set the header `Content-Range: lbound-ubound/max`
      * set the header `Accept-Range: <resource> max`
  * Creation: `POST /<resources> HEADERS {"Content-Type": …, "Accept": …} BODY …`
    - On success:
      * returns **201** or **202** on an asynchronous operation.
      * set the header `Location`
  * Update: `PUT /<resources> HEADERS {"Content-Type": …, "Accept": …} BODY …`
    - On success, returns **200** or **204** if there's no response body.
  * Deletion: `DELETE /<resources> HEADERS {"Content-Type": …, "Accept": …} BODY …`
    - On success, returns **200** or **204** if there's no response body.

### HTTP STATUS CODES

  * On success:
    * **201**: Created — a resource has been created
    * **202**: Accepted — a resource creation is ongoing
    * **204**: No Content — the request succeeded but there's no response body
    * **206**: Partial Content — a part of the content has been returned, i.e. paging on GET
    * otherwise **200**: OK — returned if no specific 2xx status code fits
  * On request error:
    * **404**: Not Found — no such resource
    * **405**: Method Not Allowed - http method not allowed on the resource
    * **406**: Not Acceptable — unsupported output formats (Accept header)
    * **409**: Conflict — the resource already exists
    * **415**: Unsupported Media Type — unsupported input formats (Content-Type header)
    * **422**: Unprocessable Entity — request input is invalid
    * **423**: Locked — the resource is in use and cannot be updated/deleted
  * On internal error:
    * **501**: Not Implemented
    * otherwise **500**: Unexpected error

### I/O FORMAT

At the moment, two body formats are supported: `application/json` and `application/xml`.

On request:
  * the HTTP `Content-Type` header defines the request body format
  * The HTTP `Accept` header defines the expected response body format

### RESPONSE STRUCTURE

In JSON (equivalent in XML):
  * On success: `{"success": true, "result": <object>}`
  * On failure: `{"success": false, "exception": <string>}`


References
----------

  * http://blog.octo.com/designer-une-api-rest/ (in French)
  * http://www.restapitutorial.com
  * https://bourgeois.me/rest/
