import	sys 
sys.path.insert(0, "../lib")
sys.path.insert(0, "../database")
from models import User
from rpc_sub import RpcSub
from rpc_pub import RpcPub

from config import Backend, Database
from common import serialize, unserialize


class BackendServ(object):
	
	def __init__(self):
		self.pub = RpcPub(Database.queue)
		self.sub = RpcSub(Backend.queue, self.fill_request)
		self.METHODS = {
			"register": self.register,
			"login": self.login
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
			return {'success': True, 'message': 'User has been register successfully!' }
		else:
			return res

	def login(self, user):
		res = self.pub.call({'method': 'get', 'resource': 'user', 'where': user})
		user = unserialize(res['result'])
		if user:
			return {'hash': user.password}
		return {'success': False, 'message': 'Invalid username'}

		

if __name__ == '__main__':
	backend = BackendServ()
	backend.sub.listen()
