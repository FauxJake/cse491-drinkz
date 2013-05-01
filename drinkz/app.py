#! /usr/bin/env python
from wsgiref.simple_server import make_server
import urlparse, os
import json as simplejson
import db, recipes

import sys
try:
	sys.path.insert(0, '/Library/Python/2.6/site-packages/Jinja2-2.6-py2.6.egg')
except Exception, e:
	pass
import jinja2

dispatch = {
	'/' : 'index',
	'/recipes_list' : 'recipes_list',
	'/error' : 'error',
	'/inventory' : 'inventory',
	'/liquor_types' : 'types',
	'/convert' : 'convert',
	'/enter_liq_types' : 'add_liq_typ',
	'/recv_addliqtyp' : 'recv_addliqtyp',
	'/enter_liq_inventory' : 'add_liq_inventory',
	'/recv_addliqinv' : 'recv_addliqinv',
	'/add_recipe' : 'add_recipe',
	'/recv_addrecipe' : 'recv_addrecipe',
	'/recv_convert' : 'recv_convert',
	'/rpc'  : 'dispatch_rpc'
}

html_headers = [('Content-type', 'text/html')]

class SimpleApp(object):
	def __call__(self, environ, start_response):
		path = environ['PATH_INFO']
		fn_name = dispatch.get(path, 'error')
		# retrieve 'self.fn_name' where 'fn_name' is the
		# value in the 'dispatch' dictionary corresponding to
		# the 'path'.
		fn = getattr(self, fn_name, None)

		if fn is None:
			start_response("404 Not Found", html_headers)
			return ["No path %s found" % path]

		return fn(environ, start_response)
			
	def index(self, environ, start_response):
		data = index()
		start_response('200 OK', list(html_headers))
		return [data]

	def recipes_list(self,environ,start_response):
		data = recipes_list()
		start_response('200 OK', list(html_headers))
		return [data]

	def inventory(self, environ, start_response):
		#db.load_dumped_db('db.txt')
		#print db._inventory_db
		data = inventory()

		start_response('200 OK', list(html_headers))
		return [data]

	def types(self, environ, start_response):
		db.load_dumped_db('db.txt')
		data = liq_typs()

		start_response('200 OK', list(html_headers))
		return	data

	def error(self, environ, start_response):
		status = "404 Not Found"
		content_type = 'text/html'
		data = "Couldn't find your stuff."
	   
		start_response('200 OK', list(html_headers))
		return [data]

	def convert(self,environ,start_response):
		data = convert()
		start_response('200 OK', list(html_headers))
		return [data]
   
	def recv_convert(self, environ, start_response):
		formdata = environ['QUERY_STRING']
		results = urlparse.parse_qs(formdata)

		amount = results['amount'][0]

		content = "%s Converted to mL is: %s.  <br/><a href='/'>Return to Index</a>\
		<a href='/convert'>Convert Another</a>"\
		 % (amount, db.convert_to_ml(str(amount)))

		vars = dict(content = content, title='Conversion Results')

		data = JinjaLoader('blank.html',vars)

		start_response('200 OK', list(html_headers))
		return data

	def add_liq_typ(self,environ,start_response):
		data = add_liq_typ()
		start_response('200 OK', list(html_headers))
		return data

	def recv_addliqtyp(self,environ,start_response):
		formdata = environ['QUERY_STRING']
		results = urlparse.parse_qs(formdata)

		mfg = results['mfg'][0]
		liquor = results['liquor'][0]
		typ = results['typ'][0]

		#print "FOMRDATA - mfg: %s Liq: %s Type: %s" % (mfg,liquor,typ)

		try:
			db.add_bottle_type(mfg,liquor,typ)

			vars = dict(title='Alll Right! Moar Booze!',
				content="Added %s, %s, %s to bottle type inventory" % (mfg, liquor, typ))

			data = JinjaLoader('blank.html',vars)
			
			start_response('200 OK',html_headers)
			return data

		except Exception, e:
			error_message = "An error occured adding %s, %s, %s to bottle type inventory" % (mfg, liquor, typ)
			data = error(error_message  + "<br/>" + e.message)

			start_response('500 INTERNAL SERVER ERROR', list(html_headers))
			return data

	def add_liq_inventory(self,environ,start_response):
		data = add_inv()
		start_response('200 OK', list(html_headers))
		return data

	def recv_addliqinv(self,environ,start_response):
		formdata = environ['QUERY_STRING']
		results = urlparse.parse_qs(formdata)

		mfg = results['mfg'][0]
		liquor = results['liq'][0]
		amount = results['amount'][0]

		try:
			db.add_to_inventory(mfg,liquor,amount)

			vars = dict(title='Alll Right! Moar Booze!',
				content="Added %s, %s, %s to liquor inventory" % (mfg, liquor, amount))

			data = JinjaLoader('blank.html',vars)
			
			start_response('200 OK', list(html_headers))
			return data
		except Exception, e:
			error_message = "An error occured adding %s, %s, %s to the inventory" % (mfg, liquor, amount)
			data = error(error_message + "<br/>" + e.message)
			
			start_response('500 INTERNAL SERVER ERROR', list(html_headers))
			return data

	def add_recipe(self,environ,start_response):
		data = add_recipe()

		start_response('200 OK', list(html_headers))
		return data

	def recv_addrecipe(self,environ,start_response):
		formdata = environ['QUERY_STRING']
		results = urlparse.parse_qs(formdata)

		try:
			name = results["name"][0]
			ingredients = []

			print results
			del results["name"]

			if not is_empty(results):
				for key,val in results.items():
					print val
					if not is_empty(val):
						parts = val[0].split(',')
						ingredients.append((parts[0],parts[1]))

			print name
			print ingredients
			r = recipes.Recipe(name,ingredients)
			db.add_recipe(r)
			print "there"
			

			vars = dict(title='Cool Recipe Dude!',
				content="Added: \n<strong>Name: </strong>%s\n<strong>Ingredients: </strong>%s"\
				 % (name,ingredients))

			data = JinjaLoader('blank.html',vars)

			start_response('200 OK', list(html_headers))
			return data

		except Exception, e:
			raise e


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

		print "PARAMS: ", params

		rpc_fn_name = 'rpc_' + method
		fn = getattr(self, rpc_fn_name)
		if type(params) == dict:
			flatten_unicode_keys(params)
			result = fn(**params)
		else:
			result = fn(*params)

		response = { 'result' : result, 'error' : None, 'id' : 1 }
		response = simplejson.dumps(response)
		return str(response)

	def rpc_convert_units_to_ml(self,amount):
		return str(db.convert_to_ml(amount))

	def rpc_get_recipe_names(self):
		basepath = os.path.dirname(__file__)
		filepath = os.path.abspath(os.path.join(basepath, "..","db.txt"))
		db.load_dumped_db(filepath)

		recipes = ""
		for r in db.get_all_recipes():
			recipes += r.Name
			recipes += "\n"

		return recipes

	def rpc_get_liquor_inventory(self):
		basepath = os.path.dirname(__file__)
		filepath = os.path.abspath(os.path.join(basepath, "..","db.txt"))
		db.load_dumped_db(filepath)

		inventory = ""
		for i in db._inventory_db:
			inventory += str(i)
			inventory += "\n"

		return inventory

	def rpc_add_recipe(self,**params):
		name = params["name"]
		ingredients = params["ingredients"]
		
		if len(name) > 0 and len(ingredients) > 0:
			try:
				r = recipes.Recipe(name,ingredients)

				db.add_recipe(r)
				return True
			except Exception, e:
				return e.message
		return False

	def rpc_add_bottle_type(self,*params):
		try:
			db.add_bottle_type(params[0],params[1],params[2])
			return True
		except Exception, e:
			return False

	def rpc_add_to_inventory(self,*params):
		try:
			db.add_to_inventory(params[0],params[1],params[2])
			return True
		except Exception, e:
			return False



