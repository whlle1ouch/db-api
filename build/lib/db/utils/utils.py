from .tree import Node
import copy


class cached_property:
    """
    Decorator that converts a method with a single self argument into a
    property cached on the instance.

    Optional ``name`` argument allows you to make cached properties of other
    methods. (e.g.  url = cached_property(get_absolute_url, name='url') )
    类缓存装饰器，在定义的类中调用创建其他的类的实例时，可以使用self作为缓存参数传递并创建
    name参数允许
    """
    def __init__(self, func, name=None):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')
        self.name = name or func.__name__

    def __get__(self, instance, cls=None):
        """
        Call the function and put the return value in instance.__dict__ so that
        subsequent attribute access on the instance returns the cached value
        instead of calling cached_property.__get__().
        """
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res




class Q(Node):
    """
    Encapsulate filters as objects that can then be combined logically (using
    `&` and `|`).
    """
    # Connection types
    AND = 'AND'
    OR = 'OR'
    default = AND
    conditional = True

    def __init__(self, *args, **kwargs):
        connector = kwargs.pop('_connector', None)
        negated = kwargs.pop('_negated', False)
        super().__init__(children=list(args) + sorted(kwargs.items()), connector=connector, negated=negated)

    def _combine(self, other, conn):
        if not isinstance(other, Q):
            raise TypeError(other)

        # If the other Q() is empty, ignore it and just use `self`.
        if not other:
            return copy.deepcopy(self)
        # Or if this Q is empty, ignore it and just use `other`.
        elif not self:
            return copy.deepcopy(other)

        obj = type(self)()
        obj.connector = conn
        obj.add(self, conn)
        obj.add(other, conn)
        return obj
    def __or__(self, other):
        return self._combine(other, self.OR)

    def __and__(self, other):
        return self._combine(other, self.AND)

    def __invert__(self):
        obj = type(self)()
        obj.add(self, self.AND)
        obj.negate()
        return obj

    def resolve_expression(self, query=None, allow_joins=True, reuse=None, summarize=False, for_save=False):
        # We must promote any new joins to left outer joins so that when Q is
        # used as an expression, rows aren't filtered d ue to joins.
        clause, joins = query._add_q(self, reuse, allow_joins=allow_joins, split_subq=False)
        query.promote_joins(joins)
        return clause

    def deconstruct(self):
        path = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        if path.startswith('django.db.models.query_utils'):
            path = path.replace('django.db.models.query_utils', 'django.db.models')
        args, kwargs = (), {}
        if len(self.children) == 1 and not isinstance(self.children[0], Q):
            child = self.children[0]
            kwargs = {child[0]: child[1]}
        else:
            args = tuple(self.children)
            if self.connector != self.default:
                kwargs = {'_connector': self.connector}
        if self.negated:
            kwargs['_negated'] = True
        return path, args, kwargs



class MetaConfig(type):
    def __new__(cls, name , bases , attrs):
        return super().__new__(cls,name,bases,attrs)
    def __call__(cls, *args , **kwargs):
        if not hasattr(cls,'_instance'):
            cls._instance = super().__call__(cls, *args , **kwargs)
        return cls._instance

class Config(metaclass=MetaConfig):
    CONFIG = None

    @classmethod
    def set(cls,config):
        cls._set_config(config)

    @classmethod
    def _set_config(cls,config):
        if isinstance(config,dict):
            cls.CONFIG = config
    @classmethod
    def parse(cls,db):
        if cls.CONFIG:
            settings = cls.CONFIG.get(db,None)
            if not settings:
                raise ValueError('has no <{}> config settings'.format(db))
            databases = Config._parse_settings(settings,'DATABASE')
            tables = Config._parse_settings(settings,'TABLE')
            selects = Config._parse_settings(settings,'SELECT')
            return databases,tables,selects

    @staticmethod
    def _parse_settings(settings,name):
        if isinstance(settings,dict):
            return settings.get(name,None)
        if isinstance(settings,str):
            return settings
        else:
            raise ValueError('invalid settings: <{}>'.format(settings))

