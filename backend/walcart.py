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
    paginated_url  = Api.paginated_url
    postbrowse_url = Api.postbrowse_url
    search_url     = Api.search_url
    stores_url     = Api.stores_url

    @classmethod
    def product(cls, product_id):
        url = '{}{}/{}?apiKey={}&format=json'.format(cls.base_url, cls.items_url, product_id, cls.key)
        return cls.get_json(url)

    @classmethod
    def nbp(cls, product_id):
        url = '{}{}?apiKey={}&itemId={}'.format(cls.base_url, cls.nbp_url, cls.key, product_id)
        return cls.get_json(url)

    @classmethod
    def paginated(cls, category_id):
        url = '{}{}?category={}&apiKey={}&format=json'.format(cls.base_url, cls.paginated_url, category_id, cls.key)
        return cls.get_json(url)

    @classmethod
    def search(cls, query):
        url = '{}{}?apiKey={}&query={}'.format(cls.base_url, cls.search_url, cls.key, query)
        return cls.get_json(url)

    @classmethod
    def get_stores(cls, zipc):
        url = '{}{}?apiKey={}&zip={}&format=json'.format(cls.base_url, cls.stores_url, cls.key, zipc)
        return cls.get_json(url)

    @classmethod
    def get_json(cls, url):
        try:
            print(url)
            return json.loads(urlopen(url).read().decode('utf-8'))
        except Exception as e:
            print(str(e))
            return {'message': 'Could not get result. This may not be a problem with Walcart, but with Walmart product API'}
