from db.utils import TableError


class SQLcompiler:
    """
    把query对象中转化为sql语句
    """
    operators = {
        'exact': '= {}',
        'iexact': 'LIKE {}',
        'contains': 'LIKE BINARY {}',
        'icontains': 'LIKE {}',
        'gt': '> {}',
        'gte': '>= {}',
        'lt': '< {}',
        'lte': '<= {}',
        'startswith': 'LIKE BINARY {}',
        'endswith': 'LIKE BINARY {}',
        'istartswith': 'LIKE {}',
        'iendswith': 'LIKE {}',
        'in': 'IN {}'
    }

    def __init__(self, query):
        self.__query = query

    def select(self, query):
        select_expr = 'SELECT {0} FROM {1}'
        if query.table is None:
            raise TableError('Table of Database must be designated')
        if query.select is None:
            select_expr = select_expr.format('*', query.table)

        elif isinstance(query.select, str):
            select_expr = select_expr.format(query.select, query.table)

        elif isinstance(query.select, list):
            select_expr = select_expr.format(','.join(query.select), query.table)
        return select_expr

    def as_sql(self):
        select = self.select(self.__query)
        if self.__query.has_extra():
            extra = self.__query.where.as_sql(self)[0]
            extra = ' WHERE ' + extra
            self.__query.set_empty()
        else:
            extra = ''
        return select + extra

    def as_decription(self):
        return self.decription(self.__query)

    def insert(self, query):
        pass

    def delete(self, query):
        pass

    def update(self, query):
        pass

    def decription(self, query):
        expr = "SELECT NAME FROM syscolumns WHERE id=Object_Id('{}')"
        expr = expr.format(query.table)
        return expr

    def compile(self, node):
        vendor_impl = getattr(node, 'as_sql', None)
        if vendor_impl:
            sql, params = vendor_impl(self)
            return sql, params
        else:
            return str(node), [node]











