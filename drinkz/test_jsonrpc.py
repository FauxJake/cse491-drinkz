import db, recipes, app
import json_rpc_client, socket
from wsgiref.simple_server import make_server
import random

def test_convert_rpc():
	#initialize the app and serve it
	port = random.randint(8000, 9999)

	app_obj = app.SimpleApp()
	httpd = make_server('', port, app)
	server_base = "http://%s:%d/" % (socket.getfqdn(), port)

	results = json_rpc_client.call_remote(server_base, method='convert_units_to_ml', params=["32 liter"], id=1)

	assert results == 32000.0, results

def test_recipe_rpc():
	#initialize the app and serve it
	port = random.randint(8000, 9999)

	app_obj = app.SimpleApp()
	httpd = make_server('', port, app)
	server_base = "http://%s:%d/" % (socket.getfqdn(), port)

	#add some test data
	db.add_bottle_type('Johnnie Walker', 'black label', 'blended scotch')
	db.add_to_inventory('Johnnie Walker', 'black label', '500 ml')

	db.add_bottle_type('Uncle Herman\'s', 'moonshine', 'blended scotch')
	db.add_to_inventory('Uncle Herman\'s', 'moonshine', '5 liter')
        
	db.add_bottle_type('Gray Goose', 'vodka', 'unflavored vodka')
	db.add_to_inventory('Gray Goose', 'vodka', '1 liter')

	db.add_bottle_type('Rossi', 'extra dry vermouth', 'vermouth')
	db.add_to_inventory('Rossi', 'extra dry vermouth', '24 oz')

	r = recipes.Recipe('scotch on the rocks', [('blended scotch',
                                                   '4 oz')])
	
	db.add_recipe(r)

	results = json_rpc_client.call_remote(server_base, method='get_recipe_names', params=[], id=1)

	text = "".join(results)

	assert text.find('scotch on the rocks') != -1, text

def test_inventory_rpc():
	#initialize the app and serve it
	port = random.randint(8000, 9999)

	app_obj = app.SimpleApp()
	httpd = make_server('', port, app)
	server_base = "http://%s:%d/" % (socket.getfqdn(), port)

	#add some test data
	db.add_bottle_type('Johnnie Walker', 'black label', 'blended scotch')
	db.add_to_inventory('Johnnie Walker', 'black label', '500 ml')

	db.add_bottle_type('Uncle Herman\'s', 'moonshine', 'blended scotch')
	db.add_to_inventory('Uncle Herman\'s', 'moonshine', '5 liter')

	results = json_rpc_client.call_remote(server_base, method='get_liquor_inventory', params=[], id=1)

	text = "".join(results)

	assert text.find("(Johnnie Walker,black label,blended scotch)") != -1, text
