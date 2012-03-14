"""Integrate the shelve module with flask."""
import os
import shelve
import fcntl

import flask
from flask import _request_ctx_stack


def init_app(app):
    """Initialize the flask app.

    Before calling this function, the `SHELVE_FILENAME` config
    value must be set, e.g.::

        app.config['SHELVE_FILENAME'] = 'my_db_file'

    This function will associate an object with the current flask
    app, which is accessible using the ``get_shelve`` function.

    """
    if 'SHELVE_FILENAME' not in app.config:
        raise RuntimeError("SHELVE_FILENAME is required in the "
                           "app configuration.")
    app.config.setdefault('SHELVE_PROTOCOL', None)
    app.config.setdefault('SHELVE_WRITEBACK', False)
    app.config.setdefault('SHELVE_LOCKFILE',
                          app.config['SHELVE_FILENAME'] + '.lock')
    app.extensions['shelve'] = _Shelve(app)


def get_shelve(mode='c'):
    """Get an instance of shelve.

    This function will return a ``shelve.Shelf`` instance.
    It does this by finding the shelve object associated with
    the current flask app (using ``flask.current_app``).

    """
    return flask.current_app.extensions['shelve'].open_db(mode=mode)


class _Shelve(object):
    def __init__(self, app):
        self.app = app
        self.app.teardown_request(self.close_db)
        self._lock = _FileLock(app.config['SHELVE_LOCKFILE'])
        # "touch" the db file so that view functions can
        # open the db with mode='r' and not have to worry
        # about the db not existing.
        self._open_db('c').close()

    def open_db(self, mode='r'):
        if self._is_write_mode(mode):
            fileno = self._lock._aquire_write_lock()
            writer = self._open_db(mode)
            writer.fileno = fileno
            _request_ctx_stack.top.shelve_writer = writer
            return writer
        else:
            fileno = self._lock._aquire_read_lock()
            reader = self._open_db(mode)
            reader.fileno = fileno
            _request_ctx_stack.top.shelve_reader = reader
            return reader

    def _is_write_mode(self, mode):
        return mode in ('c', 'w', 'n')

    def _open_db(self, flag):
        cfg = self.app.config
        return shelve.open(
            filename=cfg['SHELVE_FILENAME'],
            flag=flag,
            protocol=cfg['SHELVE_PROTOCOL'],
            writeback=cfg['SHELVE_WRITEBACK']
        )

    def close_db(self, ignore_arg):
        top = _request_ctx_stack.top
        if hasattr(top, 'shelve_writer'):
            writer = top.shelve_writer
            writer.close()
            self._lock._release_write_lock(writer.fileno)
        elif hasattr(top, 'shelve_reader'):
            reader = top.shelve_reader
            reader.close()
            self._lock._release_read_lock(reader.fileno)


class _FileLock(object):
    def __init__(self, lockfile):
        self._filename = lockfile
        # Touch the file so we can aquire read locks.
        open(self._filename, 'w').close()

    def _aquire_read_lock(self):
        fileno = os.open(self._filename, os.O_RDWR)
        fcntl.flock(fileno, fcntl.LOCK_SH)
        return fileno

    def _aquire_write_lock(self):
        fileno = os.open(self._filename, os.O_RDWR)
        fcntl.flock(fileno, fcntl.LOCK_EX)
        return fileno

    def _release_read_lock(self, fileno):
        fcntl.flock(fileno, fcntl.LOCK_UN)
        os.close(fileno)

    def _release_write_lock(self, fileno):
        fcntl.flock(fileno, fcntl.LOCK_UN)
        os.close(fileno)
