import pickle
import codecs

def serialize(obj):
    return codecs.encode(pickle.dumps(obj), 'base64').decode('utf-8')

def unserialize(str_):
    return pickle.loads(codecs.decode(str_.encode('utf-8'), 'base64'))
