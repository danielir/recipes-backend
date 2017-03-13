import json
import pprint
import pymongo
import smtp
from flask import Flask,Request,jsonify,Response,request,abort
from pymongo import MongoClient

def get_recipes():
    client = MongoClient('127.0.0.1', 27017)
    db = client.test
    recipes = list(db.recipes.find({}, {'_id':False}))
    return recipes

# return dictionary with all the recipes in complete_recipes.txt
def get_recipes_from_file():
    with open("complete_recipes.txt", "r") as json_data:
        d = json.load(json_data)
        #print(d[0]["ingredients"])
        return d

def main():
    recipes = get_recipes()
    print("These are our current recipes:")
    for i,recipe in enumerate(recipes,1):
        print(i, '-', recipe["name"])

    selected_recipes = []
    selected_recipes.append(recipes[0])
    selected_recipes.append(recipes[1])
    selected_recipes.append(recipes[2])
    selected_recipes.append(recipes[3])

    get_total_ingredients(selected_recipes)

    recipeIndex = int(input("What recipe do you want to cook?")) - 1
    print(recipes[recipeIndex])

# calculates total ingredients for a list of recipes
def get_total_ingredients(recipes):

    total_ingredients = {}
    variety_units = {}

    # iterate recipes adding ingredients
    for recipe in recipes:
        for ingredient in recipe["ingredients"]:
            #print(ingredient)
            item = ingredient.get("item")
            quantity = ingredient.get("quantity")
            unit = ingredient.get("unit")

            # ingredients with unit themselves do not have item key, use unit instead
            if item == None:
                item = unit

            # if it is first time this ingredient appears then add it
            if total_ingredients.get(item) == None:
                # add new ingredient dictionary
                total_ingredients[item] = {}
                total_ingredients[item]["quantity"] = quantity
                total_ingredients[item]["unit"] = unit
            else:
                # ingredient already exists, we have to add a quantity
                current_unit = total_ingredients[item]["unit"]
                current_quantity = total_ingredients[item]["quantity"]

                if current_unit == unit:
                    # if the units are equals then just add up quantities
                    total_ingredients[item]["quantity"] = current_quantity + quantity
                else:
                    #print("Different units " + unit + " and " + current_unit + " for ingredient", item)
                    # tactical solution
                    if total_ingredients[item]["unit"] != "variety":
                        total_ingredients[item]["unit"] = "variety"
                        variety_units[item] = {}
                        variety_units[item][unit] = quantity;
                        variety_units[item][current_unit] = current_quantity;
                    else:
                        variety_item = variety_units.get(item)
                        if variety_item.get(unit) == None:
                            variety_item[unit] = quantity
                        else:
                            variety_item[unit] = quantity + variety_item[unit]

                    #total_ingredients[item]["quantity"] = str(quantity) + ' ' + unit + ', ' + str(current_quantity) + ' ' + current_unit

    pp = pprint.PrettyPrinter(depth=6)
    print("TOTAL")
    pp.pprint(total_ingredients)
    print("variety units")
    pp.pprint(variety_units)

app = Flask(__name__)

@app.route("/mailsend", methods=['POST'])
def mail_send():
    print('mail_send called')
    msg = request.json['msg']
    print(msg)
    smtp.send_email('daniel.ivorra@gmail.com', 'Dani', msg)
    response_json = {'result':'ok'}
    resp = Response(json.dumps(response_json), mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    #if not request.json or not 'msg' in request.json:
     #   abort(400)
    return resp



@app.route("/")
def home():
    print('home called')
    recipes = list(get_recipes())
    num_recipes = len(recipes)
    #print(num_recipes)
    #print(recipes)

    recipes_json = json.dumps(recipes)
    resp = Response(recipes_json, mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    print('returning response')
    return resp

#main()
app.run(host="localhost")
#get_recipes()






