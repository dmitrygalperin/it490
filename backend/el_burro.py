'''
El Burro is a daemon process that constantly updates the prices of all products
in the database.
'''
import	sys
sys.path.insert(0, "../lib")
sys.path.insert(0, "../database")
from models import User, Product, Price, Tracked
from walcart import Walcart
import logging
import time
from rpc_pub import RpcPub
from common import serialize, unserialize

from config import Database

logging.basicConfig(filename='/var/log/it490/backend/el_burro.log',level=logging.INFO, format='%(asctime)s %(message)s')

class ElBurro(object):
    def __init__(self):
        self.delay = 1 #delay (s) between API requests
        self.pub = RpcPub(Database.queue)
        self.logger = logging.getLogger('elburro')
        self.logger.addHandler(logging.StreamHandler())
        self.running = True

    def start_updating(self):
        while self.running:
            self.update_prices()

    def update_prices(self):
        res = self.pub.call({'method': 'get', 'resource': 'product', 'where': {}})
        try:
            products = unserialize(res['result'])
        except Exception as e:
            self.logger.critical(str(e))
        for product in products:
            time.sleep(self.delay)
            self.logger.info('Updating price for {}'.format(product.name))
            product_data = Walcart.product(product.id)
            current_price = product_data.get('salePrice')
            stock = product_data.get('stock')
            old_price = None if not product.prices else product.prices[-1].price
            self.logger.info('\tOld Price: {}\tCurrent Price: {}'.format(old_price, current_price))
            if old_price != current_price:
                product.prices.append(Price(price=current_price, stock=stock))
            else:
                self.logger.info('\t\tPrice has not changed. No update necessary.')
                continue
            res = self.pub.call({'method': 'save', 'resource': serialize(product)})
            if not res.get('success'):
                self.logger.critical(res['message'])
            self.logger.info('\t\tPrice has been updated successfully.')

if __name__ == '__main__':
    running = True
    burro = ElBurro()
    burro.start_updating()
