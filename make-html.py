import os
import drinkz.db, drinkz.recipes

basepath = os.path.dirname(__file__)
filepath = os.path.abspath(os.path.join(basepath, "bin","db.txt"))
print filepath
drinkz.db.load(filepath)

try:
    os.mkdir('html')
except OSError:
    # already exists
    pass


###

fp = open('html/index.html', 'w')
print >>fp, """
<p><a href='recipes.html'>Recipes</a>
<a href='inventory.html'>Inventory</a>
<a href='liquor_types.html'>Liquor Types</a>

"""

fp.close()

###

fp = open('html/recipes.html', 'w')

print >>fp, "<ol>"

for r in drinkz.db.get_all_recipes():
    print >>fp, "<li>",str(r.Name),"</li>"

print >>fp, "</ol>"

print >>fp, """
<p><a href='recipes.html'>Recipes</a>
<a href='inventory.html'>Inventory</a>
<a href='liquor_types.html'>Liquor Types</a>

"""
fp.close()

###

fp = open('html/inventory.html', 'w')

print >>fp, """
<table>
    <thead>
        <tr>
            <th>MFG</th>
            <th>Type</th>
            <th>Amount</th>
        </tr>
    </thead>
    <tbody>
"""
for key, val in drinkz.db._inventory_db.items():
    print >>fp, "<tr>\n"
    print >>fp, "<td>", key[0],"</td>"
    print >>fp, "<td>", key[1],"</td>"
    print >>fp, "<td>", val,"</td>"
    print >>fp, "</tr>"

print >>fp, """</tbody>
</table>"""

print >>fp, """
<p><a href='recipes.html'>Recipes</a>
<a href='inventory.html'>Inventory</a>
<a href='liquor_types.html'>Liquor Types</a>

"""
fp.close()

###

fp = open('html/liquor_types.html', 'w')

print >>fp, "<ol>"
for i in drinkz.db.get_liquor_inventory():
    print >>fp, "<li>",i,"</li>"
print >>fp, "</ol>"

print >>fp, """
<p><a href='recipes.html'>Recipes</a>
<a href='inventory.html'>Inventory</a>
<a href='liquor_types.html'>Liquor Types</a>

"""

fp.close()