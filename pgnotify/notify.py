from __future__ import absolute_import, division, print_function, unicode_literals

import errno
import fcntl
import os
import select
import signal

import psycopg2
import six
from logx import log
from six import string_types


def get_wakeup_fd():
    pipe_r, pipe_w = os.pipe()
    flags = fcntl.fcntl(pipe_w, fcntl.F_GETFL, 0)
    flags = flags | os.O_NONBLOCK
    flags = fcntl.fcntl(pipe_w, fcntl.F_SETFL, flags)

    signal.set_wakeup_fd(pipe_w)
    return pipe_r


def signal_handler(signal, frame):
    pass


try:
    import sqlalchemy
except ImportError:
    sqlalchemy = None  # flake8: noqa

if sqlalchemy:
    from sqlalchemy.engine.base import Engine


def get_dbapi_connection(x):
    if isinstance(x, string_types):
        c = psycopg2.connect(x)
        x = c
    elif sqlalchemy and isinstance(x, Engine):
        sqla_connection = x.connect()
        sqla_connection.execution_options(isolation_level="AUTOCOMMIT")
        sqla_connection.detach()
        x = sqla_connection.connection.connection
    else:
        pass
    x.autocommit = True
    return x


def quote_table_name(name):
    return '"{}"'.format(name)


def await_pg_notifications(
    dburi_or_sqlaengine_or_dbapiconnection,
    channels,
    timeout=3,
    yield_on_timeout=False,
    handle_keyboardinterrupt=False,
):
    """Subscribe to PostgreSQL notifications, and handle them
    in infinite-loop style.

    On an actual message, returns the notification (with .pid,
    .channel, and .payload attributes).

    If you've enabled 'yield_on_timeout', yields None on timeout.

    If you've enabled 'handle_keyboardinterrupt', yields False on
    interrupt.
    """

    cc = get_dbapi_connection(dburi_or_sqlaengine_or_dbapiconnection)

    if isinstance(channels, string_types):
        channels = [channels]

    names = (quote_table_name(each) for each in channels)
    listens = "; ".join(["listen {}".format(n) for n in names])

    c = cc.cursor()
    c.execute(listens)
    c.close()

    try:
        if handle_keyboardinterrupt:
            original_handler = signal.signal(signal.SIGINT, signal_handler)
            wakeup = get_wakeup_fd()
            listen_on = [cc, wakeup]
        else:
            listen_on = [cc]

        while True:
            try:
                r, w, x = select.select(listen_on, [], [], timeout)
                log.debug("select call awoken, returned: {}".format((r, w, x)))

                if (r, w, x) == ([], [], []):
                    log.debug("idle timeout on select call, carrying on...")
                    if yield_on_timeout:
                        yield None

                if cc in r:
                    cc.poll()

                    while cc.notifies:
                        notify = cc.notifies.pop()
                        log.debug(
                            "NOTIFY: {}, {}, {}".format(
                                notify.pid, notify.channel, notify.payload
                            )
                        )
                        yield notify

                if handle_keyboardinterrupt and wakeup in r:
                    yield False

            except select.error as e:
                e_num, e_message = e
                if e_num == errno.EINTR:
                    log.error("EINTR happened during select")
    finally:
        if handle_keyboardinterrupt:
            signal.signal(signal.SIGINT, original_handler)
