from datetime import datetime
import json
import logging

from google.appengine.ext import ndb


def from_epoch(value):
    """
        :param value:
            Instance of `float` as the number of seconds since unix epoch.
        :returns:
            Instance of `datetime.datetime`.
    """
    return datetime.utcfromtimestamp(value / 1000)


class SerializableModel(ndb.Model):

    def to_dict(self, includes=None, excludes=None):
        """Encodes an `ndb.Model` to a `dict`. By default, only `ndb.Property`
        attributes are included in the result.

            :param include:
                List of strings keys of class attributes. Can be the name of
                the either a method or property.
            :param exclude:
                List of string keys to omit from the return value.
            :returns: Instance of `dict`.
            :raises: `ValueError` if any key in the `include` param doesn't
            exist.
        """
        value = ndb.Model.to_dict(self)
        # set the `id` of the entity's key by default..
        if self.key:
            value['key'] = self.key.urlsafe()
            value['id'] = self.key.id()
        if includes:
            for inc in includes:
                attr = getattr(self, inc, None)
                if attr is None:
                    cls = self.__class__
                    logging.warn('Cannot encode %s' % cls)
                    continue
                if callable(attr):
                    value[inc] = attr()
                else:
                    value[inc] = attr
        if excludes:
            # exclude items from the result dict, by popping the keys
            # from the dict..
            [value.pop(exc) for exc in excludes if exc in value]
        return value

    @classmethod
    def from_dict(cls, value):
        """
            :param cls: `ndb.Model` subclass.
            :param value:
        """
        def _decode(_result, _value):
            """
            Deserializes `dict` values to `ndb.Property` values.
            """
            for key, val in _value.iteritems():
                prop = cls._properties.get(key)
                if prop is None:
                    logging.warn('Cannot decode %s for %s' % (key, cls))
                    continue
                if isinstance(prop, (ndb.DateTimeProperty, ndb.DateProperty,
                                     ndb.TimeProperty)):
                    if prop._repeated:
                        val = [from_epoch(v) for v in val]
                    else:
                        val = from_epoch(val)
                if isinstance(prop, ndb.BlobKeyProperty):
                    if prop._repeated:
                        val = [ndb.BlobKey(urlsafe=v) for v in val]
                    else:
                        val = ndb.BlobKey(urlsafe=val)
                if isinstance(prop, ndb.KeyProperty):
                    if prop._repeated:
                        val = [ndb.Key(urlsafe=v) for v in val]
                    else:
                        val = ndb.Key(urlsafe=val)
                if isinstance(prop, ndb.BlobProperty):
                    pass
                _result[key] = val
            return _result
        return cls(**_decode({}, value))

    @classmethod
    def from_json(cls, value):
        """
        Deserializes a json str to an instance of an `ndb.Model` subclass.

            :param cls: `ndb.Model` subclass.
            :param value:
        """
        value = json.loads(value, strict=False)
        if isinstance(value, list):
            result = [cls.from_dict(v) for v in value]
        else:
            result = cls.from_dict(value)
        return result

