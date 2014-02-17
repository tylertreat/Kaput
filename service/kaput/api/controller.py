import logging

from flask import request

from kaput.api.blueprint import blueprint


@blueprint.route('/v1/exception', methods=['POST'])
def process_exception():
    # TODO: Implement
    data = request.data
    logging.debug('data: %s' % data)

    return data, 200

