from flask import jsonify, request
from app import app
from app.restaurant_finder import find_restaurant
from app.models import Restaurant, Base
from create_db import engine
from sqlalchemy.orm import sessionmaker

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/restaurants/', methods=['GET', 'POST'])
def all_restaurants():

    if request.method == 'GET':
        restaurants = session.query(Restaurant).all()
        return jsonify([item.serialize for item in restaurants])

    if request.method == 'POST':
        location = request.args.get('l')
        meal = request.args.get('m')
        restaurant_data = find_restaurant(meal, location)

        if restaurant_data['name'] == 'No restaurants found.':
            return jsonify({"error": "No Restaurants Found for {} in {}".format(meal, location)})
        else:
            rest_query = session.query(Restaurant).filter_by(name=restaurant_data['name'])
            if rest_query.first():
                restaurant = rest_query.first()
                return jsonify({"error": "Restaurant {} already exists in the database.".format(restaurant.name)})
            else:
                restaurant = Restaurant(name=restaurant_data['name'],
                                        address=restaurant_data['address'].decode('utf-8'),
                                        image=restaurant_data['image'])
                session.add(restaurant)
                session.commit()
                return jsonify(restaurant=restaurant.serialize)


@app.route('/restaurants/<int:id>/', methods=['GET', 'PUT', 'DELETE'])
def restaurant(id):
    restaurant = session.query(Restaurant).filter_by(id=id).one()
    if request.method == 'GET':
        return jsonify(restaurant.serialize)

    if request.method == 'PUT':
        name = request.args.get('name')
        address = request.args.get('address')
        image = request.args.get('image')

        restaurant.update(name, address, image)
        session.commit()
        return jsonify({'Updated': restaurant.serialize})

    if request.method == 'DELETE':
        session.delete(restaurant)
        session.commit()
        return jsonify({'deleted': {'restaurant': restaurant.id}})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
