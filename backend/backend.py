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
	

	def fill_request(request):
		request_method = request["method"]
		func = self.METHODS[request_method]
		return func(request["data"])

	def register(user):
		newUser = User(
			username=user['username'],
			password=user['password'],
			email=user['email']
		)
		res = self.pub.call({'save': serialize(newUser)})
		if res['success']:
			return {'success': True, 'message': 'User has been register successfully!' }
		else:
			return res

	def login(user):
		pass

		

if __name__ == '__main__':
	backend = BackendServ()
	backend.sub.listen()
