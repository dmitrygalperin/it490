import	sys
sys.path.insert(0, "../lib")
sys.path.insert(0, "../database")
from models import User, Product, Price, Tracked
from rpc_sub import RpcSub
from rpc_pub import RpcPub
from walcart import Walcart

from config import Backend, Database
from common import serialize, unserialize


class BackendServ(object):
	def __init__(self):
		self.pub = RpcPub(Database.queue)
		self.sub = RpcSub(Backend.queue, self.fill_request)
		self.METHODS = {
			"register": self.register,
			"login": self.login,
            "search": self.search
		}

	def fill_request(self, request):
		request_method = request.get("method", None)
		if request_method:
			func = self.METHODS[request_method]
			return func(request["data"])
		return {'success': False, 'message': 'Invalid request'}

	def register(self, user):
		newUser = User(**user)
		res = self.pub.call({'method': 'save', 'resource': serialize(newUser)})
		if res['success']:
			return {'success': True, 'message': 'User has been registered successfully!' }
		else:
			return res

	def login(self, user):
		res = self.pub.call({'method': 'get', 'resource': 'user', 'where': user})
		user = unserialize(res['result'])
		if user:
			return {'hash': user.password}
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
				product.prices.append(Price(price=price, product_id=product.id, stock=product_data.get('stock')))
			res = self.pub.call({'method': 'save', 'resource': serialize(product)})
			if not res['success']:
				return res
			print(res)
			return {'product': unserialize(res['resource']).to_dict()}
		return {'product': product.to_dict()}

if __name__ == '__main__':
	backend = BackendServ()
	backend.sub.listen()
