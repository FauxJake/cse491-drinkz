#! /usr/bin/env python
from wsgiref.simple_server import make_server
import urlparse, os
import json as simplejson
import db, recipes

dispatch = {
    '/' : 'index',
    '/recipes' : 'recipes',
    '/error' : 'error',
    '/inventory' : 'inventory',
    '/liquor_types' : 'types',
    '/form' : 'form',
    '/recv' : 'recv',
    '/rpc'  : 'dispatch_rpc'
}

html_headers = [('Content-type', 'text/html')]

class SimpleApp(object):
	def __call__(self, environ, start_response):
		path = environ['PATH_INFO']
		fn_name = dispatch.get(path, 'error')
		print os.path.realpath(__file__)

        # retrieve 'self.fn_name' where 'fn_name' is the
        # value in the 'dispatch' dictionary corresponding to
        # the 'path'.
		fn = getattr(self, fn_name, None)

		if fn is None:
			start_response("404 Not Found", html_headers)
			return ["No path %s found" % path]

		return fn(environ, start_response)
            
	def index(self, environ, start_response):
		data = head_html("index") + index() + javascript() + "</body></html>"
		start_response('200 OK', list(html_headers))
		return [data]

	def recipes(self,environ,start_response):
		data = recipes()
		start_response('200 OK', list(html_headers))
		return [data]

	def inventory(self, environ, start_response):
		basepath = os.path.dirname(__file__)
		filepath = os.path.abspath(os.path.join(basepath, "..","db.txt"))
		db.load_db(filepath)
		print db._inventory_db
		data = inventory()

		start_response('200 OK', list(html_headers))
		return [data]

	def types(self, environ, start_response):
		basepath = os.path.dirname(__file__)
		filepath = os.path.abspath(os.path.join(basepath, "..","db.txt"))
		db.load_db(filepath)
		data = liq_typs()

		start_response('200 OK', list(html_headers))
		return	data

	def error(self, environ, start_response):
		status = "404 Not Found"
		content_type = 'text/html'
		data = "Couldn't find your stuff."
       
		start_response('200 OK', list(html_headers))
		return [data]

	def form(self,environ,start_response):
		data = form()
		start_response('200 OK', list(html_headers))
		return [data]
   
	def recv(self, environ, start_response):
		formdata = environ['QUERY_STRING']
		results = urlparse.parse_qs(formdata)

		amount = results['amount'][0]

		content_type = 'text/html'
		data = "%s Converted to mL is: %s.  <a href='./'>return to index</a>" % (amount, db.convert_to_ml(str(amount)))

		start_response('200 OK', list(html_headers))
		return [data]

	def dispatch_rpc(self, environ, start_response):
        # POST requests deliver input data via a file-like handle,
        # with the size of the data specified by CONTENT_LENGTH;
        # see the WSGI PEP.
        
		if environ['REQUEST_METHOD'].endswith('POST'):
			body = None
			if environ.get('CONTENT_LENGTH'):
				length = int(environ['CONTENT_LENGTH'])
				body = environ['wsgi.input'].read(length)
				print body
				response = self._dispatch(body) + '\n'
				start_response('200 OK', [('Content-Type', 'application/json')])

				return [response]

        # default to a non JSON-RPC error.
		status = "404 Not Found"
		content_type = 'text/html'
		data = "Couldn't find your stuff."
       
		start_response('200 OK', list(html_headers))
		return [data]

	def _decode(self, json):
		return simplejson.loads(json)

	def _dispatch(self, json):
		rpc_request = self._decode(json)

		method = rpc_request['method']
		params = rpc_request['params']

		rpc_fn_name = 'rpc_' + method
		fn = getattr(self, rpc_fn_name)
		result = fn(*params)

		response = { 'result' : result, 'error' : None, 'id' : 1 }
		response = simplejson.dumps(response)
		return str(response)

	def rpc_convert_units_to_ml(self,amount):
		return str(db.convert_to_ml(amount))

	def rpc_get_recipe_names(self):
		basepath = os.path.dirname(__file__)
		filepath = os.path.abspath(os.path.join(basepath, "..","db.txt"))
		db.load_db(filepath)

		recipes = ""
		for r in db.get_all_recipes():
			recipes += r.Name
			recipes += "\n"

		return recipes

	def rpc_get_liquor_inventory(self):
		basepath = os.path.dirname(__file__)
		filepath = os.path.abspath(os.path.join(basepath, "..","db.txt"))
		db.load_db(filepath)

		inventory = ""
		for i in db._inventory_db:
			inventory += str(i)
			inventory += "\n"

		return inventory



#HTML Generation Functions and such
#----------------------------------
def index():
	return """\
	<body>
		<h1>Welcome to the Alcohol Thing website</h1>
		<a href="recipes">List of recipes</a>
		<a href="inventory">Current Inventory</a>
		<a href="liquor_types">Types of Liquor</a>
		<a href="form">Unit Converter</a>
		<button onclick="Alert()" value="showAlertBox">I'm an Alert Button!</button>
"""

def inventory():
	data = head_html("current inventory")
	data += """\
<h1>Current Inventory</h1>
<table class="table">
<thead>
	<tr>
		<th>MFG</th>
		<th>Type</th>
		<th>Amount</th>
	</tr>
</thead>
<tbody>
"""
	for key, val in db._inventory_db.items():
		data += "<tr><td>%s</td><td>%s</td><td>%s</td>" % (key[0],key[1],val)

	data += "</tbody></table></body></html>"
	return data

def recipes():
	data = head_html("my favorite recipez") + "<ol>" + "<h1>Recipes in Db</h1>"
	for r in db.get_all_recipes():
		data += "<li>%s</li>" % r.Name
	data += "</ol></body></html>"
	return data

def liq_typs():
	data = head_html("das liquidz") + "<ol>" + "<h1>Types of Liquor</h1>"
	print db._bottle_types_db
	for i in db.get_liquor_inventory():
		print i
		data += "<li>%s, %s</li>" % (i[0],i[1])
	data += "<ol></body></html>"
	return data

def form():
	return head_html("convert unitz") + """
	<h1>Enter amount to be Converted to mL</h1>
	<form action='recv'>
		<input type='text' name='amount' size'20'>
		<input class="btn" type='submit'>
	</form>
</body>
</html>
"""

def head_html(title):
	return """\
<html>
	<head>
		<title>%s</title>
		<style type='text/css'>
		h1 {color:#ff0000;}
		body {
		font-size: 14px;
		}
		</style>
	</head>""" % (str(title))

def javascript():
	return """\
	<script type="text/javascript">
		function Alert(){
			alert("Ello!");
		}
	</script>"""

if (__name__ == '__main__'):
	import random, socket
	port = random.randint(8000, 9999)
    
	app = SimpleApp()
    
	httpd = make_server('', port, app)
	print "Serving on port %d..." % port
	print "Try using a Web browser to go to http://%s:%d/" % \
          (socket.getfqdn(), port)
	httpd.serve_forever()

