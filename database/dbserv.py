#!/usr/bin/env python
import sys
sys.path.insert(0, "/home/produ/it490/lib")

import pika
from rpc_sub import RpcSub
from config import RabbitMQ, Database
from dbcon import Dbcon
from common import serialize, unserialize
import logging
from sqlalchemy.orm import joinedload_all

logging.basicConfig(filename='/var/log/it490/database/dbserv.log',level=logging.INFO, format='%(asctime)s %(message)s')

#CRUD operation types
CREATE = 'create'
READ   = 'read'
UPDATE = 'update'
#DELETE = 'delete'

#SQLAlchemy operation types
GET = 'get'
SAVE = 'save'
DELETE = 'delete'
SQL_SELECT_TO_ORM = 'sql_select_to_orm'

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
            sql = request.get('sql')
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
                return self.delete(Resource, where_clause)
            elif req_method == GET:
                return self.get(Resource, where_clause)
            elif req_method == SAVE:
                return self.save(req_resource)
            elif req_method == SQL_SELECT_TO_ORM:
                return self.sql_select_to_orm(Resource, sql)
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
        if where_clause and type(list(where_clause.values())[0]) is list:
            col = list(where_clause.keys())[0]
            values = list(where_clause.values())[0]
            result = self.session.query(resource).filter(getattr(resource, col).in_(values)).all()
        else:
            result = self.session.query(resource).filter_by(**where_clause)
        #self.session.expunge_all()
        for item in result:
            response.append(item)
        self.logger.info(response)
        if len(response) == 1:
            response = response[0]
        self.logger.info(response)
        return {'result': serialize(response)}

    def save(self, resource):
        r_obj = unserialize(resource)
        if type(r_obj) is list:
            for obj in r_obj:
                self.session.add(obj)
                try:
                    self.session.commit()
                except:
                    self.session.rollback()
        else:
            self.session.add(r_obj)
        try:
            self.session.commit()
            self.session.expunge_all()
            #r_obj = self.session.query(type(r_obj)).filter_by(id=r_obj.id).options(joinedload_all()).one()
            return {'success': True}
        except Exception as e:
            self.logger.info(e)
            self.session.rollback()
            return {'message': str(e)}

    def delete(self, resource, where_clause):
        self.session.query(resource).filter_by(**where_clause).delete(synchronize_session='fetch')
        self.session.commit()
        return {'success': True}

    def sql_select_to_orm(self, resource, sql):
        rows = self.session.execute(sql)
        ids = [row[0] for row in rows]
        return self.get(resource, {'id': ids})

if __name__ == '__main__':
    dbserv = DbServ()
    if not dbserv.session:
        sys.exit()
    rpc_sub = RpcSub(Database.queue, dbserv.fill_request)
    rpc_sub.listen()
