import sys
sys.path.insert(0, "../lib")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Database
from models import User, Product, Tracked, Price
import logging

logging.basicConfig(filename='/var/log/it490/dbcon.log',level=logging.INFO, format='%(asctime)s %(message)s')

USERNAME = Database.username
PASSWORD = Database.password
HOST     = Database.host
DB_TYPE  = Database.db_type
DB_NAME  = Database.db_name

#Register SQLAlchemy resources here
RESOURCES = {
    'user': User,
    'product': Product,
    'price': Price,
    'tracked': Tracked
}


class Dbcon(object):

    '''Static class that creates SQLAlchemy engine and session'''

    logger = logging.getLogger('dbcon')
    logger.addHandler(logging.StreamHandler())

    @classmethod
    def get_engine(cls, host=HOST):
        try:
            cls.logger.info('Connecting to database at {}://{}:****@{}/{}'.format(DB_TYPE, USERNAME, PASSWORD, host, DB_NAME))
            engine = create_engine('{}+pymysql://{}:{}@{}/{}'.format(DB_TYPE, USERNAME, PASSWORD, host, DB_NAME))
            engine.connect()
            cls.logger.info('Database connection successful')
            return engine
        except: #TODO: Catch specific errors
            cls.logger.critical(sys.exc_info())
            return

    @classmethod
    def get_session(cls):
        engine = cls.get_engine()
        if engine:
            Session = sessionmaker(bind=engine)
            return Session()
        else:
            return

    @classmethod
    def get_resource(cls, resource_name):
        return RESOURCES.get(resource_name)
