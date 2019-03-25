from db.backends.base.client import BaseClient


class DatabaseClient(BaseClient):
    executable_name = 'Sql Server'


    @classmethod
    def database_setting(cls,settings_dict):
        if isinstance(settings_dict,str):
            return settings_dict
        args = ''
        driver = settings_dict['DRIVER']
        server = settings_dict['SERVER']
        database = settings_dict['DATABASE']
        uid = settings_dict['UID']
        pwd = settings_dict['PWD']
        if driver:
            args += 'DRIVER={};'.format(driver)
        if server:
            args += 'SERVER={};'.format(server)
        if database:
            args += 'DATABASE={};'.format(database)
        if uid:
            args += 'UID={};'.format(uid)
        if pwd:
            args += 'PWD={}'.format(pwd)
        return args





