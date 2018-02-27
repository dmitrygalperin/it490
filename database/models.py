import sys
sys.path.insert(0, "../lib")
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.collections import InstrumentedList
import datetime
from common import is_sa_mapped

Base = declarative_base()

class WalCommon():
    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        getattr(self, key)
        return setattr(self, key, value)

    def to_dict(self):
        d = self.__dict__
        d.pop('_sa_instance_state')
        return d


class Tracked(Base, WalCommon):
    __tablename__ = 'tracked'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    wishlist = Column(Boolean)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="products")
    product = relationship("Product", back_populates="users")
    #user = relationship("User", backref="product_tracked_items")
    #product = relationship("Product", backref="user_tracked_items")

    def to_dict(self):
        return {'tracked_since': self.created_at,
                'wishlist': self.wishlist,
                'product': self.product.to_dict()}


class User(Base, WalCommon):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(20), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    email = Column(String(80), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    products = relationship("Tracked", back_populates="user")
    #products = relationship('Product', secondary='tracked_items')

    def to_dict(self):
        d = self.__dict__
        d.pop('_sa_instance_state')
        products = d.get('products')
        if products:
            d['products'] = [product.to_dict() for product in products]
        return d

    def __repr__(self):
        return "<User(name={})>".format(self.username)


class Product(Base, WalCommon):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    upc = Column(Integer, nullable=False)
    name = Column(String(200), nullable=False)
    thumbnail_img = Column(String(200))
    med_img = Column(String(200))
    lg_img = Column(String(200))
    short_descr = Column(String(500))
    long_descr = Column(String(500))
    msrp = Column(Float)
    add_to_cart_url = Column(String(200))
    url = Column(String(200))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    users = relationship("Tracked", back_populates="product")
    prices = relationship("Price", back_populates="products")
    #users = relationship("User", secondary="tracked_items")

    def to_dict(self):
        d = self.__dict__
        d.pop('_sa_instance_state')
        d.pop('users')
        prices = d.get('prices')
        if prices:
            d['prices'] = [price.to_dict() for price in prices]
        return d

    def __repr__(self):
        return "<Product(id={}, name={})>".format(self.id, self.name)


class Price(Base, WalCommon):
    __tablename__ = 'prices'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    price = Column(Float)
    available = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    products = relationship("Product", back_populates="prices")

    def to_dict(self):
        return {'price': self.price,
                'available': self.available,
                'created_at': self.created_at}

    def __repr__(self):
        return "<Price(product_id={}, price={})>".format(self.product_id, self.price)
