Flask-Shelve
------------

A flask extension that integrates the shelve module with flask.

View the docs at: http://packages.python.org/Flask-Shelve/


Running the Tests
~~~~~~~~~~~~~~~~~

The tests can be run using:

    python setup.py test


The repo also contains a scripts directory that has
a ``threadtest.py`` that can be run to verify the
locking behavior of Flask-Shelve::

    scripts/threadtest.py
