from schema import Schema, Optional, Use


class Self(object): pass


class Parseable(object):

    _schema = None

    @classmethod
    def _replace_self(cls, data):
        '''
        Replace instances of 'Self' by own class in the current schema
        This makes recursive parsing possible
        '''
        print('replace_self({})'.format(data))
        if isinstance(data, list):
            for idx, val in enumerate(data):
                if val is Self:
                    data[idx] = cls
                else:
                    cls._replace_self(val)
        elif isinstance(data, dict):
            for key, val in data.items():
                if val is Self:
                    data[key] = cls
                else:
                    cls._replace_self(val)

    def __init__(self, data):
        self._replace_self(self._schema)
        self._data = Schema(self._schema, ignore_extra_keys=True).validate(data)

    def __getattr__(self, attr):
        return self._data[attr]

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               ', '.join(['{}={}'.format(key, value)
                                          for key, value
                                          in self._data.items()]))


def parseable(name, schema):
    class ParseableClass(Parseable):
        _schema = schema
    ParseableClass.__name__ = name
    return ParseableClass
