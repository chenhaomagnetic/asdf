ASDF - Advanced Scientific Data Format
======================================

[![Build Status](https://travis-ci.org/spacetelescope/asdf.svg?branch=master)](https://travis-ci.org/spacetelescope/asdf)
[![Build status](https://ci.appveyor.com/api/projects/status/s1jtd9np3catfr1c?svg=true)](https://ci.appveyor.com/project/spacetelescope/asdf)
[![Documentation Status](https://readthedocs.org/projects/asdf/badge/?version=latest)](http://asdf.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/spacetelescope/asdf/badge.svg?branch=master)](https://coveralls.io/github/spacetelescope/asdf?branch=master)
[![stsci](https://img.shields.io/badge/powered%20by-STScI-blue.svg?colorA=707170&colorB=3e8ddd&style=flat)](http://www.stsci.edu)
[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)

![STScI Logo](docs/_static/stsci_logo.png)


The **A**dvanced **S**cientific **D**ata **F**ormat (ASDF) is a next-generation
interchange format for scientific data. This package contains the Python
implementation of the ASDF Standard. More information on the ASDF Standard
itself can be found [here](https://asdf-standard.readthedocs.io).

The ASDF format has the following features:
* A hierarchical, human-readable metadata format (implemented using [YAML](http://yaml.org))
* Numerical arrays are stored as binary data blocks which can be memory mapped. Data blocks can optionally be compressed.
* The structure of the data can be automatically validated using schemas (implemented using [JSON Schema](http://json-schema.org))
* Native Python data types (numerical types, strings, dicts, lists) are serialized automatically
* ASDF can be extended to serialize custom data types

ASDF is under active development [on
github](https://github.com/spacetelescope/asdf). More information on
contributing can be found [below](#contributing).

## Overview

This section outlines basic use cases of the ASDF package for creating and reading ASDF files.

### Creating a file

We're going to store several `numpy` arrays and
other data to an ASDF file. We do this by creating a "tree", which
is simply a Python dictionary, and using it to create an `AsdfFile` object:

```python
import asdf
import numpy as np

# Create some data
sequence = np.array([x for x in range(100)])
squares = np.array([x**2 for x in range(100)])
random = np.random.random(100)

# Store the data in an arbitrarily nested dictionary
tree = {
    'foo': 42,
    'name': 'Monty',
    'sequence': sequence,
    'powers': { 'squares' : squares },
    'random': random
}

# Create the ASDF file object from our data tree
af = asdf.AsdfFile(tree)

# Write the data to a new file
af.write_to('example.asdf')
```

If we open the newly created file, we can see some of the key features of ASDF on display:

```
#ASDF 1.0.0
#ASDF_STANDARD 1.2.0
%YAML 1.1
%TAG ! tag:stsci.edu:asdf/
--- !core/asdf-1.0.0
asdf_library: !core/software-1.0.0 {author: Space Telescope Science Institute, homepage: 'http://github.com/spacetelescope/asdf',
  name: asdf, version: 1.3.1}
foo: 42
name: Monty
powers:
  squares: !core/ndarray-1.0.0
    source: 1
    datatype: int64
    byteorder: little
    shape: [100]
random: !core/ndarray-1.0.0
  source: 2
  datatype: float64
  byteorder: little
  shape: [100]
sequence: !core/ndarray-1.0.0
  source: 0
  datatype: int64
  byteorder: little
  shape: [100]
...
```

The metadata in the file mirrors the structure of the tree that was stored. It is hierarchical and human-readable. Notice that `asdf` has added metadata to the tree that was not explicitly given by the user. Notice also that the numerical array data is not stored in the metadata tree itself. Instead, it is stored as binary data blocks below the metadata section (not shown here).

It is possible to compress the array data when writing the file:

```Python
af.write_to('compressed.asdf', all_array_storage='zlib')
```
Available compression algorithms are `'zlib'`, `'bzp2'`, and `'lz4'`.

### Reading a file

To read an existing ASDF file, we simply use the top-level `open` function of the `asdf` package:

```python
import asdf

af = asdf.open('example.asdf')
```

The `open` function also works as a context handler:

```python
with asdf.open('example.asdf') as af:
    ...
```

To access the data stored in the file, use the top-level `tree` attribute:

```python
>>> import asdf
>>> af = asdf.open('example.asdf')
>>> af.tree
{'asdf_library': {'author': 'Space Telescope Science Institute',
  'homepage': 'http://github.com/spacetelescope/asdf',
  'name': 'asdf',
  'version': '1.3.1'},
 'foo': 42,
 'name': 'Monty',
 'powers': {'squares': <array (unloaded) shape: [100] dtype: int64>},
 'random': <array (unloaded) shape: [100] dtype: float64>,
 'sequence': <array (unloaded) shape: [100] dtype: int64>}
```

The tree is simply a Python dictionary, and nodes are accessed like any other dictionary entry:

```Python
>>> af.tree['name']
'Monty'
>>> af.tree['powers']
{'squares': <array (unloaded) shape: [100] dtype: int64>}
```

Array data remains unloaded until it is explicitly accessed:

```python
>>> af.tree['powers']['squares']
array([   0,    1,    4,    9,   16,   25,   36,   49,   64,   81,  100,
        121,  144,  169,  196,  225,  256,  289,  324,  361,  400,  441,
        484,  529,  576,  625,  676,  729,  784,  841,  900,  961, 1024,
       1089, 1156, 1225, 1296, 1369, 1444, 1521, 1600, 1681, 1764, 1849,
       1936, 2025, 2116, 2209, 2304, 2401, 2500, 2601, 2704, 2809, 2916,
       3025, 3136, 3249, 3364, 3481, 3600, 3721, 3844, 3969, 4096, 4225,
       4356, 4489, 4624, 4761, 4900, 5041, 5184, 5329, 5476, 5625, 5776,
       5929, 6084, 6241, 6400, 6561, 6724, 6889, 7056, 7225, 7396, 7569,
       7744, 7921, 8100, 8281, 8464, 8649, 8836, 9025, 9216, 9409, 9604,
       9801])

>>> import numpy as np
>>> expected = [x**2 for x in range(100)]
>>> np.equal(af.tree['powers']['squares'], expected).all()
True
```

By default, uncompressed data blocks are memory mapped for efficient access. Memory mapping can be disabled by using the `copy_arrays` option when reading:

```Python
af = asdf.open('example.asdf', copy_arrays=True)
```

For more information and for advanced usage examples, see the [documentation](#documentation).

### Extending ASDF

Out of the box, the `asdf` package automatically serializes and deserializes native Python types. It is possible to extend `asdf` by implementing custom tag types that correspond to custom user types. More information on extending ASDF can be found in the [official documentation](http://asdf.readthedocs.io/en/latest/asdf/extensions.html).

Installation
------------

Stable releases of the ASDF Python package are registered [at
PyPi](https://pypi.python.org/pypi/asdf). The latest stable version can be
installed using `pip`:

```
$ pip install asdf
```

The latest development version of ASDF is available from the `master` branch on
github. To clone the project:

```
$ git clone https://github.com/spacetelescope/asdf
```

To install:

```
$ cd asdf
$ python setup.py install
```

To install in [development mode](https://packaging.python.org/tutorials/distributing-packages/#working-in-development-mode):

```
$ python setup.py develop
```

Currently [Astropy](https://github.com/astropy/astropy) is a hard dependency of
the ASDF Python package. However, we hope to eliminate Astropy as a dependency
in the near future, although it will still be required for [running the test
suite](#testing).

**NOTE**: The source repository makes use of a git submodule for referencing the
schemas provided by the ASDF standard. While this submodule is automatically
initialized when installing the package (including in development mode), it may
be necessary for developers to manually update the submodule if changes are made
upstream. See the [documentation on git
submodules](https://git-scm.com/docs/git-submodule) for more information.


Testing
-------

To run the unit tests from a source checkout of the repository:

```
$ python setup.py test
```

It is also possible to run the test suite from an installed version of the
package. In a Python interpreter:

```python
import asdf
asdf.test()
```

Please note that the [astropy](https://github.com/astropy/astropy) package must
be installed to run the tests.

Documentation
-------------

More detailed documentation on this software package can be found
[here](https://asdf.readthedocs.io).

More information on the ASDF Standard itself can be found
[here](https://asdf-standard.readthedocs.io).

> If you are looking for the **A**daptable **S**eismic **D**ata **F**ormat, information can be found [here](https://seismic-data.org/).


Contributing
------------
We welcome feedback and contributions to the project. Contributions of code,
documentation, or general feedback are all appreciated. Please follow the
[contributing guidelines](CONTRIBUTING.md) to submit an issue or a pull request.

We strive to provide a welcoming community to all of our users by abiding to the
[Code of Conduct](CODE_OF_CONDUCT.md).
