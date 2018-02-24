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
    def get_item(cls, item_id):
        url = '{}{}/{}?apiKey={}&format=json'.format(cls.base_url, cls.items_url, item_id, cls.key)
        res = urlopen(url)
        return json.loads(res.read())
