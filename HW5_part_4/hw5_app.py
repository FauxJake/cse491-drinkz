#! /usr/bin/env python
from wsgiref.simple_server import make_server
import urlparse

dispatch = {
	'/' : "index",
	'/form' : "form",
	'/recv' : "recv",
	'/image' : "image"
}

html_headers = [("content-type", 'text/html')]

class SimpleApp(object):
	def __call__(self,environ,start_response):
		path = environ['PATH_INFO']
		fn_name = dispatch.get(path, 'error')

		function = getattr(self,fn_name,None)

		if function is None:
			start_response("404 Not Found", html_headers)
			return ["No path %s found" % path]

		return function(environ,start_response)

	def index(self,environ,start_response):
		start_response('200 OK', list(html_headers))

		return "THIS IS THE INDEX AND IT IS AWESOME"

	def form(self,environ,start_response):
		start_response('200 OK', list(html_headers))

		return """<form action='recv'>
Favorite Color? <input type='text' name='color'>
Favorite Cookie Flavor? <input type='text' name='cookie'>
<input type='submit'>
</form>"""

	def recv(self,environ,start_response):

		formdata = environ['QUERY_STRING']
		results = urlparse.parse_qs(formdata)

		color = results["color"][0]
		cookie = results["cookie"][0]
		status = ""

		start_response('200 OK', list(html_headers))

		if color.lower() == "pink":
			status = "...Pink is ugly"
		elif cookie.lower() == "chocolate chip":
			status = "...so mainstream, oatmeal raisin is where it's at"

		return "Favorite Color: %s, Favorite Cookie Flavor: %s %s" % (color,cookie,status)

	def image(self,environ,start_response):
		content_type = 'image/jpg'

		data = open('IMG_0171.jpg','rb').read()
		start_response('200 OK', [('content-type', content_type)])

		return [data]
	
if __name__ == '__main__':
	import random, socket
	port = 8888
	
	app = SimpleApp()
	
	httpd = make_server('', port, app)
	print "Serving on port %d..." % port
	print "Try using a Web browser to go to http://%s:%d/" % \
		  (socket.getfqdn(), port)
	httpd.serve_forever()