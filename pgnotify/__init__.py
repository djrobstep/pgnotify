from __future__ import absolute_import, division, print_function, unicode_literals

from logx import log

from .notify import (
    await_pg_notifications,
    get_dbapi_connection,  # noqa
    start_listening,
)

log.set_null_handler()


def notify(connection, channel, payload):
    """Send a PostgreSQL notify with a payload

    :param connection: dburi, sqlengine or dbapiconnection
    :param channel: channel that the notify is sent to
    :param payload: payload to be sent together with notify
    """
    connection = get_dbapi_connection(connection)

    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_notify('%s', '%s');", (channel, payload))

    connection.close()
