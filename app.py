#! /usr/bin/env python
from wsgiref.simple_server import make_server
import urlparse

class DrinkzApp(object):
	def __call__(self, environ, start_response):
		status = '200 OK'
		path = environ['PATH_INFO']

		if path == '/':
			content_type = 'text/html'
			data = """\
<h1>Welcome to the Alcohol website<h1>
<a href="html/recipes">List of recipes</a>
<a href="html/inventory">Current Inventory</a>
<a href="html/liquor_types">Types of Liquor</a>
"""

		headers = [('Content-type', content_type)]
		start_response(status, headers)

		return [data]

if __name__ == '__main__':
	import random, socket
	port = random.randint(8000, 9999)

	app = DrinkzApp

	httpd = make_server('', port, app)
	print "Serving on port %d..." % port
	print "Try using a Web browser to go to http://%s:%d/" % \
          (socket.getfqdn(), port)
	httpd.serve_forever()