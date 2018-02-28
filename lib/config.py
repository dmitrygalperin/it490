class Database(object):
    username     = 'walcart'
    password     = 'it490'
    #host         = '192.168.2.110'
    host         = '192.168.56.3'
    db_type      = 'mysql'
    db_name      = 'walcart'
    queue        = 'db'

class Frontend(object):
    host         = '192.168.2.105'

class Backend(object):
    host         = '192.168.2.101'
    queue        = 'backend'

class Api(object):
    key            = 'tujnm62k873ak8h7se4b4s9e'
    base_url       = 'http://api.walmartlabs.com/v1'
    items_url      = '/items'
    nbp_url        = '/nbp'
    postbrowse_url = '/postbrowse'

class RabbitMQ(object):
    username     = 'super'
    password     = 'super'
    host         = '192.168.2.102'
    port         = 5672
    virtual_host = '/'
    exchange     = ''
