
**Urest** is a tiny Python REST Framework built over [Bottle](http://bottlepy.org/docs/dev/index.html).
It offers a simple resource abstraction to API developers
and takes care of implementing the REST best practices behind the scene.


Server Side: API Developer's Guide
----------------------------------

### EXAMPLE

	import urest
	class Messages(urest.Resources):
		def select(self, *args, **kwargs):
			return [{"msg": "hello world!"}]
		def create(self, obj):
			raise urest.MethodNotAllowed
		def update(self, obj):
			raise urest.MethodNotAllowed
		def delete(self, obj):
			raise urest.MethodNotAllowed
		def __len__(self):
			return len(self.memdb)
	server = urest.Server(post_filtering = True)
	server.register("/messages", Messages())
	server.run()

You can then cURL the endpoint:

	$ curl -H "Content-Type: application/json" http://localhost:8080/messages?limit=4

### INSTALLATION

Do not install **Urest** directly, register it as a requirement of your package instead:
in `setup.py`, add `urest` to the `install_requires` and `tests_require` lists.

### RESOURCES INTERFACE

  * **Method `select()`**:
    1. Parameters:
       * `limit` and `offset` allow to control paging.
       * `fields` (list of strings) allow to select result columns.
       * `kwargs` (conjunction of equalities) allow to filter rows.
    2. Return: **iterable** object that will be encoded as the response body.
    3. Raisable exceptions:
       * `NotImplementedError` if the method or a part of it is not implemented
       * `MethodNotAllowed` if the method is not allowed
       * `ValidationError` on an invalid input
  * **Method `create()`**:
    1. Parameters: `obj` is the decoded request body.
    2. Return: tuple `result, querystring, asynchronous`
       * `result` will be encoded as the response body
       * `querystring` is used to build the response `Location` header.
       * `asynchronous`, a boolean. If set, returns **202**, otherwise **201**.
    3. Raisable exceptions:
       * `NotImplementedError` if the method or a part of it is not implemented
       * `MethodNotAllowed` if the method is not allowed
       * `ValidationError` on an invalid input
       * `ResourceExists` on resource conflict
  * **Method `update()`**:
    1. Parameters: `obj` is the decoded request body.
    2. Return: object that will be encoded as the response body.
    3. Raisable exceptions:
       * `NotImplementedError` if the method or a part of it is not implemented
       * `MethodNotAllowed` if the method is not allowed
       * `ValidationError` on an invalid input
       * `NoSuchResource` on missing resource
       * `LockedError` on resource in use
  * **Method `delete()`**:
    1. Parameters: `obj` is the decoded request body.
    2. Return: object that will be encoded as the response body.
    3. Raisable exceptions:
       * `NotImplementedError` if the method or a part of it is not implemented
       * `MethodNotAllowed` if the method is not allowed
       * `ValidationError` on an invalid input
       * `NoSuchResource` on missing resource
       * `LockedError` on resource in use

Any other exception will be handled as a generic server error.

### FILTERING

For performance reasons, the `select()` implementation is expected to handle the filtering,
that is the `offset`, `limit`, `fields` and `kwargs` constraints.
You can also let the server do this work by setting the `post-filtering` flag.


Client Side: REST Implementation
--------------------------------

### HTTP CRUD

  * Selection: `GET /<resources>?[range=…][offset=…][&limit=…][&fields=…][&key=value]… HEADERS {["Accept":…], …}`
    - Paging is supported both via querystring and range requests (RFC 7233, `Range` header.)
    - For querystring paging, you may use `range` (x-y, -y, x-) OR `offset`+`limit` for paging
    - On success:
      * returns **200** or **206** on a partial content.
      * set the header `Content-Range: resource <offset>-<offset+limit>/<count>`
      * set the header `Accept-Range: resource`
  * Creation: `POST /<resources> HEADERS {"Content-Type": …, ["Accept": …], …} BODY …`
    - On success:
      * returns **201** or **202** on an asynchronous operation.
      * set the header `Location: <resource_url>`
  * Update: `PUT /<resources> HEADERS {"Content-Type": …, ["Accept": …], …} BODY …`
    - On success, returns **200** or **204** if there's no response body.
  * Deletion: `DELETE /<resources> HEADERS {"Content-Type": …, ["Accept": …], …} BODY …`
    - On success, returns **200** or **204** if there's no response body.

### HTTP STATUS CODES

  * On success:
    * **201**: Created — a resource has been created
    * **202**: Accepted — a resource creation is ongoing
    * **204**: No Content — the request succeeded but there's no response body
    * **206**: Partial Content — a part of the content has been returned, i.e. paging on GET
    * otherwise **200**: OK — returned if no specific 2xx status code fits
  * On request error:
    * **400**: Bad Request
    * **404**: Not Found — no such resource
    * **405**: Method Not Allowed - http method not allowed on the resource
    * **406**: Not Acceptable — unsupported output formats (`Accept` header)
    * **409**: Conflict — the resource already exists
    * **415**: Unsupported Media Type — unsupported input formats (`Content-Type` header)
    * **[416](http://svn.tools.ietf.org/svn/wg/httpbis/specs/rfc7233.html#status.416)**: Range Not Satisfiable
    * **422**: Unprocessable Entity — request input syntax is correct but semantically invalid
    * **423**: Locked — the resource is in use and cannot be updated/deleted
  * On internal error:
    * **501**: Not Implemented
    * otherwise **500**: Internal Server Error

### I/O FORMAT

3 body formats are supported: `application/json`, `application/yaml` and `application/xml`.

On request:
  * the HTTP `Content-Type` header defines the request body format
  * The HTTP `Accept` header defines the expected response body format

### RESPONSE STRUCTURE

In JSON (equivalent in XML):
  * On success: `{"success": true, "result": <object>}`
  * On failure: `{"success": false, "exception": <string>}`

### SECURITY

**Urest** does not support any native authentication mechanism for the moment.

RFC 7233 §6.1 — Denial-of-Service Attacks Using Range

> Unconstrained multiple range requests are susceptible to denial-of-service
> attacks because the effort required to request many overlapping ranges of
> the same data is tiny compared to the time, memory, and bandwidth consumed
> by attempting to serve the requested data in many parts. Servers ought to
> ignore, coalesce, or reject egregious range requests, such as requests for
> more than two overlapping ranges or for many small ranges in a single set,
> particularly when the ranges are requested out of order for no apparent
> reason. Multipart range requests are not designed to support random access.

According to this **Urest** doesn't forbid to explicitly fetch all resources (`?range=0-`.)


References
----------

  * http://blog.octo.com/designer-une-api-rest/ (in French)
  * http://www.restapitutorial.com
  * https://bourgeois.me/rest/
