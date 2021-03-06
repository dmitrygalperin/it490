import sys
sys.path.insert(0, "/home/produ/it490/lib")
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
    user = relationship("User", back_populates="products", lazy="subquery")
    product = relationship("Product", back_populates="users", lazy="subquery")
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

    products = relationship("Tracked", back_populates="user", lazy="subquery")
    #products = relationship('Product', secondary='tracked_items')

    def to_dict(self):
        d = self.__dict__.copy()
        d.pop('_sa_instance_state')
        if d.get('created_at'):
            d.pop('created_at')
        d['created_at'] = str(self.created_at)
        if self.products:
            d['products'] = [product.to_dict() for product in self.products]
        return d

    def __repr__(self):
        return "<User(name={})>".format(self.username)


class Product(Base, WalCommon):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    upc = Column(String(200))
    name = Column(String(200), nullable=False)
    thumbnail_img = Column(String(1000))
    med_img = Column(String(1000))
    lg_img = Column(String(1000))
    short_descr = Column(String(5000))
    long_descr = Column(String(5000))
    msrp = Column(Float)
    add_to_cart_url = Column(String(1000))
    url = Column(String(1000))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    users = relationship("Tracked", back_populates="product", lazy="subquery")
    prices = relationship("Price", back_populates="products", lazy="subquery", order_by="Price.created_at")
    #users = relationship("User", secondary="tracked_items")

    def to_dict(self):
        d = self.__dict__.copy()
        d.pop('_sa_instance_state')
        if d.get('created_at'):
            d.pop('created_at')
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

    products = relationship("Product", back_populates="prices", lazy="subquery")

    def to_dict(self):
        return {'price': self.price,
                'stock': self.stock,
                'created_at': str(self.created_at)
                }
    def __repr__(self):
        return "<Price(product_id={}, price={})>".format(self.product_id, self.price)

class Category(Base, WalCommon):
    __tablename__ = 'categories'
    id = Column(String(40), primary_key=True)
    name = Column(String(200))
    pages_parsed = Column(Integer)

    def __repr__(self):
        return '<Category(id={}, name={})>'.format(self.id, self.name)
