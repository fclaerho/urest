REST
====

REST Framework for Python.
Built as a Bottle wrapper implementing REST design recommended practices.

How-to
------

  * Import the module
  * Implement the Model() base class for each of your resources
  * Instantiate an Api()
  * Register() each URL path againts a resource instance
  * Call server() on the API instance.

Example
-------

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

