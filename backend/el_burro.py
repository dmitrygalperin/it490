'''
El Burro is a daemon process that constantly updates the prices of all products
in the database.
'''
import	sys
sys.path.insert(0, "/home/produ/it490/lib")
sys.path.insert(0, "/home/produ/it490/database")
from models import User, Product, Price, Tracked, Category
from walcart import Walcart
import logging
import time
from rpc_pub import RpcPub
from common import serialize, unserialize

from config import Database

logging.basicConfig(filename='/var/log/it490/backend/el_burro.log',level=logging.INFO, format='%(asctime)s %(message)s')

class ElBurro(object):
    def __init__(self):
        self.threads = 0
        self.delay = 40 #delay (s) between API requests
        self.pub = RpcPub(Database.queue)
        self.logger = logging.getLogger('elburro')
        self.logger.addHandler(logging.StreamHandler())
        self.running = True

    def start(self, method_to_start):
        self.threads += 1
        time.sleep(self.threads * (self.delay//2))
        while self.running:
            method_to_start()

    @staticmethod
    def make_product(product_data):
        product = Product(
            id = product_data.get('itemId'),
            upc = product_data.get('upc'),
            name = product_data.get('name'),
            thumbnail_img = product_data.get('thumbnailImage'),
            med_img = product_data.get('mediumImage'),
            lg_img = product_data.get('largeImage'),
            short_descr = product_data.get('shortDescription'),
            long_descr = product_data.get('longDescription'),
            msrp = product_data.get('msrp'),
            add_to_cart_url = product_data.get('addToCartUrl'),
            url = product_data.get('productUrl'),
        )
        price = product_data.get('salePrice')
        if price:
            product.prices.append(Price(price=price, stock=product_data.get('stock')))
        return product

    def paginated(self):
        self.logger.info('[PAGINATED] Beginning paginated products traversal...')
        res = self.pub.call({'method': 'get', 'resource': 'category', 'where': {}})
        try:
            categories = unserialize(res['result'])
        except Exception as e:
            self.logger.critical(str(e))
        self.logger.info('[PAGINATED] Received {} categories'.format(len(categories)))
        categories = categories[45:]
        for category in categories:
            time.sleep(self.delay * self.threads)
            print(self.delay * self.threads)
            paginated = Walcart.paginated(category.id)
            for i in range(category.pages_parsed):
                if 'nextPage' in paginated:
                    time.sleep(self.delay * self.threads)
                    paginated = Walcart.get_json(paginated['nextPage'])
                else:
                    category.pages_parsed = -1
            if 'items' in paginated:
                products = []
                products_data = paginated['items']
                for product_data in products_data:
                    product = self.make_product(product_data)
                    products.append(product)
                self.logger.info('\t[PAGINATED] Saving {} products...'.format(len(products)))
                res = self.pub.call({'method': 'save', 'resource': serialize(products)})
                if 'success' not in res:
                    self.logger.critical('[PAGINATED] '.format(res['message']))
            category.pages_parsed += 1
            self.pub.call({'method': 'save', 'resource': serialize(category)})

    def update_prices(self):
        res = self.pub.call({'method': 'get', 'resource': 'product', 'where': {}})
        try:
            products = unserialize(res['result'])
        except Exception as e:
            self.logger.critical('[UPDATE_PRICES] {}'.format(str(e)))
        for product in products:
            time.sleep(self.delay * self.threads)
            self.update_price(product)

    def update_price(self, product):
        self.logger.info('[UPDATE_PRICES] Updating price for {}'.format(product.name))
        product_data = Walcart.product(product.id)
        current_price = product_data.get('salePrice')
        stock = product_data.get('stock')
        old_price = None if not product.prices else product.prices[-1].price
        self.logger.info('\t[UPDATE_PRICES] Old Price: {}\tCurrent Price: {}'.format(old_price, current_price))
        if old_price != current_price:
            self.logger.info('\t\t[UPDATE_PRICES] Price has been updated successfully.')
            product.prices.append(Price(price=current_price, stock=stock))
            res = self.pub.call({'method': 'save', 'resource': serialize(product)})
            if not res.get('success'):
                self.logger.critical('[UPDATE_PRICES] {}'.format(res['message']))
        else:
            self.logger.info('\t\t[UPDATE_PRICES] Price has not changed. No update necessary.')
            return (product, False)

if __name__ == '__main__':
    running = True
    burro = ElBurro()
    burro.start_updating()
