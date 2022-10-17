JSON->URL PYthon implementation
===============================

About
-----

This is a python implementation of jsonurl, an alternative text format which
encodes the same data model in a way that is more suitable for use in URLs.

See https://jsonurl.org/

This is an incomplete implementation.

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