#HTML Generation Functions and such
#----------------------------------
def JinjaLoader(filename,vars):
	# this sets up jinja2 to load templates from the 'templates' directory
	basepath = os.path.dirname(__file__)
	filepath = os.path.abspath(os.path.join(basepath,'JinjaTemplates'))
	#print filepath

	loader = jinja2.FileSystemLoader(filepath)
	#print loader.list_templates()

	env = jinja2.Environment(loader=loader)
	# pick up a filename to render
	
	template = env.get_template(filename)

	x = template.render(vars).encode('ascii','ignore')
	return x


def index():
	# variables for the template rendering engine
	vars = dict(title = 'Home')
	filename = 'index_page.html'

	return JinjaLoader(filename,vars)
	

def liq_typs():
	tcontent = []
	for i in db.get_bottle_types():
		tcontent.append(i)

	vars = dict(title = 'Bottle Types', theaders=["MFG","Liquor","Type"],tcontent = tcontent)

	return JinjaLoader('bottle_type_pages.html', vars)	

def inventory():
	tcontent = []
	for i in db.get_liquor_inventory():
		tup = (i[0], i[1], i[2])
		tcontent.append(tup)

	vars = dict(title = 'Liquor Inventory', theaders=["MFG","Liquor","Amount (mL)"],tcontent = tcontent)

	return JinjaLoader('bottle_type_pages.html', vars)

