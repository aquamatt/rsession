import logging
from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase, CreateError
from django.utils.encoding import force_unicode

from redis import Redis

KEY_PREFIX = "%s:%%s" % settings.RSESSION.get("PREFIX", "RSESSION")

logger = logging.getLogger("rsession")

class SessionStore(SessionBase):
    """
    Implements database session store.
    """
    def __init__(self, session_key=None):
        super(SessionStore, self).__init__(session_key)
        self.db = Redis(
            settings.RSESSION.get('HOST', 'localhost'),
            settings.RSESSION.get('PORT', 6379),
            settings.RSESSION.get('DB', 0),
            settings.RSESSION.get('PASSWORD', ''),
        )

    def load(self):
        logger.debug("RSession loading session {}".format(self.session_key))
        session_data = self.db.get(self.session_key)
        if session_data is None:
            self.create()
            return {}
        return self.decode(force_unicode(session_data))

    def exists(self, session_key):
        logger.debug("RSession testing existence of session {}".format(session_key))
        if self.db.exists(session_key):
            return True
        return False

    def _make_key(self):
        return KEY_PREFIX % self._get_new_session_key()

    def create(self):
        while True:
            self._session_key = self._make_key()
            setter_fn = self._redis_method(True)
            # Save immediately to ensure we have a unique entry in the
            # database.
            result = setter_fn(self.session_key, 
                               self.encode(self._get_session(no_load=True)))

            if result is False:
                continue

            self.db.expire(self.session_key, self.get_expiry_age())

            self.modified = True
            self._session_cache = {}
            return

    def _redis_method(self, must_create=False):
        """
        Return the redis method to use to save the key
        """
        setter_fn = self.db.setnx if must_create else self.db.set
        return setter_fn

    def save(self, must_create=False):
        """
        Saves the current session data to the database. If 'must_create' is
        True, a database error will be raised if the saving operation doesn't
        create a *new* entry (as opposed to possibly updating an existing
        entry).
        """
        if must_create:
            if self.exists(self.session_key):
                raise CreateError
            self.create()

        if self.session_key is None:
            self.create()

        setter_fn = self._redis_method(must_create)
        key = self.session_key
        logger.debug("RSession saving session {}".format(key))
        result = setter_fn(key,
                           self.encode(self._get_session(no_load=must_create)))

        if must_create and result is False:
            raise CreateError

        self.db.expire(key, self.get_expiry_age())

    def delete(self, session_key=None):
        if session_key is None:
            if self._session_key is None:
                return
            session_key = self._session_key

        self.db.delete(KEY_PREFIX % session_key)


# At bottom to avoid circular import
from django.contrib.sessions.models import Session
