Tiny REST Framework for Python,
built as a Bottle wrapper implementing REST design recommended practices.
Of course you'll need Bottle as dependency (it's a single-file module.)

**HTTP STATUS CODES**

  * 201: Successful creation
  * 204: Idem, empty response
  * 406: Unsupported output formats (Accept header)
  * 415: Unsupported input formats (Content-Type header)
  * 422: Invalid input
  * 409: Resource exists
  * 404: No such resource
  * 501: Not implemented

**HTTP CRUD**

  * Selection: GET /%resource%s?[&fields=][&limit=][&offset=][&name=]
  * Creation: POST /%resource%s and body contains the payload
  * Update: PUT /%resource%s and body contains the payload
  * Deletion: DELETE /%resource%s {"name": %string%}

**RESPONSE FORMAT**

  * On success: {"success": true, "result": …}
  * On failure: {"success": false, "exception": %string%}

**USAGE**

  - `import rest`
  - Implement the `Model()` base class for each of your resources
  - Instantiate an `Api()`
  - `Register()` each URL path againts a resource instance
  - Call `serve()` on the API instance.
  - Connect to your endpoint at localhost:8080 (default)

**EXAMPLE**

	import rest
	class About(rest.Model):
		def select(self, **kwargs):
			return {"msg": "hello world!"}
		def create(self, body):
			raise NotImplementedError("cannot create")
		def update(self, body):
			raise NotImplementedError("cannot update")
		def delete(self, body):
			raise NotImplementedError("cannot delete")
	api = Api()
	api.register("/about", About())
	api.serve()

