from app import app
from app.models import Base, Restaurant, MenuItem, User
from create_db import engine

from flask import render_template, redirect, url_for, request, flash, jsonify, g
from flask import session as ls
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy.orm import sessionmaker
from app import forms
from app.forms import LoginForm, RegistrationForm
from app.oauth import FacebookOAuth, GoogleOAuth
from app.auth import log_in
from passlib.hash import sha256_crypt
import json
import random
import string

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.before_request
def before_request():
    g.user = current_user


@app.route('/authorize/facebook')
def oauth_facebook():
    if not current_user.is_anonymous:
        return redirect(url_for('homepage'))
    oauth = FacebookOAuth()
    return oauth.authorize()


@app.route('/callback/facebook')
def oauth_callback_facebook():
    if not current_user.is_anonymous:
        return redirect(url_for('homepage'))
    oauth = FacebookOAuth()
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication Failed.')
        return redirect(url_for('homepage'))
    user = session.query(User).filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, username=username, email=email)
        session.add(user)
        session.commit()
    login_user(user, True)
    return redirect(url_for('homepage'))


@app.route('/authorize/google')
def oauth_google():
    if not current_user.is_anonymous:
        return redirect(url_for('homepage'))
    oauth = GoogleOAuth()
    return oauth.authorize()


@app.route('/callback/google')
def oauth_callback_google():
    if not current_user.is_anonymous:
        return redirect(url_for('homepage'))
    oauth = GoogleOAuth()
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication Failed.')
        return redirect(url_for('homepage'))
    user = session.query(User).filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, username=username, email=email)
        session.add(user)
        session.commit()
    login_user(user, True)
    return redirect(url_for('homepage'))


@app.route('/login/', methods=['GET', 'POST'])
def login_page():
    if not current_user.is_anonymous:
        return redirect(url_for('homepage'))
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user_submit = request.form['email']
        password = request.form['password']
        user = session.query(User).filter_by(email=user_submit).first()
        return log_in(user, password)
    return render_template('login.html', form=form)


@app.route('/register/', methods=['GET', 'POST'])
def registration_page():
    if not current_user.is_anonymous:
        return redirect(url_for('homepage'))
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)

        user_data = session.query(User).filter_by(username=username).first()
        user_email = session.query(User).filter_by(email=email).first()

        if user_data is not None:
            flash('Username not available.')
            return redirect(url_for('registration_page', form=form))
        elif user_email is not None:
            flash('Email is already in use.')
            return redirect(url_for('registration_page', form=form))
        else:
            new_user = User(username=username, email=email, password=password)
            session.add(new_user)
            session.commit()

            login_user(new_user)
            flash('Registration Successful.')

            return redirect(url_for('homepage'))
    return render_template('register.html', form=form)


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))


@app.route('/restaurant/<int:rest_id>/menu/JSON')
def rest_menu_JSON(rest_id):
    menu_items = session.query(MenuItem).filter_by(restaurant_id=rest_id).all()
    menu_dict = dict()
    for item in menu_items:
        item_dict = {"description": item.description,
                    "course": item.course, "price": item.price}
        menu_dict[item.name] = item_dict

    return jsonify(Menu=menu_dict)


@app.route('/')
def homepage():
    return render_template("index.html")


@app.route('/restaurant/')
def list_restaurants():
    user = current_user
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants, user=user)


@app.route('/restaurant/new/', methods=['GET', 'POST'])
@login_required
def add_restaurant():
    user = current_user
    form = forms.NewRestaurant(request.form)
    if request.method == 'POST':
        new_restaurant = Restaurant(name=form.name.data, user_id=user.id)
        session.add(new_restaurant)
        session.commit()
        return redirect(url_for('list_restaurants'))

    return render_template('add_restaurant.html', form=form)


