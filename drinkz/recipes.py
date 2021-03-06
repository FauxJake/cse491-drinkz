import db

class Recipe(object):
	recipeCnt = 0
	def __init__(self,name,ingredients):

		self.Name = name.lower()
		self.Ingredients = ingredients
		Recipe.recipeCnt += 1

	def display_count(self):
		print "Recipe Count: ", Recipe.recipeCnt

	def need_ingredients(self):
		print "SELF.IN: ",self.Ingredients
		missing = []
		stock = dict() #contains key: (mfg,liquor,typ) value: amount

		#First: fill a dict with our stock that matches the liquor type
		for i in self.Ingredients:
			for item in db.check_inventory_for_type(i[0]): #returns mfg/liquor tuples with liquor == {ingredient name}
				#fetches from the inventory the amount
				db._c.execute("SELECT amount FROM inventory WHERE \
					mfg = ? AND liquor = ?",(item[1],item[2]))
				amount = int(db._c.fetchone()[0])

				if item in stock.keys(): #add to temp dictionary
					stock[(item[2],item[3])] += float(amount)
				else:
					stock[(item[2],item[3])] = float(amount)


		if len(stock) == 0:
			#no ingredients of that type(s) in db
			for i in self.Ingredients:
				amount = db.convert_to_ml(i[1])
				missing.append((i[0],amount))
			return missing

		#next: check to see if we have bottles with enough liquor for each ingredient in the recipe (to refrain from mixing bottles)
		for i in self.Ingredients:			
			needed = db.convert_to_ml(i[1])
			#print "\nWe need %s ml of %s" % (needed, i[0])
			most = 0 #greatest amount per bottle, overwritable
			flag = False  #False implies not enough liquor in any given bottle to satisfy the ingredient amount
			for item, amt in stock.items():
				#print "looking for greatest amount: %s -- %s?" % (item, amt)
				print item[1], i[0]
				if str(item[1]) == str(i[0]):
					if amt >= needed:
						flag = True
						#print "	greater than needed!"
					if amt > most:
						most = stock[item]
						#print "	new greatest amount!"

			if flag == False:
				miss = i[0],(needed-most)
				missing.append(miss)


		if len(missing) != 0:
			return missing
		else:
			return False

				