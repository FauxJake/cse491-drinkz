"""
Database functionality for drinkz information.
"""

# private singleton variables at module level
_bottle_types_db = set()
_inventory_db = dict()

def _reset_db():
    "A method only to be used during testing -- toss the existing db info."
    global _bottle_types_db, _inventory_db
    _bottle_types_db = set()
    _inventory_db = dict()

# exceptions in Python inherit from Exception and generally don't need to
# override any methods.
class LiquorMissing(Exception):
    pass
def convert_to_ml(amount):
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
        return total


def add_bottle_type(mfg, liquor, typ):
    "Add the given bottle type into the drinkz database."
    _bottle_types_db.add((mfg, liquor, typ))

def _check_bottle_type_exists(mfg, liquor):
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

def check_inventory(mfg, liquor):
    for key in _inventory_db.keys():
        if mfg == key[0] and liquor == key[1]:
            return True
        
    return False

def get_liquor_amount(mfg, liquor):
    "Retrieve the total amount of any given liquor currently in inventory."
    total = 0

    for key in _inventory_db.keys():
        if key[0] == mfg and key[1] == liquor:
            total += _inventory_db[key]

    return total

def get_liquor_inventory():
    "Retrieve all liquor types in inventory, in tuple form: (mfg, liquor)."
    for key in _inventory_db.keys():
        yield key
