from . import db

class Recipe(object):
	recipeCnt = 0
	def __init__(self,name,ingredients):

		self.Name = name.lower()
		self.Ingredients = ingredients
		Recipe.recipeCnt += 1

	def display_count(self):
		print "Recipe Count: ", Recipe.recipeCnt

	def need_ingredients(self):
		missing = []
		mfg_and_amounts = dict() #contains key: (mfg,liquor) value: amount

		#First: fill a dict with our stock that matches the liquor type
		for i in self.Ingredients:
			for item in db.check_inventory_for_type(i[0]): #returns mfg/liquor tuples with liquor == {ingredient name}
				mfg = item[0]
				liquor = item[1]
				amount = db._inventory_db[item] #fetches from the inventory the amount

				if mfg in mfg_and_amounts.keys(): #add to temp dictionary
					mfg_and_amounts[mfg] += float(amount)
					print "here\n"
				else:
					mfg_and_amounts[mfg] = float(amount)
					print "there\n"


		if len(mfg_and_amounts) == 0:
			#no liquor of that type in db
			for i in self.Ingredients:
				amount = db.convert_to_ml(i[1])
				missing.append((i[0],amount))
			return missing


		#next: check to see if we have bottles with enough liquor for each ingredient in the recipe (to refrain from mixing bottles)
		for i in self.Ingredients:
			needed = db.convert_to_ml(i[1])
			most = 0 #greatest amount per bottle, overwritable
			flag = False  #False implies not enough liquor in any given bottle to satisfy the ingredient amount
			for item in mfg_and_amounts.keys():
				if mfg_and_amounts[item] >= needed:
					flag = True
				if mfg_and_amounts[item] > most:
					most = mfg_and_amounts[item]

			if flag == False:
				miss = i[0],(needed-most)
				missing.append(miss)


		if len(missing) != 0:
			return missing
		else:
			return False
