from db.utils import Node
from db.backends import SQLcompiler
from db.utils import FieldError,WhereNode,NothingNode,AND,OR

__all__ = ['Query']


class Query:
    def __init__(self, model, where=WhereNode):
        self.model = model
        self.where = where()
        self.where_class = where
        self.compiler = None
        self.table = self.model.table
        self.select = self.model.select_list
        self.insert = None
        self.delete = None
        self.update = None

    def _new_instance(cls, model, where=WhereNode):
        obj = Query(model=model, where=where)
        return obj

    def add_q(self, q_project, branch_negated=False, current_negated=False):
        clause = self._add_q(q_project, branch_negated=branch_negated, current_negated=current_negated)
        if clause:
            self.where.add(clause, AND)

    def clear(self):
        self._clear()

    def as_sql(self):
        return self.get_compiler().as_sql()

    def all(self):
        query = self._new_instance(self.model)
        return query.get_compiler().as_sql()

    def as_decription(self):
        return self.get_compiler().as_decription()

    def has_extra(self):
        return not self.is_empty()

    def set_empty(self):
        self.where.add(NothingNode(), AND)

    def is_empty(self):
        if len(self.where.children) == 0:
            return True
        elif isinstance(self.where.children[-1], NothingNode):
            return True
        else:
            return False

    def _add_q(self, q_project, branch_negated=False, current_negated=False):
        connector = q_project.connector
        current_negated = current_negated ^ q_project.negated
        branch_negated = branch_negated or q_project.negated
        target_clause = self.where_class(connector=connector, negated=q_project.negated)
        for child in q_project.children:
            if isinstance(child, Node):
                child_clause = self._add_q(child, branch_negated=branch_negated, current_negated=current_negated)
            else:
                child_clause = self.build_filter(child, branch_negated=branch_negated, current_negated=current_negated)
            if child_clause:
                target_clause.add(child_clause, connector)
        return target_clause

    def _clear(self):
        self.where.children = []
        self.where.connector = self.where.default
        self.where.negeted = False

    def build_filter(self, filter_expr, branch_negated, current_negated):
        if isinstance(filter_expr, dict):
            raise FieldError("Cannot parse keyword query as dict")
        arg, value = filter_expr
        check_filter = self.check_filter_type(arg)
        if not check_filter:
            return ''
        expr = self.get_filter_data(arg, value)
        return expr

    def check_filter_type(self, arg):
        if not isinstance(arg, str):
            return False
        else:
            return True

    def get_compiler(self):
        if self.compiler is None:
            self.compiler = SQLcompiler(self)
        return self.compiler

    def get_filter_data(self, arg, value):
        compiler = self.get_compiler()
        operators = compiler.operators
        expr = '"{:s}" {:s}'
        field, operator = arg.split('__')
        if isinstance(value, list):
            value = list(set(value))
            if len(value) == 1 and operator == 'in':
                value = value[0]
                operator = 'exact'
            else:
                value = tuple(value)
        elif isinstance(value, str):
            value = '\'' + value + '\''
        if field and operator:
            if operators[operator] and value:
                expr = expr.format(field, operators[operator])
                expr = expr.format(value)
                return expr
            else:
                return ''
        else:
            return ''












