class Database(object):
    username     = 'dg94'
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

class RabbitMQ(object):
    username     = 'super'
    password     = 'super'
    host         = '192.168.2.102'
    port         = 5672
    virtual_host = '/'
    exchange     = ''
