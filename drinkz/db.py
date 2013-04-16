"""
Database functionality for drinkz information.
recipes implemented as a set in order to avoid duplicates
"""
from cPickle import dump, load
import os

# private singleton variables at module level

#keyed by tuples of (mfg, liquor) with the value in the dictionary being the total quantity.
_inventory_db = dict()
#'set' containing tuples of (mfg, liquor, typ)
_bottle_types_db = set() 
#'set' containing tuples of the form: ({name}, list((ingridient name, amount),(n,a), etc.))
_recipes = set()

def save_db(filename):
	try:
		print "in save:\nfileName: %s\n" % filename
		fp = open(filename, 'wb')
		tosave = (_bottle_types_db, _inventory_db)
		print "ToSave: ", tosave
		dump(tosave, fp)

		fp.close()
		print "done"
		return True
	except Exception, e:
		return False
	

def load_db(filename):
	try:
		basepath = os.path.dirname(__file__)
		filepath = os.path.abspath(os.path.join(basepath, "..",filename))
		global _bottle_types_db, _inventory_db
		fp = open(filename, 'rb')

		loaded = load(fp)
		(_bottle_types_db, _inventory_db) = loaded

		print "LOADED: ", loaded

		fp.close()
	except Exception, e:
		raise e
	

def _reset_db():
	"A method only to be used during testing -- toss the existing db info."
	global _bottle_types_db, _inventory_db, _recipes
	_bottle_types_db = set()
	_inventory_db = dict()
	_recipes = set()
	save_db('db.txt')

# exceptions in Python inherit from Exception and generally don't need to
# override any methods.
class LiquorMissing(Exception):
	pass

class DuplicateRecipeName(Exception):
	pass

def available_recipes():
	results = []
	for r in _recipes:
		if not r.need_ingredients():
			results.append(r)

	return results

def add_recipe(recipe):
	if not get_recipe(recipe):
		_recipes.add(recipe)
	else:
		err = "Recipe '%s', is already in db" % (recipe.Name)
		raise DuplicateRecipeName(err)
	

def get_all_recipes():
	for r in _recipes:
		yield r

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
		elif units == "liter" or units == "L":
			total += float(amount) * 1000.0
		return total


def add_bottle_type(mfg, liquor, typ):
	"Add the given bottle type into the drinkz database."
	try:
		_bottle_types_db.add((mfg, liquor, typ))
		print "added to database"
		print _bottle_types_db

		save_db('db.txt')
		"saved database"
		return True
	except Exception, e:
		print "exception" + e.message
		return False
	

def _check_bottle_type_exists(mfg, liquor):
	load_db('db.txt')
	print "DB: ",_inventory_db
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
	save_db('db.txt')

def check_inventory(mfg, liquor):
	for key in _inventory_db.keys():
		if mfg == key[0] and liquor == key[1]:
			return True
		
	return False

def check_inventory_for_type(typ):
	for key in _bottle_types_db:
		#print "in check_inventory_for_type, searching for: ", typ
		if key[2] == typ:
			#print "key found: ",key
			yield key

def get_liquor_amount(mfg, liquor):
	"Retrieve the total amount of any given liquor currently in inventory."
	total = 0

	for key in _inventory_db.keys():
		if key[0] == mfg and key[1] == liquor:
			total += _inventory_db[key]

	return total

def get_liquor_inventory():
	"Retrieve all liquor types in inventory, in tuple form: (mfg, liquor)."
	load_db('db.txt')
	for key in _inventory_db.keys():
		yield key