def recipes_list():
	tcontent = []
	for r in db.get_all_recipes():
		tup = (r.Name,r.Ingredients,r.need_ingredients())
		tcontent.append(tup)

	vars = dict(title = 'Recipe Inventory', theaders=["Recipe Name","Ingredients","Missing Ingredients"],tcontent = tcontent)

	return JinjaLoader('bottle_type_pages.html', vars)

def convert():
	vars = dict(title= 'Convert Unitz to mL', 
		btnText = 'Convert Mah!', 
		formItems = ["Amount"], 
		action = 'recv_convert', 
		formTitle = 'Enter an Amount to Convert',
		isAjaxCall = "True")

	return JinjaLoader('form_pages.html',vars)

def add_liq_typ():
	vars = dict(title= 'Add a Bottle Type', 
		btnText = 'Add Mah!', 
		formItems = ["mfg","liquor","typ"], 
		action = 'recv_addliqtyp', 
		formTitle = 'Enter Bottle Information')

	return JinjaLoader('form_pages.html',vars)

def add_inv():
	vars = dict(title="Add Some Booze",
		btnText='Add Mah!',
		formItems=["mfg","liq","amount"],
		action='recv_addliqinv',
		formTitle='Feed Me Liquor!')

	return JinjaLoader('form_pages.html',vars)

def add_recipe():
	vars = dict(title="Gimme a Good Recipe",
		btnText='Add Mah!',
		formItems=["Name",
			"Primary",
			"Secondary",
			"Tertiary",
			"Quaternary"],
		action='recv_addrecipe',
		formTitle='Recipe Details, Add a Name and up to 4 Ingredients ({name}, {amount} form please)')

	return JinjaLoader('form_pages.html',vars)

def error(content):
	vars = dict(title="you done messed up",
		content= "<p class='alert alert-danger'><strong>" + content + "</strong></p>")

	return JinjaLoader('blank.html',vars)


#-----HELPERS------
def is_empty(item):
	return True if len(item)==0 else False

def flatten_unicode_keys(d):
	for k in d:
		if isinstance(k, unicode):
			v = d[k]
			del d[k]
			d[str(k)] = v

if (__name__ == '__main__'):
	import random, socket
	port = random.randint(8000, 9999)
	
	app = SimpleApp()
	
	httpd = make_server('', port, app)
	print "Serving on port %d..." % port
	print "Try using a Web browser to go to http://%s:%d/" % \
		  (socket.getfqdn(), port)
	httpd.serve_forever()

