.. Flask-Shelve documentation master file, created by
   sphinx-quickstart on Tue Mar 13 12:54:20 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Flask-Shelve
============

.. module:: Flask-Shelve

The **Flask-Shelve** extension integrates the ``shelve`` module with `Flask`_,
which provides basic key value storage to views::

    import flask
    from flask.ext import shelve

    app = flask.Flask(__name__)
    app.config['SHELVE_FILENAME'] = 'shelve.db'
    shelve.init_app(app)

    @app.route('/')
    def index():
        db = shelve.get_db('c')
        db['foo'] = 'bar'
        return str(db['other_key'])

    if __name__ == '__main__':
        app.run()


**Flask-Shelve** automatically handles file locking for concurent access, and
allows multiple concurrent readers, and a single exclusive writer.

Installing Flask-Shelve
-----------------------

Install with **pip**::

    pip install Flask-Shelve

or download the latest version from github::

    git clone git://github.com/jamesls/flask-shelve.git
    cd flask-shelve
    python setup.py develop


Configuration
-------------

**Flask-Shelve** uses the following configuration values:

* ``SHELVE_FILENAME`` - The filename of the shelve db.  This is the value that
  is passed to `shelve.open`_.
* ``SHELVE_FLAG`` - The flag option to use with `shelve.open`_, defaults to
  ``'c'``.
* ``SHELVE_PROTOCOL`` - The protocol option to use with `shelve.open`_,
  defaults to None.
* ``SHELVE_WRITEBACK`` - The writeback option to use with `shelve.open`_,
  defaults to False.
* ``SHELVE_LOCKFILE`` - The filename of the lock file to use, defaults to
  ``SHELVE_FILENAME`` + '.lock'.

In general, you typically need to supply just the ``SHELVE_FILENAME`` option,
the remaining config options have reasonable defaults.


Concurrency
-----------

**Flask-Shelve** does not rely on any locking mechanism provided by the
underlying dbm, instead it implements its own locking:

* There can be any number of readers at any time provided that no one has
  the shelve db opened for write ('c', 'n', or 'w').
* In order to write to the db, all read locks must be released, and there
  can't be anyone else writing to the db.

In practice, this means that while any thread or process has a view function
that has called ``shelve.get_db`` with a mode of 'c', 'n', or 'w' will block
until all views that have the db opened return.  Note that this is across
**all threads and processes for any given shelve file.**


.. _Flask: http://flask.pocoo.org
.. _shelve.open: http://docs.python.org/library/shelve.html#shelve.open
