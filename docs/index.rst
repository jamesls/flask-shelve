.. Flask-Shelve documentation master file, created by
   sphinx-quickstart on Tue Mar 13 12:54:20 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Flask-Shelve
============

.. module:: Flask-Shelve

The **Flask-Shelve** extension integrates the `shelve`_ module with `Flask`_,
which provides basic key value storage to views::

    import flask
    from flask.ext import shelve

    app = flask.Flask(__name__)
    app.config['SHELVE_FILENAME'] = 'shelve.db'
    shelve.init_app(app)

    @app.route('/')
    def index():
        db = shelve.get_shelve('c')
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


Using Flask-Shelve
------------------

To enable the **Flask-Shelve** extension, use the ``init_app`` function::

    import flask
    from flask.ext.shelve import init_app

    app = flask.Flask(__name__)
    app.config['SHELVE_FILENAME'] = 'shelve.db'
    init_app(app)


In a view function, you can invoke the :func:`get_shelve` function, with a
mode argument of 'c', 'n', 'w', or 'r'.  The returned value is a
:func:`shelve.Shelf` instance, which exposes a dict like interface::


    from flask.ext.shelve import get_shelve, init_app
    from myapp import app

    init_app(app)

    @app.route('/')
    def index():
        db = get_shelve('c')
        db['foo'] = 'bar'
        return str(db['other_key'])

    if __name__ == '__main__':
        app.run()


The view function does not need to worry about aquiring/releasing read/write
locks, nor does it need to worry about closing the shelve instance,
**Flask-Shelve** takes care of this for you.


Concurrency
-----------

**Flask-Shelve** does not rely on any locking mechanism provided by the
underlying dbm, instead it implements its own locking:

* There can be any number of readers at any time provided that no one has
  the shelve db opened for write ('c', 'n', or 'w').
* In order to write to the db, all read locks must be released, and there
  can't be anyone else writing to the db.

In practice, this means that any thread or process has a view function
that has called ``shelve.get_db`` with a mode of 'c', 'n', or 'w' will block
until all views that have the db currently opened return.
Note that this is across **all threads and processes for any given shelve file.**

Performance
-----------

Performance is terrible, mostly due to the locking needed for concurrent access
discussed above.  This may change in the future, but there are much better
options if you need something with higher performance (a separate server
running a SQL/NoSQL db).  The main reasons for using this extension are:

* **Simplicity** -  All your data is stored locally using the familiar shelve module.
* **Minimal configuration** - No external server configuration is needed, and the
  only app configuration needed is ``SHELVE_FILENAME``.


.. _Flask: http://flask.pocoo.org
.. _shelve.open: http://docs.python.org/library/shelve.html#shelve.open
.. _shelve: http://docs.python.org/library/shelve.html
