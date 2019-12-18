.. image:: doc/manuals/_images/DIVA_Final_Logo_72dpi.png
   :alt: DIVA

Deep Intermodal Video Analytics (DIVA) Framework
================================================

The DIVA Framework is a software framework designed to provide an architecutre and a set of software modules
which will facilitate the development of DIVA analytics.
From the `DIVA Website <https://www.iarpa.gov/index.php/research-programs/diva>`_:

  	The DIVA program seeks to develop robust automatic activity detection for a
	multi-camera streaming video environment. Activities will be enriched by person
	and object detection. DIVA will address activity detection for both forensic
	applications and for real-time alerting.

Resources
---------

* `DIVA Framework Github Repository <https://github.com/Kitware/DIVA>`_ This is the main DIVA Framework site, all development of the framework happens here.
* `DIVA Framework Issue Tracker <https://github.com/Kitware/DIVA/issues>`_  Submit any bug reports or feature requests for the framework here.
* `DIVA Framework Main Documentation Page <https://kwiver-diva.readthedocs.io/en/latest/>`_ The source for the framework documentation is maintained in the Github repository using `Sphinx <http://www.sphinx-doc.org/en/master/>`_  A built version is maintained on `ReadTheDocs <https://readthedocs.org/>`_.   A good place to get started in the documentation, after reading the `Introduction <https://kwiver-diva.readthedocs.io/en/latest/introduction.html>`_ is the `UseCase <https://kwiver-diva.readthedocs.io/en/latest/usecases.html>`_ section which will walk you though a number of typical use cases with the framework.
* KITWARE has implemented two "baseline" activity recognition algorithms in terms of the Framework:

  + `R-C3D <https://gitlab.kitware.com/kwiver/R-C3D/tree/kitware/master>`_
  + `ACT <https://gitlab.kitware.com/kwiver/act_detector/tree/kitware/master>`_

DIVA Docker Image
=================

Kitware maintains a `Docker <https://www.docker.com/>`_ image with DIVA prebuilt.
The Dockerfile used to build the image can be found `here <Dockerfile>`_.

Pull the image from Dockerhub::

 docker pull kitware/diva:latest

(`https://hub.docker.com/r/kitware/diva <https://hub.docker.com/r/kitware/diva>`_)

or build the DIVA image using the dockerfile::

 docker build -t diva:tagname .

DIVA Python wheel
=================

Kitware also provides a pared down DIVA build as a Python 3 wheel.  The DIVA wheel depends on the Kwiver wheel, and the following system dependencies (installed via apt-get in this example)::

  # The following example uses the Ubuntu apt-get package manager
  # These command may differ depending on your Linux flavor and package manager
  sudo apt-get install libgl1-mesa-dev libexpat1-dev libgtk2.0-dev liblapack-dev python3.6 python3-pip

Upgrade PIP if older than version 19.3.1::
  
  pip3 install -U pip

Install the wheels::

  pip install kwiver diva-framework

Verify the installation::

  plugin_explorer --proc diva

The plugin `diva_experiment` should be listed in the output.

Building DIVA
=============

Dependencies
------------
DIVA requires, at a minimum, `Git <https://git-scm.com/>`_, `CMake <https://cmake.org/>`_, a C++ compiler, and a `Python 2.7 environment <https://python.org>`_.

The DIVA Framework repository is structured as a CMake "super-build" which fetches, configures
and builds both KWIVER and Fletch along with the DIVA Framework specific code.  While most of the framework's dependencies are carried by Fletch, there may be some preparation of your development
system required before you can successfully build the framework.

On Ubuntu systems, for example you'll want to make sure the following packages are installed on your system:

.. code-block :: bash

 # The following example uses the Ubuntu apt-get package manager
 # These command may differ depending on your Linux flavor and package manager
 sudo apt-get install build-essential libgl1-mesa-dev
 sudo apt-get install libexpat1-dev
 sudo apt-get install libgtk2.0-dev
 sudo apt-get install liblapack-dev
 sudo apt-get install python2.7-dev

Running CMake
-------------

We recommend building DIVA out of its source directory to prevent mixing
source files with compiled products.  Create a build directory in parallel
with the DIVA source directory for each desired configuration. For example :

========================== ===================================================================
``\DIVA\src``               contains the code from the git repository
``\DIVA\build\release``     contains the built files for the release configuration
``\DIVA\build\debug``       contains the built files for the debug configuration
========================== ===================================================================

Basic CMake generation via command line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following example will pull and build Fletch and KWIVER along with the DIVA code base.
It assumes that you are ``\DIVA\build\release`` directory.  What follows are the commands
to configure and build the DIVA framework in several common configurations:


To build a "release" version of DIVA::

    $ cmake ../../src -DCMAKE_BUILD_TYPE=Release
    $ make -j 4

.. Note::
   The `-j 4` argument starts a build process with 4 threads.  You'll want to choose a value consistent with the number of cores you have,
   typically one or two more if you have a dedicated machine

To build with CUDA enabled::

    $ cmake ../../src -DCMAKE_BUILD_TYPE=Release -DDIVA_BUILD_WITH_CUDA=ON
    $ make -j 4

To build with CUDNN enabled::

    $ cmake ../../src -DCMAKE_BUILD_TYPE=Release -DDIVA_BUILD_WITH_CUDA=ON -DDIVA_BUILD_WITH_CUDNN=ON
    $ make -j 4

.. Note::
   If your CUDA and or CUDNN installations are not in the default location, you may need to specifiy their
   location with the CUDA_TOOLKIT_ROOT_DIR and CUDNN_TOOLKIT_ROOT_DIR variables

Next Steps
==========

For more details on building and using the DIVA framework, please see the
`DIVA Framework Documentation <https://kwiver-diva.readthedocs.io/en/latest/introduction.html>`_

For general build or code issues, please join the `kwiver-users
<http://public.kitware.com/mailman/listinfo/kwiver-users>`_ mailing list. For discussions of the DIVA API, please contact diva-te <at> kitware.com to join the diva-API mailing list.

For announcements about KWIVER in general, please join the
`kwiver-announce <http://public.kitware.com/mailman/listinfo/kwiver-announce>`_
mailing list.
