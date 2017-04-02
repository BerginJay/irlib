[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.439723.svg)](https://doi.org/10.5281/zenodo.439723)

*Radar Tools* is a library and set of tools useful for visualizing and
processing data collected from ice-penetrating radar. The tools have been
designed to work the HDF5 datasets generated by [Blue
System](http://www.radar.bluesystem.ca/) IceRadar.

There are two primary ways of using *Radar Tools*. The first is to use the
command-line and graphical tools, listed below. These tools provide an
efficient and simple way to apply established methodologies for analysing radar
data. Pre-written filters and processing routines are called by typing
commands.

![](http://njwilson23.github.com/radar_tools/images/repo_image.png)

The second way is to use the ``irlib`` package through custom Python scripts.
This makes it possible to programmatically analyze radar data. New filters and
processing routines can be implemented using the API.

There is experimental support for reading other types of datasets using *Radar
Tools*. Right now, it's possible to read CReSIS and pulseEKKO PRO lines, making
the filters in ``irlib`` available. Helper functions to load CReSIS \*.mat files
and pulseEKKO PRO \*.HD and \*.DT1 files are in ``itools.py``

Graphical tools:
----------------

- **icepick2**: View radar lines directly and experiment interactively with
  processing filters. Pick reflection arrivals from a radar line, either
  manually or with simple pattern recognition

- **icerate**: Rate reflection quality using **icepick** output

- **irview**: General purpose viewer for radar lines that doubles as a tool for
  marking englacial regions **[DEPRECATED IN FAVOUR OF icepick2]**

Command-line tools:
-------------------

- **h5_dumpmeta**: Dump metadata from an HDF5 survey into a CSV file
- **h5_add_utm**: Add UTM coordinates to an HDF5 survey file (requires
  [**pyproj**](http://code.google.com/p/pyproj/))
- **h5_replace_gps**: Replace the coordinates in an HDF5 survey with those from
  a GPS eXchange (GPX) file
- **h5_generate_cache**: Generate caches to speed loading radar lines
- **h52a**: Export a line from an HDF5 file to ASCII or binary
- **irtrace**: Plot a radar trace acquired at a single location
- **irline**: Plot a radar section along a line of locations

Dependencies:
-------------

*Radar Tools* should run anywhere Python and the necessary dependencies work. In
the past, I've managed to get it running under Windows, OS X, and Linux without
trouble.

1. [*Python*](http://www.python.org) 2.6+ (3.x works for the irlib package and
   icepick2)

2. [*Numpy*](http://www.numpy.org) numerical array classes for Python

2. [*Scipy*](http://www.scipy.org) science-oriented libraries for Python

2. [*h5py*](http://www.h5py.org): HDF5 interface for Python

2. [*matplotlib*](http://www.matplotlib.org) plotting for Python

2. [*pyproj*](https://github.com/jswhit/pyproj) _libproj_ bindings

2. [*six*](https://pythonhosted.org/six) compatibility library for Python 2/3

If you do not already have a scientific Python environment and you do not know
how to set one up, I recommend the [Anaconda Python
distribution](https://www.continuum.io/downloads).

Additional useful packages and tools:
-------------------------------------

1. [*Cython*](http://www.cython.org) for generating accelerated filters

2. *pywavelet* wrapper for wavelet algorithms (*Torrence and Compo, 1998*)
(included in `external/pywavelet-0.1`)

Installation
------------

I recommend installing with `pip`. Download or clone this repository, navigate
to it in a terminal, and type

    pip install .

Documentation:
--------------

In addition to the basic information here, documentation can be found in `doc`.
In order to build the documentation, [Sphinx](http://sphinx-doc.org/) must be
installed, with the ``numpydoc`` extension. The extensions may be installed by

    pip install numpydoc

or

    conda install numpydoc

Then, from the ``doc/`` directory, type

    make html

If LaTeX is available, the documentation can be compiled into a PDF. Type

    make latexpdf

A copy can be found [here](https://dl.dropboxusercontent.com/u/375008/irlib_manual.pdf).

Changes in irlib version 0.4-dev
--------------------------------

*irlib* 0.4 represents significant refactoring and cleaning of both the library
and application design. Breaking changes in the final version will be kept to a
minimum, however the *stable-0.3* branch is available if necessary.

- remove deprecated `CutSingle`, `CutRegion` methods
- refactor pickable gathers into separate subclasses
- map window
- refactor icepick, irview, icerate into a single codebase, kept in `irlib/app/`
  (all except icerate)
- build *icepick2* based on the refactored `app` codebase
- modular command system, one of the benefits of which is that additional custom
  filters can be added easily at runtime and on a project-basis
- rewrite ``h5_replace_gps`` to be more robust, handle timezones, and work over
  multiple days
- some bug fixes and polishing
- Python 3 compatibility (WIP: tests pass, basic icepick2 use)
- project config file (not complete)
- composable line gathers and surveys by overloading arithmetic operators?
- HDF file write?
- PulseEkko data reader?

License:
--------

*Radar Tools* is provided "as is," without any warranty. Some parts of
*Radar Tools* are affected by different licensing terms. See `license.txt` for
detailed information.

