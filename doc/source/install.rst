How to install?
===============

Requirements
------------

The code is tested with python 3.4.

Po4a is an optional requirement (see below).

Package manager
---------------

* [Archlinux](https://aur.archlinux.org/packages/scifig/)

PyPI
----

`See Pypi <http://pypi.python.org/pypi/scifig/>`_

To install with pip:

.. code-block:: sh

    pip install scifig


Manual installation
-------------------

From sources

.. code-block:: sh

    python setup.py install


Files for po4a for translations (i18n)
-------------------------------------

Po4a part (optional)

According to your distribution, move pm files
located in po4a/ to

* /usr/share/perl5/vendor_perl/Locale/Po4a
* or /usr/share/perl5/Locale/Po4a (debian)

