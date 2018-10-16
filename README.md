# pgnotify: Easily LISTEN to PostgreSQL NOTIFY notifications

LISTEN to and process NOTIFY events with a simple for loop, like so:

    from pgnotify import await_pg_notifications

    for notification in await_pg_notifications(
            'postgresql:///nameofdatabase',
            ['nameoflisteningchannel', 'nameoflisteningchannel2']):

        print(notification.channel)
        print(notification.payload)

More docs to come.
