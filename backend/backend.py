import	sys
sys.path.insert(0, "../lib")
sys.path.insert(0, "../database")
from models import User, Product, Price, Tracked
from rpc_sub import RpcSub
from rpc_pub import RpcPub
from walcart import Walcart
from el_burro import ElBurro
import logging
import threading

from config import Backend, Database
from common import serialize, unserialize

logging.basicConfig(filename='/var/log/it490/backend/backendserv.log',level=logging.INFO, format='%(asctime)s %(message)s')

class BackendServ(object):
	def __init__(self):
		self.pub = RpcPub(Database.queue)
		self.sub = RpcSub(Backend.queue, self.fill_request)
		self.METHODS = {
			"register": self.register,
			"login": self.login,
			"search": self.search,
			"track_product": self.track_product,
			"get_user": self.get_user
		}
		self.logger = logging.getLogger('backendserv')
		self.logger.addHandler(logging.StreamHandler())

	def fill_request(self, request):
		request_method = request.get("method", None)
		if request_method:
			func = self.METHODS.get(request_method)
			return func(request["data"])
		self.logger.info('Invalid request: {}'.format(request_method))
		return {'success': False, 'message': 'Invalid request'}

	def register(self, user):
		newUser = User(**user)
		res = self.pub.call({'method': 'save', 'resource': serialize(newUser)})
		if res['success']:
			return {'success': True, 'message': 'User has been registered successfully!' }
		else:
			self.logger.info(res['message'])
			return res

	def login(self, user):
		res = self.pub.call({'method': 'get', 'resource': 'user', 'where': user})
		user = unserialize(res['result'])
		if user:
			return {'hash': user.password}
		self.logger.info('Invalid username')
		return {'success': False, 'message': 'Invalid username'}

	def search(self, product_id):
		res = self.pub.call({'method': 'get', 'resource': 'product', 'where': {'id': product_id}})
		product = unserialize(res['result'])
		if not product:
			print(product_id)
			product_data = Walcart.product(product_id)
			if product_data.get('message'):
				return product_data
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
			res = self.pub.call({'method': 'save', 'resource': serialize(product)})
			if not res.get('success'):
				self.logger.info(res['message'])
				return res
			res = self.pub.call({'method': 'get', 'resource': 'product', 'where': {'id': product_data.get('itemId')}})
			return {'product': unserialize(res['result']).to_dict()}
		return {'product': product.to_dict()}

	def track_product(self, vald):
		username = vald['username']
		product_id = vald['product_id']
		try:
			res = self.pub.call({'method': 'get', 'resource': 'user', 'where': {'username': username}})
			user = unserialize(res['result'])
			res = self.pub.call({'method': 'get', 'resource': 'product', 'where': {'id': product_id}})
			product = unserialize(res['result'])
		except Exception as e:
			return {'message': str(e)}
		tracked = Tracked(wishlist=vald['wishlist'])
		tracked.product = product
		user.products.append(tracked)
		res = self.pub.call({'method': 'save', 'resource': serialize(user)})
		if not res.get('success'):
			self.logger.info(res['message'])
		return res

	def get_user(self, username):
		try:
			res = self.pub.call({'method': 'get', 'resource': 'user', 'where': {'username': username}})
			user = unserialize(res['result'])
		except Exception as e:
			return {'message': str(e)}
		return {'success': True, 'user': user.to_dict()}

if __name__ == '__main__':
	backend = BackendServ()
	burro = ElBurro()
	#threading.Thread(target=burro.start_updating).start()
	backend.sub.listen()
