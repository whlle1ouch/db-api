from .tree import Node


AND = 'AND'
OR = 'OR'


class WhereNode(Node):
    default = AND
    resolved = False
    contional = True

    def clone(self):
        """
        Create a clone of the tree. Must only be called on root nodes (nodes
        with empty subtree_parents). Childs must be either (Constraint, lookup,
        value) tuples, or objects supporting .clone().
        """
        clone = self.__class__._new_instance(
            children=[], connector=self.connector, negated=self.negated)
        for child in self.children:
            if hasattr(child, 'clone'):
                clone.children.append(child.clone())
            else:
                clone.children.append(child)
        return clone

    def as_sql(self, compiler):
        result = []
        result_params = []
        if self.connector == AND:
            full_needed, empty_needed = len(self.children), 1
        else:
            full_needed, empty_needed = 1, len(self.children)

        for child in self.children:
            try:
                sql, params = compiler.compile(child)
            except EmptyResultSet:
                empty_needed -= 1
            else:
                if sql:
                    result.append(sql)
                    result_params.extend(params)
                else:
                    full_needed -= 1
            if empty_needed == 0:
                if self.negated:
                    return '', []
                else:
                    raise EmptyResultSet
            if full_needed == 0:
                if self.negated:
                    raise EmptyResultSet
                else:
                    return '', []
        conn = ' {} '.format(self.connector)
        sql_string = conn.join(result)
        if sql_string:
            if self.negated:
                # Some backends (Oracle at least) need parentheses
                # around the inner SQL in the negated case, even if the
                # inner SQL contains just a single expression.
                sql_string = 'NOT ({})'.format(sql_string)
            elif len(result) > 1 or self.resolved:
                sql_string = '({})'.format(sql_string)
        return sql_string, result_params


class NothingNode:
    """A node that matches nothing."""
    contains_aggregate = False

    def as_sql(self, compiler=None, connection=None):
        raise EmptyResultSet