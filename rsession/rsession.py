from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase, CreateError
from django.utils.encoding import force_unicode

from redis import Redis

KEY_PREFIX = "%s:%%s" % settings.RSESSION.get("PREFIX", "RSESSION")


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
        session_data = self.db.get(KEY_PREFIX % self.session_key)
        if session_data is None:
            self.create()
            return {}
        return self.decode(force_unicode(session_data))

    def exists(self, session_key):
        if self.db.exists(KEY_PREFIX % session_key):
            return True
        return False

    def create(self):
        while True:
            self._session_key = self._get_new_session_key()
            try:
                # Save immediately to ensure we have a unique entry in the
                # database.
                self.save(must_create=True)
            except CreateError:
                # Key wasn't unique. Try again.
                continue
            self.modified = True
            self._session_cache = {}
            return

    def save(self, must_create=False):
        """
        Saves the current session data to the database. If 'must_create' is
        True, a database error will be raised if the saving operation doesn't
        create a *new* entry (as opposed to possibly updating an existing
        entry).
        """
        if must_create and self.exists(self.session_key):
            raise CreateError

        setter_fn = self.db.setnx if must_create else self.db.set

        key = KEY_PREFIX % self.session_key
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
