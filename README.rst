rsession
========

rsession is yet another Redis-backed Django session store.

There are a few available within a short Google but it was
not clear which should be used and differences between them
made me decide to roll my own.

This session store is a copy of Django's own database
session store with each method modified to suit Redis.

Installation of rsession is easily accomplished with pip::

    $ pip install rsession

To use, install Redis and amend your Django settings as follows, substituting 
appropriate values if your Redis server is not a default installation 
on localhost::

    RSESSION = {
        'HOST'     : 'localhost',
        'PORT'     : 6379,
        'DB'       : 0,
        'PASSWORD' : '',
        'PREFIX'   : 'RSESSION',
    }

    SESSION_ENGINE = "rsession.rsession"
    # 14 days is default expiry for Django. Setting included
    # here to remind the user that the session length is modifiable
    # and probably should be for your application
    SESSION_COOKIE_AGE = 60 * 60 * 24 * 14 # 14 days in seconds
    SESSION_SAVE_EVERY_REQUEST = True
    SESSION_EXPIRE_AT_BROWSER_CLOSE = False

Finally, whilst not essential, you can remove ``django.contrib.sessions`` from 
your installed apps as this is only required if using
Django database-backed sessions.

Your work is now done. Django sessions will be stored in Redis under the key
``RSESSION:<session key>`` (unless you change the prefix in settings as above) 
and these will be purged ``SESSION_COOKIE_AGE`` seconds after the last use.

If you have comments and would like to get in touch, please mail
rsession at zorinholdings.com

Matthew
May 2011

