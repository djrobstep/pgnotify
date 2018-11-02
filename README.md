# pgnotify: Easily LISTEN to PostgreSQL NOTIFY notifications

LISTEN to and process NOTIFY events with a simple `for` loop, like so:

    from pgnotify import await_pg_notifications

    for notification in await_pg_notifications(
            'postgresql:///nameofdatabase',
            ['channel1', 'channel2']):

        print(notification.channel)
        print(notification.payload)

You can also handle timeouts and signals, as in this more fully-fleshed example:

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
          # when n is an integer, a signal has been has been caught for further handling.
          if isinstance(n, int):
              sig = signal.Signals(n)
              if n in SIGNALS_TO_HANDLE:
                  print(f"handling {sig.name}")
              print("interrupted, stopping")
              break

          # if `yield_on_timeout` has been set to True, the loop returns None after the timeout has been reached
          elif n is None:
              print("timeout, continuing")

          # handle the actual notify occurrences here
          else:
              print((n.pid, n.channel, n.payload))

Further documentation to come.
