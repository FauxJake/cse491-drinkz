import db, recipes, app

def test_recipes():
	#just in case of freak accidents
	db._reset_db()

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

	#initialize the app
	environ = {}
	environ['PATH_INFO'] = '/recipes'

	d = {}
	def my_start_response(s, h, return_in=d):
		d['status'] = s
		d['headers'] = h

	app_obj = app.SimpleApp()
	results = app_obj(environ, my_start_response)

	text = "".join(results)
	status, headers = d['status'], d['headers']
    
	assert text.find('scotch on the rocks') != -1, text
	assert ('Content-type', 'text/html') in headers
	assert status == '200 OK'

def test_index():
   	environ = {}
	environ['PATH_INFO'] = '/'
    
	d = {}
	def my_start_response(s, h, return_in=d):
		d['status'] = s
		d['headers'] = h

	app_obj = app.SimpleApp()
	results = app_obj(environ, my_start_response)

	text = "".join(results)
	status, headers = d['status'], d['headers']
    
	assert text.find('Welcome to the Alcohol Thing website') != -1, text
	assert ('Content-type', 'text/html') in headers
	assert status == '200 OK'