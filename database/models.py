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
        d = self.__dict__.copy()
        d.pop('_sa_instance_state')
        return d


class Tracked(Base, WalCommon):
    __tablename__ = 'tracked'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    wishlist = Column(Boolean)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="products", lazy="joined")
    product = relationship("Product", back_populates="users", lazy="joined")
    #user = relationship("User", backref="product_tracked_items")
    #product = relationship("Product", backref="user_tracked_items")

    def to_dict(self):
        return {'tracked_since': str(self.created_at),
                'wishlist': self.wishlist,
                'product': self.product.to_dict()}


class User(Base, WalCommon):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(20), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    email = Column(String(80), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    products = relationship("Tracked", back_populates="user", lazy="joined")
    #products = relationship('Product', secondary='tracked_items')

    def to_dict(self):
        d = self.__dict__.copy()
        d.pop('_sa_instance_state')
        d['created_at'] = str(d['created_at'])
        if self.products:
            d['products'] = [product.to_dict() for product in self.products]
        return d

    def __repr__(self):
        return "<User(name={})>".format(self.username)


class Product(Base, WalCommon):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    upc = Column(String(200), nullable=False)
    name = Column(String(200), nullable=False)
    thumbnail_img = Column(String(2000))
    med_img = Column(String(2000))
    lg_img = Column(String(2000))
    short_descr = Column(String(10000))
    long_descr = Column(String(10000))
    msrp = Column(Float)
    add_to_cart_url = Column(String(2000))
    url = Column(String(2000))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    users = relationship("Tracked", back_populates="product", lazy="joined")
    prices = relationship("Price", back_populates="products", lazy="joined")
    #users = relationship("User", secondary="tracked_items")

    def to_dict(self):
        d = self.__dict__.copy()
        d.pop('_sa_instance_state')
        if d.get('users'):
            d.pop('users')
        d['created_at'] = str(self.created_at)
        d['prices'] = [price.to_dict() for price in self.prices]
        return d

    def __repr__(self):
        return "<Product(id={}, name={})>".format(self.id, self.name)


class Price(Base, WalCommon):
    __tablename__ = 'prices'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    price = Column(Float)
    stock = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    products = relationship("Product", back_populates="prices", lazy="joined")

    def to_dict(self):
        return {'price': self.price,
                'stock': self.stock,
                'created_at': str(self.created_at)}

    def __repr__(self):
        return "<Price(product_id={}, price={})>".format(self.product_id, self.price)
