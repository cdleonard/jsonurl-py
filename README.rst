JSON->URL PYthon implementation
===============================

.. image:: https://img.shields.io/github/license/cdleonard/jsonurl-py.svg
   :target: https://github.com/cdleonard/jsonurl-py/blob/master/LICENSE

.. image:: https://img.shields.io/pypi/v/jsonurl-py.svg
   :target: https://pypi.org/project/jsonurl-py/

.. image:: https://github.com/cdleonard/jsonurl-py/actions/workflows/main.yml/badge.svg
    :target: https://github.com/cdleonard/jsonurl-py/actions

.. image:: https://cdleonard.github.io/jsonurl-py/htmlcov/badge.svg
    :target: https://cdleonard.github.io/jsonurl-py/htmlcov/

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

About
-----

This is a python implementation of jsonurl, an alternative text format which
encodes the same data model in a way that is more suitable for use in URLs.

See https://jsonurl.org/ and especially https://github.com/jsonurl/specification/

The following optional features are supported:

* `2.9.1 <https://github.com/jsonurl/specification/#291-implied-arrays>`_ Implied Arrays
* `2.9.2 <https://github.com/jsonurl/specification/#292-implied-objects>`_ Implied Objects
* `2.9.5 <https://github.com/jsonurl/specification/#295-empty-objects-and-arrays>`_ Distinction between empty object and array
* `2.9.6 <https://github.com/jsonurl/specification/#296-address-bar-query-string-friendly>`_ AQF - Address Bar Query String Friendly

The following optional features are not yet supported:

* `2.9.3 <https://github.com/jsonurl/specification/#293-x-www-form-urlencoded-arrays-and-objects>`_ WFU - x-www-form-urlencoded Arrays and Objects
* `2.9.4 <https://github.com/jsonurl/specification/#294-implied-object-missing-values>`_ Implied Object Missing Values

Installation
------------
::

    pip install jsonurl-py

The package name is jsonurl_py to avoid confusion with an `unrelated jsonurl
package <https://pypi.org/project/jsonurl/>`_ on pypi which implements an
unrelated syntax. In theory you can install and import both packages without
having them interfere with each other.

The project name uses a dash in the name for consistency with the existing
`jsonurl-js <https://github.com/jsonurl/jsonurl-js>`_ and `jsonurl-java
<https://github.com/jsonurl/jsonurl-java>`_ implementations.

Usage
-----
::

    import jsonurl_py as jsonurl

    assert jsonurl.loads('(a:1,b:c)') == {'a': 1, 'b': 'c'}
    assert jsonurl.dumps(dict(a=[1,2])) == '(a:(1,2))'

Command Line Interface
----------------------

The package includes a command line interface for converting between jsonurl and
standard json::

    $ echo "(a:b)" | jsonurl-py load
    {"a": "b"}
    $ echo '{"a":"b"}' | jsonurl-py dump
    (a:b)

It is also possible to run the executable directly via pipx::

    $ echo '(a:b)' | pipx run jsonurl-py load
    {"a": "b"}

Documentation
-------------

Published on `github pages <https://cdleonard.github.io/jsonurl-py/docs/>`__.

Can be built locally using ``tox -e docs``

Testing
-------

Tests run via github actions.

Code coverage for main branch is published on `github pages <https://cdleonard.github.io/jsonurl-py/htmlcov/>`__.
