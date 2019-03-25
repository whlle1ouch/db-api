from .manager import Manager
import pandas as pd
from .fields import Field
import warnings


class ModelBase(type):
    def __new__(cls,name , bases , attrs):
        super_new = super().__new__
        parents = [b for b in bases if isinstance(b, ModelBase)]
        if not parents:
            return super_new(cls, name, bases, attrs)
        mappings = dict()
        for k,v in attrs.items():
            if isinstance(v,Field):
                mappings[k] = v
        for k in mappings.keys():
            attrs.pop(k)
        attrs['__table__']  = name.lower()
        attrs['__mappings__'] = mappings
        new_class = super_new(cls, name, bases, attrs)
        return new_class


class Model(metaclass=ModelBase):
    dynamic = True

    def __init__(self, db, table, select):
        self.database = db
        self.table = table
        self.select_list = select
        self.data = None
        self._prepare()

    @classmethod
    def _new_instance(cls,other):
        if not isinstance(other,Model):
            raise ValueError('{} is not Model object'.format(other))
        obj = Model(other.database , other.table , other.select_list)
        obj.__class__ = cls
        return obj

    def _prepare(self):
        manager = Manager(self)
        setattr(self, 'objects', manager)


    def set_db(self, db):
        self.database = db

    def set_table(self, table):
        self.table = table

    def set_select(self, select_list):
        self.select_list = select_list

    def update(self, q_filter=None):
        if self.data is None:
            if q_filter is not None:
                result = self.objects.filter(q_filter)
            else:
                result = self.objects.all()
            colname = self.decription()
            self.data = pd.DataFrame(result, columns=colname)
            self.data_format()

    def data_format(self):
        if self.data is None:
            raise ValueError('empty data')
        if not isinstance(self.data, pd.DataFrame):
            raise ValueError('data is not a dataframe object')
        # if hasattr(self,'pk'):
        #     try:
        #         self.data.index =self.data[self.pk]
        #     except KeyError as e:
        #         print(e.args[0])
        if hasattr(self,'datetime'):
            try:
                self.data = self.data.sort_values([self.datetime])
                self.data[self.datetime] = pd.to_datetime(self.data[self.datetime])
            except KeyError as e:
                print(e.args[0])

    def save_csv(self, f , sep , mode, index , columns , header):
        if self.data is None:
            raise ValueError('empty data')
        self.data.to_csv(f, sep=sep , mode=mode , index=index , columns=columns , header=header,encoding='utf_8_sig')

    def read_csv(self, f , header , sep=','):
        if self.data is not None:
            warnings.warn('data will will be overwrite')
        self.data = pd.read_csv(f, sep=sep , header = header, encoding='utf_8_sig')
        self.data.columns = self.decription()
        self.data_format()

    def decription(self):
        if self.select_list == '*':
            self.select_list = [f[0] for f in self.objects.decription()]
        return self.select_list




