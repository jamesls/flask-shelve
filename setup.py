"""
Flask-Shelve
------------

Integrate the shelve module with flask.

Links
`````

* `documentation <http://packages.python.org/Flask-Shelve/>`_

"""

from setuptools import setup


setup(
    name='Flask-Shelve',
    version='0.1',
    url='https://github.com/jamesls/flask-shelve',
    license='BSD',
    author='James Saryerwinnie',
    author_email='jls.npi@gmail.com',
    maintainer='James Saryerwinnie',
    maintainer_email='jls.npi@gmail.com',
    description='Shelve support for Flask',
    long_description=__doc__,
    py_modules=['flask_shelve'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
    ],
    test_suite='tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
