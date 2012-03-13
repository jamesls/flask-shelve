#!/usr/bin/env python
from __future__ import with_statement

import os
import unittest
import shelve
import tempfile

import flask
from flask_shelve import init_app, get_shelve


class TestFlaskShelve(unittest.TestCase):
    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile()
        # shelve (anydbm) won't work with empty files.
        os.unlink(self.tempfile.name)

        app = flask.Flask('test-flask-shelve')
        app.debug = True
        app.config['SHELVE_FILENAME'] = self.tempfile.name

        @app.route('/setkey/', methods=['POST'])
        def setkey():
            db = get_shelve()
            db['foo'] = 'bar'
            return db['foo']

        @app.route('/getkey/')
        def getkey():
            db = get_shelve('r')
            return db.get('foo', 'NOEXIST')

        init_app(app)
        self.app = app

    def get_db(self, mode='r'):
        return shelve.open(self.tempfile.name, mode)

    def tearDown(self):
        try:
            self.tempfile.close()
        except OSError:
            pass

    def test_set_value_in_shelve(self):
        with self.app.test_client() as c:
            rv = c.post('/setkey/')
        self.assertEqual(rv.status_code, 200)
        db = self.get_db()
        self.assertEqual(db['foo'], 'bar')

    def test_multiple_readers_in_a_request(self):
        self.get_db('c')['foo'] = 'not bar'
        with self.app.test_client() as c:
            r1 = c.get('/getkey/')
            r2 = c.get('/getkey/')
        self.assertEqual(r1.data, 'not bar')
        self.assertEqual(r2.data, 'not bar')
        with self.app.test_client() as c:
            r3 = c.post('/setkey/')
        self.assertEqual(r3.data, 'bar')

    def test_db_file_does_not_have_to_exist(self):
        with self.app.test_client() as c:
            r1 = c.get('/getkey/')
        self.assertEqual(r1.data, 'NOEXIST')

    def test_shelve_filename_required(self):
        app = flask.Flask('missing-shelve-filename')
        self.assertRaises(RuntimeError, init_app, app)

    def test_default_config_values(self):
        app = flask.Flask('missing-shelve-filename')
        app.config['SHELVE_FILENAME'] = 'shelve_filename'
        init_app(app)
        cfg = app.config
        self.assertEqual(cfg['SHELVE_PROTOCOL'], None)
        self.assertEqual(cfg['SHELVE_WRITEBACK'], False)
        self.assertEqual(cfg['SHELVE_LOCKFILE'], 'shelve_filename.lock')


if __name__ == '__main__':
    unittest.main()
