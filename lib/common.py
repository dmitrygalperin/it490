import pickle
import codecs

def stringify(obj):
    return codecs.encode(pickle.dumps(obj), 'base64').decode('utf-8')

def objectify(str_):
    return pickle.loads(codecs.decode(str_.encode('utf-8'), 'base64'))
