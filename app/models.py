from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer, String
from flask_login import UserMixin
from app import lm, Base
from create_db import engine
from sqlalchemy.orm import sessionmaker


DBSession = sessionmaker(bind=engine)
session = DBSession()


class User(UserMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    social_id = Column(String(64), nullable=True, unique=True)
    username = Column(String(64), nullable=False)
    email = Column(String(64), nullable=True)
    password = Column(String(150), nullable=True)


@lm.user_loader
def load_user(id):
    return session.query(User).get(int(id))


class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), unique=False)
    user = relationship(User)


class MenuItem(Base):
    __tablename__ = 'menu_item'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(300))
    price = Column(String(8))
    course = Column(String(250))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    user_id = Column(Integer, ForeignKey('users.id'), unique=False)
    restaurant = relationship(Restaurant)
    user = relationship(User)
