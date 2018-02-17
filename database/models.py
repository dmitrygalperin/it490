from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()


class Tracked(Base):
    __tablename__ = 'tracked'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    wishlist = Column(Boolean)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="products")
    product = relationship("Product", back_populates="users")
    #user = relationship("User", backref="product_tracked_items")
    #product = relationship("Product", backref="user_tracked_items")


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(20), nullable=False)
    password = Column(String(100), nullable=False)
    email = Column(String(80), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    products = relationship("Tracked", back_populates="user")
    #products = relationship('Product', secondary='tracked_items')

    def to_dict(self):
        return {'id': self.id, 'username': self.username, 'email': self.email}

    def __repr__(self):
        return "<User(name={})>".format(self.username)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        getattr(self, key)
        return setattr(self, key, value)


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    upc = Column(Integer, nullable=False)
    name = Column(String(200), nullable=False)
    thumbnail_img = Column(String(200), nullable=False)
    med_img = Column(String(200), nullable=False)
    lg_img = Column(String(200), nullable=False)
    description = Column(String(500), nullable=False)
    msrp = Column(Float, nullable=False)
    rollback = Column(Boolean)
    add_to_cart_url = Column(String(200))
    url = Column(String(200))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    users = relationship("Tracked", back_populates="product")
    prices = relationship("Price", back_populates="products")
    #users = relationship("User", secondary="tracked_items")


class Price(Base):
    __tablename__ = 'prices'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    price = Column(Float)
    available = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    products = relationship("Product", back_populates="prices")
