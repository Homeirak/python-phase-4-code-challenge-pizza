#!/usr/bin/env python3
# app.py
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants")
def get_restaurants():
    restaurants = Restaurant.query.all()
    return[r.to_dict(only=("address", "id", "name")) for r in restaurants], 200

@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)

    if restaurant:
        restaurant_data = restaurant.to_dict(only=("id", "name", "address"))

        restaurant_data["restaurant_pizzas"] = []
        for restaurant_pizza in restaurant.restaurant_pizzas:
            restaurant_pizza_data = restaurant_pizza.to_dict(only=("id", "price", "pizza_id", "restaurant_id"))
            restaurant_pizza_data["pizza"] = (
                restaurant_pizza.pizza.to_dict(only=("id", "name", "ingredients"))
                if restaurant_pizza.pizza else None
            )
            restaurant_data["restaurant_pizzas"].append(restaurant_pizza_data)

        return restaurant_data, 200
    else:
        return {"error": "Restaurant not found"}, 404

@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    # restaurant = Restaurant.query.get(id)
    restaurant = db.session.get(Restaurant, id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return {}, 204
    else:
        return {"error": "Restaurant not found"}, 404

@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return [p.to_dict(only=("id", "name", "ingredients")) for p in pizzas], 200

@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    if not (1 <= price <= 30):
        return {"errors": ["validation errors"]}, 400

    pizza = db.session.get(Pizza, pizza_id)
    restaurant = db.session.get(Restaurant, restaurant_id)

    if not pizza or not restaurant:
        return {"errors": ["Invalid pizza or restaurant"]}, 400

    restaurant_pizza = RestaurantPizza(
        price=price,
        pizza_id=pizza_id,
        restaurant_id=restaurant_id
    )
    db.session.add(restaurant_pizza)
    db.session.commit()

    restaurant_pizza_data = restaurant_pizza.to_dict(
        only=("id", "price", "pizza_id", "restaurant_id")
    )
    restaurant_pizza_data["pizza"] = pizza.to_dict(only=("id", "name", "ingredients"))
    restaurant_pizza_data["restaurant"] = restaurant.to_dict(only=("id", "name", "address"))

    return restaurant_pizza_data, 201

if __name__ == "__main__":
    app.run(port=5555, debug=True)
