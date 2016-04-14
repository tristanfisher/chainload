chainload
=========

Load a value from an environmental variable, YAML/JSON file, or default to a provided value.


|TravisBadge|_

.. |TravisBadge| image:: https://travis-ci.org/tristanfisher/chainload.svg?branch=master
.. _TravisBadge: https://travis-ci.org/tristanfisher/chainload


Getting chainload
-----------------

Simply:

.. code-block:: bash

    pip install chainload


Install requirements
--------------------

.. code-block:: bash

    pip install -r requirements.txt

or:

.. code-block:: bash

    python setup.py install


Using chainload
---------------

If you have variables that exist in a file, I recommend assigning a file object to a variable, then passing that variable to the chain loading method.

e.g.

.. code-block:: python

    $ python
    >>> from chainload import chainload
    >>> variable_file = chainload.load_file(file_name="tests/test_settings.yaml")
    >>> chainload.chain_load_variable("environment", "environment", "debug", variable_file)
    'production'

or, if you have a lot of variables to load, use the class-based approach:

.. code-block:: python

    $ python
    >>> chainer = chainload.ChainloadSetup(filename="tests/test_settings.yaml", environment_variable_prefix="webapp_")
    >>> environment_value = chainer("environment")

the latter has the advantage of being far more `DRY <http://stackoverflow.com/questions/6453235/what-does-damp-not-dry-mean-when-talking-about-unit-tests>`_ for larger use-cases.


See the docstring for `chain_load_variable`, but this will load a variable in order of:


1. A default value

2. From file object

3. From an environment variable.  
   
   Optional: If the environmental variable is None, and the specified file option name exists in the env, and this behavior is enabled, an attempt to load from an environmental variable of the same name as specified for #2


Running tests
-------------

If you want to run the tests for this package:

.. code-block:: bash

    $ make test
    python setup.py test
    running nosetests
    running egg_info
    writing chainload.egg-info/PKG-INFO
    writing top-level names to chainload.egg-info/top_level.txt
    writing dependency_links to chainload.egg-info/dependency_links.txt
    reading manifest file 'chainload.egg-info/SOURCES.txt'
    writing manifest file 'chainload.egg-info/SOURCES.txt'
    .........
    ----------------------------------------------------------------------
    Ran 9 tests in 0.007s


Filing bugs / issues
--------------------

When filing a bug report, please include a `Short, Self Contained, Correct (Compilable), Example <http://sscce.org/>`_.


New features / Pull requests
----------------------------

If requesting a new feature, please include a well-explained use-case with example usage.

When making a pull request, if new functionality is added, please include appropriate tests.
