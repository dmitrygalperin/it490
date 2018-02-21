#!/usr/bin/env python
import sys
sys.path.insert(0, "../lib")

import pika
from rpc_sub import RpcSub
from config import RabbitMQ, Database
from dbcon import Dbcon
from common import serialize, unserialize
import logging

logging.basicConfig(filename='/var/log/it490/dbserv.log',level=logging.INFO, format='%(asctime)s %(message)s')

#CRUD operation types
CREATE = 'create'
READ   = 'read'
UPDATE = 'update'
DELETE = 'delete'

#SQLAlchemy operation types
GET = 'get'
SAVE = 'save'

class DbServ(object):

    '''
    Middleware that subscribes to RabbitMQ RPC channel via pika and translates
    JSON request messages into database CRUD operations via SQLAlchemy.

    Example request format:

    {
        'method': 'update',
    	'resource': 'user',
    	'where': [
    		['username', '==', 'jimbo']
    	],
    	'values': {
    		'username': 'newusername'
    	}
    }
    '''

    def __init__(self):
        self.session = Dbcon.get_session()
        self.logger = logging.getLogger('dbserv')
        self.logger.addHandler(logging.StreamHandler())

    def fill_request(self, request):
        try:
            req_method = request.get('method').lower()
            req_resource = request.get('resource')
            vald = request.get('values')
            where_clause = request.get('where')
            order_by = request.get('orderBy')
            if req_method != SAVE:
                Resource = Dbcon.get_resource(req_resource.lower())
                if not Resource:
                    return {'message': "The specified resource <{}> doesn't exist".format(req_resource)}
                tbl = Resource.__table__

            if req_method == CREATE:
                stmt = tbl.insert()
            elif req_method == READ:
                stmt = tbl.select()
            elif req_method == UPDATE:
                stmt = tbl.update()
            elif req_method == DELETE:
                stmt = tbl.delete()
            elif req_method == GET:
                return self.get(Resource, where_clause)
            elif req_method == SAVE:
                return self.save(req_resource)
            else:
                return {'message': "Invalid request type. Valid types are create, read, update, delete, get, save. e.g {method: 'create'}"}

            if where_clause:
                stmt = self.set_where(where_clause, stmt, tbl)
            if vald:
                stmt = stmt.values(**vald)
            if order_by:
                stmt = self.set_order_by(order_by, stmt, tbl)
        except Exception as e:
            self.logger.info(str(e))
            return {'message': str(e)}

        self.logger.info(vald)

        return self.execute(stmt)

    def execute(self, stmt):
        self.logger.info(stmt)
        try:
            res = self.session.execute(stmt)
            self.session.commit()
            try:
                return {'rows': [dict(row) for row in res]}
            except:
                return {'affected': res.rowcount}
        except Exception as e:
            self.logger.info(e)
            self.session.rollback()
            return {'message': str(e)}

    def set_where(self, where_list, stmt, tbl):
        for where in where_list :
            col = getattr(tbl.c, where[0])
            op = where[1]
            comp = where[2]
            if op == '==':
                stmt = stmt.where(col==comp)
            elif op == '!=':
                stmt = stmt.where(col!=comp)
            elif op == 'like':
                stmt = stmt.where(col.like(comp))
            elif op == 'in':
                stmt = stmt.where(~col.in_(comp))
        return stmt

    def set_order_by(self, order_by, stmt, tbl):
        colname, direction = tuple(order_by)
        self.logger.info(colname,direction)
        col = getattr(tbl.c, colname)
        order_func = col.desc() if direction == 'desc' else col.asc()
        return stmt.order_by(order_func)

    def get(self, resource, where_clause):
        response = []
        result = self.session.query(resource).filter_by(**where_clause)
        for item in result:
            response.append(item)
        if len(response) is 1:
            response = response[0]
        self.logger.info(response)
        return {'result': serialize(response)}

    def save(self, resource):
        self.session.add(unserialize(resource))
        try:
            self.session.commit()
            return {'success': True}
        except Exception as e:
            self.logger.info(e)
            self.session.rollback()
            return {'message': str(e)}

if __name__ == '__main__':
    dbserv = DbServ()
    if not dbserv.session:
        sys.exit()
    rpc_sub = RpcSub(Database.queue, dbserv.fill_request)
    rpc_sub.listen()
