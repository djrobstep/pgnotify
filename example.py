from sqlalchemy import create_engine

from pgnotify import await_pg_notifications

CONNECT = "postgresql:///example"
CONNECT = create_engine(CONNECT)

for n in await_pg_notifications(
    CONNECT,
    ["hello", "hello2"],
    timeout=1,
    yield_on_timeout=True,
    handle_keyboardinterrupt=True,
):

    if n is False:
        print("interrupted, stopping")
        break

    elif n is None:
        print("timeout, continuing")

    else:
        print((n.pid, n.channel, n.payload))
