class Database(object):
    username     = 'walcart'
    password     = 'it490'
    host         = '192.168.2.110'
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
    paginated_url  = '/paginated/items'
    postbrowse_url = '/postbrowse'
    search_url     = '/search'
    stores_url     = '/stores'

class RabbitMQ(object):
    username     = 'super'
    password     = 'super'
    host         = '192.168.2.102'
    port         = 5672
    virtual_host = '/'
    exchange     = ''