@app.route('/restaurant/<int:rest_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit_restaurant(rest_id):
    user = current_user
    restaurant = session.query(Restaurant).filter_by(id=rest_id).one()
    if user.id != restaurant.user_id:
        flash("You don't have permission to edit this information.")
        return redirect(url_for('list_restaurants'))
    form = forms.EditRestaurant(request.form)
    if request.method == 'POST' and 'new_name' in request.form:
        restaurant.name = form.new_name.data
        return redirect(url_for('list_restaurants'))

    return render_template('edit_restaurant.html', restaurant=restaurant, user=user, form=form)


@app.route('/restaurant/<int:rest_id>/delete/', methods=['GET', 'POST'])
@login_required
def del_restaurant(rest_id):
    user = current_user
    restaurant = session.query(Restaurant).filter_by(id=rest_id).one()
    menu = session.query(MenuItem).filter_by(restaurant_id=rest_id).all()
    if user.id != restaurant.user_id:
        flash("You don't have permission to edit this information.")
        return redirect(url_for('list_restaurants'))
    if request.method == 'POST':
        for item in menu:
            session.delete(item)
        session.delete(restaurant)
        session.commit()
        return redirect(url_for('list_restaurants', rest_id=rest_id))

    return render_template('delete_restaurant.html', restaurant=restaurant, user=user)


@app.route('/restaurant/<int:rest_id>/')
@app.route('/restaurant/<int:rest_id>/menu/')
def show_menu(rest_id):
    user = current_user
    restaurant = session.query(Restaurant).filter_by(id=rest_id).one()
    menu = session.query(MenuItem).filter_by(restaurant_id=rest_id).all()
    return render_template('menu.html', restaurant=restaurant, menu=menu, user=user)


@app.route('/restaurant/<int:rest_id>/menu/new/', methods=['GET', 'POST'])
@login_required
def new_menu_item(rest_id):
    user = current_user
    form = forms.NewMenuItem(request.form)
    restaurant = session.query(Restaurant).filter_by(id=rest_id).one()
    if user.id != restaurant.user_id:
        flash("You don't have permission to edit this information.")
        return redirect(url_for('show_menu', rest_id=restaurant.id))
    if request.method == 'POST':
        name = form.name.data
        description = form.description.data
        price = form.price.data
        course = form.course.data
        menu = MenuItem(name=name, description=description,
                     price=price, course=course, restaurant=restaurant, user=user)
        session.add(menu)
        session.commit()
        return redirect(url_for('show_menu', rest_id=rest_id))
    return render_template('new_menu.html', restaurant=restaurant, form=form)


@app.route('/restaurant/<int:rest_id>/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_menu_item(rest_id, menu_id):
    user = current_user
    form = forms.EditMenuItem(request.form)
    restaurant = session.query(Restaurant).filter_by(id=rest_id).one()
    menu = session.query(MenuItem).filter_by(id=menu_id).one()
    if user.id != restaurant.user_id:
        flash("You don't have permission to edit this information.")
        return redirect(url_for('show_menu', rest_id=restaurant.id))
    if request.method == 'POST':
        if form.new_name.data != '':
            menu.name = form.new_name.data
        if form.new_description.data != '':
            menu.description = form.new_description.data
        if form.new_price.data != '':
            menu.price = form.new_price.data
        if form.new_course.data != '':
            menu.course = form.new_course.data
        return redirect(url_for('show_menu', rest_id=rest_id))

    return render_template('edit_menu.html', restaurant=restaurant, menu=menu,
                            form=form, user=user)


@app.route('/restaurant/<int:rest_id>/menu/<int:menu_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_menu_item(rest_id, menu_id):
    user = current_user
    restaurant = session.query(Restaurant).filter_by(id=rest_id).one()
    menu = session.query(MenuItem).filter_by(id=menu_id).one()
    if user.id != restaurant.user_id:
        flash("You don't have permission to edit this information.")
        return redirect(url_for('show_menu', rest_id=restaurant.id))
    if request.method == 'POST':
        session.delete(menu)
        session.commit()
        return redirect(url_for('show_menu', rest_id=rest_id))

    return render_template('delete_menu.html', restaurant=restaurant,
                            menu=menu, user=user)


@app.route('/search/', methods=['GET', 'POST'])
def search():
    if request.method == "POST":

        search_data = request.form['search']
        if not search_data:
            data = 'No data entered.'
            return redirect(url_for('search', data=data))

        restaurants = []
        menus = []

        search_rests = session.query(Restaurant).all()
        for entry in search_rests:
            if entry.name.lower().startswith(search_data):
                restaurants.append(entry)

        search_menu = session.query(MenuItem).all()
        for entry in search_menu:
            if entry.name.startswith(search_data):
                rest_name = session.query(Restaurant).filter_by(id=entry.restaurant_id).one()
                menus.append((entry, rest_name))

        if restaurants == []:
            rests_data = 'No restaurants found.'
        else:
            rests_data = restaurants
        if menus == []:
            menu_data = 'No menu entries found.'
        else:
            menu_data = menus

        return render_template('search.html', rests_data=rests_data,
                                menu_data=menu_data)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html")
