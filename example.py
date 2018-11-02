import signal

from pgnotify import await_pg_notifications, get_dbapi_connection

CONNECT = "postgresql:///example"
e = get_dbapi_connection(CONNECT)


SIGNALS_TO_HANDLE = [signal.SIGINT, signal.SIGTERM]

for n in await_pg_notifications(
    e,
    ["hello", "hello2"],
    timeout=10,
    yield_on_timeout=True,
    handle_signals=SIGNALS_TO_HANDLE,
):
    if isinstance(n, int):
        sig = signal.Signals(n)
        if n in SIGNALS_TO_HANDLE:
            print(f"handling {sig.name}")
        print("interrupted, stopping")
        break

    elif n is None:
        print("timeout, continuing")

    else:
        print((n.pid, n.channel, n.payload))
