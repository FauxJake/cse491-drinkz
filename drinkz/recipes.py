from . import db

class Recipe(object):
	def __init__(self,name,ingredients):
		self.Name = name.lower()
		self.Ingredients = ingredients
		Recipe.recipeCnt += 1

	def need_ingridients():
		pass