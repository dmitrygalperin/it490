import	sys 
sys.path.insert(0, "../lib")
sys.path.insert(0, "../database")
from models import User
from rpc_sub import RpcSub
from config import Backend
from common import stringify, objectify


METHODS = dict()

def init_methods():
	METHODS = {
		"register": register,
		"login": login
	}

def fill_request(request):
	request_method = request["method"]
	func = METHODS[request_method]
	return func(request["data"])

def register(user):
	newUser = User(
		username=user['username'],
		password=user['password'],
		email=user['email']
	)
	res = pub.call({'save': stringify(newUser)})
	if res['success']:
		return {'success': True, 'message': 'User has been register successfully!' }
	else:
		return res

def login(user):
	pass

if __name__ == '__main__':

	init_methods()
	backend = RpcSub(Backend.queue, fill_request)
	backend.listen()