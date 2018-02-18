import	sys 
sys.path.insert(0, "../lib")
from rpc_sub import RpcSub
from config import Backend

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
	pass

def login(user):
	pass

if __name__ == '__main__':

	init_methods()
	backend = RpcSub(Backend.queue, fill_request)
	backend.listen()