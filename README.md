Tiny REST Framework for Python,
built as a Bottle wrapper implementing REST design recommended practices:
  - HTTP verbs
  - Status code

**NOTE**
Of course you'll need bottle as dependency (it's a single-file module.)

— USAGE —

  - `import rest`
  - Implement the `Model()` base class for each of your resources
  - Instantiate an `Api()`
  - `Register()` each URL path againts a resource instance
  - Call `serve()` on the API instance.
  - Connect to your endpoint at localhost:8080 (default)

— EXAMPLE —

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

