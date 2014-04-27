import datetime
import json
import logging
import time

from google.appengine.ext import db
from google.appengine.ext import ndb


SERIALIZABLE_TYPES = (int, long, float, bool, dict, basestring, list)


class SerializableMixin(object):

    def to_dict_(self, includes=None, excludes=None):
        """Convert a db or ndb entity to a json-serializable dict."""
        output = {}

        if self.key:
            output['id'] = self.key.id()
            output['key'] = self.key.urlsafe()

        for key, prop in self._properties.iteritems():
            value = getattr(self, key)

            if value is None or isinstance(value, SERIALIZABLE_TYPES):
                output[key] = value
            elif isinstance(value, datetime.date):
                # Convert date/datetime to unix timestamp
                output[key] = time.mktime(value.utctimetuple())
            elif isinstance(value, (db.Key, ndb.Key)):
                output[key] = value.id()
            elif isinstance(value, (db.Model, ndb.Model)):
                output[key] = self.to_dict(value)
            else:
                raise ValueError('Cannot encode ' + repr(prop))

        if includes:
            for inc in includes:
                attr = getattr(self, inc, None)
                if attr is None:
                    cls = self.__class__
                    logging.warn('Cannot encode %s' % cls)
                    continue
                if callable(attr):
                    output[inc] = attr()
                else:
                    output[inc] = attr

        if excludes:
            [output.pop(exc) for exc in excludes if exc in output]

        return output


class EntityEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.date):
            return time.mktime(obj.utctimetuple())

        elif isinstance(obj, ndb.Model):
            return obj.to_dict()

        else:
            return json.JSONEncoder.default(self, obj)


def chunk(the_list, chunk_size):
    """Chunks the given list into lists of size chunk_size.

    Args:
        the_list: the list to chunk into sublists.
        chunk_size: the size to chunk the list by.

    Returns:
        generator that yields the chunked sublists.
    """

    if not the_list or chunk_size <= 0:
        yield []
        return

    for i in xrange(0, len(the_list), chunk_size):
        yield the_list[i:i + chunk_size]

