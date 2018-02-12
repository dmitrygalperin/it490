class Database(object):
    username     = 'dg94'
    password     = 'it490'
    host         = '192.168.56.101'
    db_type      = 'mysql'
    db_name      = 'testdb'
    queue        = 'db'

class Frontend(object):
    host         = '<FRONTEND_HOSTNAME>'

class Backend(object):
    host         = '<BACKEND_HOSTNAME>'
    queue        = 'backend'

class RabbitMQ(object):
    username     = 'dg94'
    password     = 'it490'
    host         = '192.168.56.102'
    port         = 5672
    virtual_host = '/'
    exchange     = ''
