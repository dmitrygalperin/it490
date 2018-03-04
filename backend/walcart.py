import sys
sys.path.insert(0, "../lib")
from config import Api
import json
from urllib.request import urlopen

class Walcart(object):
    key            = Api.key
    base_url       = Api.base_url
    items_url      = Api.items_url
    nbp_url        = Api.nbp_url
    postbrowse_url = Api.postbrowse_url

    @classmethod
    def product(cls, product_id):
        url = '{}{}/{}?apiKey={}&format=json'.format(cls.base_url, cls.items_url, product_id, cls.key)
        return cls.get_json(url)

    @classmethod
    def nbp(cls, product_id):
        url = '{}{}?apiKey={}&itemId={}'.format(cls.base_url, cls.nbp_url, cls.key, product_id)
        return cls.get_json(url)

    @classmethod
    def get_json(cls, url):
        try:
            print(url)
            return json.loads(urlopen(url).read().decode('utf-8', 'ignore'))
        except Exception as e:
            print(str(e))
            return {'message': 'Product not found'}
