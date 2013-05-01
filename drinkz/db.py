"""
Database functionality for drinkz information.
recipes implemented as a set in order to avoid duplicates
"""
import sqlite3
from cPickle import dump, load, dumps, loads
import os
import recipes
import unicodedata

# database connection 

_db = sqlite3.connect('drinkzdata.db')

_c = _db.cursor()

#keyed by tuples of (mfg, liquor) with the value in the dictionary being the total quantity.
_inventory_db = dict()
#'set' containing tuples of (mfg, liquor, typ)
_bottle_types_db = set() 
#'set' containing tuples of the form: ({name}, list((ingridient name, amount),(n,a), etc.))
_recipes = set()

def dump_db(filename):
	try:
		fp = open(filename, 'wb')
		tosave = (_bottle_types_db, _inventory_db, _recipes)
		dump(tosave, fp)

		fp.close()
		return True
	except Exception, e:
		return False

def save_db():
	try:
		_db.commit()
	except Exception, e:
		raise e

def load_dumped_db(filename):
	try:
		basepath = os.path.dirname(__file__)
		filepath = os.path.abspath(os.path.join(basepath, "..",filename))
		global _bottle_types_db, _inventory_db, _recipes
		fp = open(filename, 'rb')

		loaded = load(fp)
		(_bottle_types_db, _inventory_db, _recipes) = loaded

		fp.close()
	except Exception, e:
		raise e

def _reset_db():
	"A method only to be used during testing -- toss the existing db info."
	global _bottle_types_db, _inventory_db, _recipes
	_bottle_types_db = set()
	_inventory_db = dict()
	_recipes = set()
	dump_db('db.txt')
	_c.execute("DELETE FROM recipes")
	_c.execute("DELETE FROM inventory")
	_c.execute("DELETE FROM bottle_types")
	_c.execute("DELETE FROM users")

# exceptions in Python inherit from Exception and generally don't need to
# override any methods.
class LiquorMissing(Exception):
	pass

class DuplicateRecipeName(Exception):
	pass

def check_username_and_pass(username,password):
	_c.execute("SELECT * FROM users WHERE username = ? AND pass = ?", (username,password))
	results = _c.fetchall()
	if len(results) != 0:
		return True

	return False

def available_recipes():
	results = []
	_c.execute("SELECT * FROM recipes")
	results = _c.fetchall()
	for r in results:
		norm = unicodedata.normalize('NFKD', r[2]).encode('ascii','ignore') #remove unicode encodings
		ing = loads(norm) #unpickle
		rec = recipes.Recipe(r[1],ing)
		if not rec.need_ingredients():
			results.append(r)
	return results

def add_recipe(recipe):
	if not get_recipe(recipe):
		_recipes.add(recipe)
		try:
			ing = dumps(recipe.Ingredients) # serialize ingredients as string
			_c.execute('INSERT INTO recipes (name, ingredients) VALUES (?, ?)', (recipe.Name,ing))
			save_db()
		except Exception, e:
			raise e
	else:
		err = "Recipe '%s', is already in db" % (recipe.Name)
		raise DuplicateRecipeName(err)
	

def get_all_recipes():
	_c.execute('SELECT * FROM recipes')
	results = _c.fetchall()
	for r in results:
		norm = unicodedata.normalize('NFKD', r[2]).encode('ascii','ignore') #remove unicode encodings
		ing = loads(norm) # load as a string
		rec = recipes.Recipe(r[1],ing) #create a recipe object
		yield rec

def get_recipe(name):
	if type(name) is str:
		for r in get_all_recipes():
			#print "r.Name: ", r.Name, "\nname: ", name
			if r.Name == name:
				return r
	#recipe type
	else:
		for r in get_all_recipes():
			#print "r.Name: ", r.Name, "\nname: ", name.Name
			if r.Name == name.Name:
				return r
	#print "NOTHING"
	return False


def convert_to_ml(amount):
	#print amount
	data = amount.split()
	amount = data[0]
	units = data[1].lower()

	if units == "ml":
		return float(amount)
	else:
		total = 0
		if units == "oz":
			total += float(amount) * 29.5735
		elif units == "g" or units == "gallon" or units == "gal":
			total += float(amount) * 3785.41
		elif units == "qt" or units == "quart":
			total += float(amount) * 946.353
		elif units == "pt" or units == "pint":
			total += float(amount) * 473.176
		elif units == "liter" or units == "l":
			total += float(amount) * 1000.0
		return total


def add_bottle_type(mfg, liquor, typ):
	"Add the given bottle type into the drinkz database."
	try:
		_bottle_types_db.add((mfg, liquor, typ))
		_c.execute("INSERT INTO bottle_types (mfg,liquor,type) VALUES (?,?,?)", (mfg,liquor,typ))
		return True

	except Exception, e:
		raise e
	
def _check_bottle_type_exists(mfg, liquor):
	#print "current inventory db: ", _inventory_db
	#print "searching for %s, %s" % (mfg,liquor)
	_c.execute("SELECT * FROM bottle_types WHERE mfg = ? AND liquor = ?", (mfg,liquor))
	for (m, l, _) in _bottle_types_db:
		if mfg == m and liquor == l:
			return True
	return False

def add_to_inventory(mfg, liquor, amount):
	"Add the given liquor/amount to inventory."
	if not _check_bottle_type_exists(mfg, liquor):
		err = "Missing liquor: manufacturer '%s', name '%s'" % (mfg, liquor)
		raise LiquorMissing(err)

	amount = convert_to_ml(amount)
	_inventory_db[(mfg,liquor)] = amount

	_c.execute("INSERT INTO inventory (mfg, liquor, amount) VALUES (?,?,?)",(str(mfg),str(liquor),float(amount)))
	save_db()

def check_inventory(mfg, liquor):

	#for key in _inventory_db.keys():
	#	if mfg == key[0] and liquor == key[1]:
	#		return True
	_c.execute("SELECT mfg,liquor,amount FROM inventory WHERE mfg = ? AND liquor = ?", (mfg,liquor))
	res = _c.fetchall()
	if len(res) != 0:
		return True	
	return False

def check_inventory_for_type(typ):
	_c.execute("SELECT * FROM bottle_types WHERE type = ?", [typ])
	results = _c.fetchall()

	for key in results:
		yield key

def get_liquor_amount(mfg, liquor):
	"Retrieve the total amount of any given liquor currently in inventory."
	total = 0

	for key in _inventory_db.keys():
		if key[0] == mfg and key[1] == liquor:
			total += _inventory_db[key]

	return total

def get_liquor_inventory():
	"Retrieve all liquor types in inventory, in tuple form: (mfg, liquor, amount)."
	_c.execute("SELECT mfg, liquor, amount FROM inventory")
	results = _c.fetchall()
	for i in results:
		yield (i[0],i[1],i[2])

def get_bottle_types():
	"Retrieve all liquor types in inventory, in tuple form: (mfg, liquor, amount)."
	_c.execute("SELECT mfg, liquor, type FROM bottle_types")
	results = _c.fetchall()
	for i in results:
		yield (i[0],i[1],i[2])