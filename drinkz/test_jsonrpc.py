"""
Test the app.py rpc functionality
"""

import sys
sys.path.insert(0, 'bin/') # allow _mypath to be loaded;
import os
import ast
import db
import recipes
import app
import urllib
import simplejson
from StringIO import StringIO

def initialize_db():
	db._reset_db()

	db.add_bottle_type('Johnnie Walker', 'black label', 'blended scotch')
	db.add_to_inventory('Johnnie Walker', 'black label', '500 ml')

	db.add_bottle_type('Three Olives', 'Vodka', 'flavored vodka')
	db.add_bottle_type('Uncle Herman\'s', 'moonshine', 'blended scotch')
	db.add_to_inventory('Uncle Herman\'s', 'moonshine', '5 liter')

	r = recipes.Recipe('scotch on the rocks', [('blended scotch','4 oz')])
	db.add_recipe(r)
	r = recipes.Recipe('vodka martini', [('unflavored vodka', '7 oz'),('vermouth', '1.5 oz')])
	db.add_recipe(r)
	r = recipes.Recipe('vomit inducing martini', [('orange juice',
											  '6 oz'),
											 ('vermouth',
											  '1.5 oz')])
	db.add_recipe(r)
	db._c.execute('INSERT INTO users (firstname,lastname,username,pass) VALUES ("test1_first","test1_last","test1_username","guest")')
	db.dump_db('db.txt')


def test_rpc_convert_oz_to_ml():
	
	initialize_db()
	myApp = app.SimpleApp()


	environ = {}
	environ['REQUEST_METHOD'] = 'POST'
	environ['PATH_INFO'] = '/rpc'
	

	d = dict(method='convert_units_to_ml', params=['40 oz'] ,id=1)
	encoded = simplejson.dumps(d)
	environ['wsgi.input'] = StringIO(encoded)
	environ['CONTENT_LENGTH'] = 1000
	
	def my_start_response(s, h, return_in=d):
		d['status'] = s
		d['headers'] = h
		
	results = myApp.__call__(environ,my_start_response)
	text = "".join(results)
	
	assert text.find("1182.94") != -1, text


def test_rpc_get_recipe_names():
	
	initialize_db()
	myApp = app.SimpleApp()


	environ = {}
	environ['REQUEST_METHOD'] = 'POST'
	environ['PATH_INFO'] = '/rpc'
	

	d = dict(method='get_recipe_names', params=[] ,id=1)
	encoded = simplejson.dumps(d)
	environ['wsgi.input'] = StringIO(encoded)
	environ['CONTENT_LENGTH'] = 1000
	
	def my_start_response(s, h, return_in=d):
		d['status'] = s
		d['headers'] = h
		
	results = myApp.__call__(environ,my_start_response)
	text = "".join(results)
	
	assert text.find("scotch on the rocks") != -1, text
	assert text.find("vodka martini") != -1, text
	assert text.find("vomit inducing martini") != -1, text

def test_rpc_get_liqour_inventory():
	
	initialize_db()
	myApp = app.SimpleApp()


	environ = {}
	environ['REQUEST_METHOD'] = 'POST'
	environ['PATH_INFO'] = '/rpc'
	

	d = dict(method='get_liquor_inventory', params=[] ,id=1)
	encoded = simplejson.dumps(d)
	environ['wsgi.input'] = StringIO(encoded)
	environ['CONTENT_LENGTH'] = 1000
	
	def my_start_response(s, h, return_in=d):
		d['status'] = s
		d['headers'] = h
		
	results = myApp.__call__(environ,my_start_response)
	text = "".join(results)
	
	assert text.find("Johnnie Walker") != -1, text
	assert text.find("Uncle Herman's") != -1, text

def test_get_users():
	initialize_db()
	myApp = app.SimpleApp()


	environ = {}
	environ['REQUEST_METHOD'] = 'POST'
	environ['PATH_INFO'] = '/rpc'
	

	d = dict(method='get_users', params=[] ,id=1)
	encoded = simplejson.dumps(d)
	environ['wsgi.input'] = StringIO(encoded)
	environ['CONTENT_LENGTH'] = 1000
	
	def my_start_response(s, h, return_in=d):
		d['status'] = s
		d['headers'] = h
		
	results = myApp.__call__(environ,my_start_response)
	text = "".join(results)
	
	assert text.find("test1_last") != -1, text
	assert text.find("guest") != -1, text


#------------------------------------------------------------------------------
# HW #5 TESTS
#------------------------------------------------------------------------------

def test_rpc_add_bottle_type():
	
	initialize_db()
	myApp = app.SimpleApp()


	environ = {}
	environ['REQUEST_METHOD'] = 'POST'
	environ['PATH_INFO'] = '/rpc'
	

	d = dict(method='add_bottle_type', params=["Burnett's","Strawberry Vodka", "Vodka"] ,id=1)
	encoded = simplejson.dumps(d)
	environ['wsgi.input'] = StringIO(encoded)
	environ['CONTENT_LENGTH'] = 1000
	
	def my_start_response(s, h, return_in=d):
		d['status'] = s
		d['headers'] = h
		
	results = myApp.__call__(environ,my_start_response)
	text = "".join(results)
	
	assert text.find("true") != -1, text

def test_rpc_add_to_inventory():
	
	initialize_db()
	myApp = app.SimpleApp()


	environ = {}
	environ['REQUEST_METHOD'] = 'POST'
	environ['PATH_INFO'] = '/rpc'
	

	d = dict(method='add_to_inventory', params=["Burnett's","Strawberry Vodka", "400 ml"] ,id=1)
	encoded = simplejson.dumps(d)
	environ['wsgi.input'] = StringIO(encoded)
	environ['CONTENT_LENGTH'] = 1000
	
	def my_start_response(s, h, return_in=d):
		d['status'] = s
		d['headers'] = h
		
	results = myApp.__call__(environ,my_start_response)
	text = "".join(results)
	
	assert text.find("false") != -1, text


def test_rpc_add_recipe():
	
	initialize_db()
	myApp = app.SimpleApp()


	environ = {}
	environ['REQUEST_METHOD'] = 'POST'
	environ['PATH_INFO'] = '/rpc'
	

	d = dict(method='add_recipe', params=dict(name="Screw Driver",
		ingredients=[("Orange Juice","8 oz"),("Vodka","1 oz")]),
		id=1)
	
	encoded = simplejson.dumps(d)
	environ['wsgi.input'] = StringIO(encoded)
	environ['CONTENT_LENGTH'] = 1000
	
	def my_start_response(s, h, return_in=d):
		d['status'] = s
		d['headers'] = h

	results = myApp.__call__(environ,my_start_response)

	assert "true" in results[0], results[0]


	