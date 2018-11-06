from __future__ import absolute_import, division, print_function, unicode_literals

import os
import signal

import psycopg2
from pytest import raises
from sqlalchemy import create_engine
from sqlbag import S

from pgnotify import await_pg_notifications
from pgnotify.notify import get_dbapi_connection

SIGNALS_TO_HANDLE = [signal.SIGINT]


def test_get_connection(db):
    a = db
    b = create_engine(db)
    c = psycopg2.connect(db)

    for x in [a, b, c]:
        cc = get_dbapi_connection(x)
        try:
            assert type(cc) is type(c)
            assert cc.autocommit is True
        finally:
            cc.close()


def test_pg_notify(db):
    for n in await_pg_notifications(
        db,
        ["hello", "hello2"],
        timeout=0.01,
        yield_on_timeout=True,
        handle_signals=SIGNALS_TO_HANDLE,
    ):
        if n is None:
            with S(db) as s:
                s.execute("notify hello, 'here is my message'")

        elif isinstance(n, int):
            sig = signal.Signals(n)
            assert sig.name == "SIGINT"
            assert n == signal.SIGINT
            break

        else:
            assert n.channel == "hello"
            assert n.payload == "here is my message"
            os.kill(os.getpid(), signal.SIGINT)

    with raises(KeyboardInterrupt):
        for n in await_pg_notifications(
            db, "hello", timeout=0.1, yield_on_timeout=True
        ):
            os.kill(os.getpid(), signal.SIGINT)


def test_dynamic_timeout(db):
    def get_timeout():
        return -1

    for n in await_pg_notifications(
        db,
        ["hello", "hello2"],
        timeout=get_timeout,
        yield_on_timeout=True,
        notifications_as_list=True,
        handle_signals=SIGNALS_TO_HANDLE,
    ):
        if n is None:
            with S(db) as s:
                s.execute("notify hello, 'here is my message'")

        elif isinstance(n, int):
            sig = signal.Signals(n)
            assert sig.name == "SIGINT"
            assert n == signal.SIGINT
            break

        else:
            assert len(n) == 1
            _n = n[0]
            assert _n.channel == "hello"
            assert _n.payload == "here is my message"
            os.kill(os.getpid(), signal.SIGINT)

    with raises(KeyboardInterrupt):
        for n in await_pg_notifications(
            db, "hello", timeout=0.1, yield_on_timeout=True
        ):
            os.kill(os.getpid(), signal.SIGINT)
