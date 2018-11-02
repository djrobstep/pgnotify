import signal

from pgnotify import await_pg_notifications, get_dbapi_connection

# the first parameter of the await_pg_notifications
# loop is a dbapi connection in autocommit mode
CONNECT = "postgresql:///example"

# use this convenient method to create the right connection
# from a database URL
e = get_dbapi_connection(CONNECT)

SIGNALS_TO_HANDLE = [signal.SIGINT, signal.SIGTERM]

for n in await_pg_notifications(
    e,
    ["hello", "hello2"],
    timeout=10,
    yield_on_timeout=True,
    handle_signals=SIGNALS_TO_HANDLE,
):
    # the integer code of the signal is yielded on each
    # occurrence of a handled signal
    if isinstance(n, int):
        sig = signal.Signals(n)
        if n in SIGNALS_TO_HANDLE:
            print(f"handling {sig.name}")
        print("interrupted, stopping")
        break

    # the `yield_on_timeout` option makes the
    # loop yield `None` on timeout
    elif n is None:
        print("timeout, continuing")

    # handle the actual notify occurrences here
    else:
        print((n.pid, n.channel, n.payload))
