Installing DIVA
===============

Dependencies
------------
DIVA requires, at a minimum, Git, CMake, a C++ compiler, and a Python 2.7 compiler.

DIVA is built on top of the `KWIVER <https://github.com/Kitware/kwiver>`_ toolkit.
which is in turn built on the `Fletch <https://github.com/Kitware/fletch>`_ super build system.
To make it easier to build DIVA, a "super-build" is provided to build both KWIVER and Fletch.
It will pull both projects, configure them for DIVA, and build them for you.
If you wish, you may point the DIVA build to use your own builds of KWIVER or Fletch for DIVA to use.

On Linux systems, Install the following packages before building

.. code-block :: bash

 # The following example uses the Ubuntu apt-get package manager
 # These command may differ depending on your Linux flavor and package manager
 sudo apt-get install build-essential libgl1-mesa-dev
 sudo apt-get install libexpat1-dev
 sudo apt-get install libgtk2.0-dev
 sudo apt-get install liblapack-dev
 sudo apt-get install python2.7-dev

Building DIVA
-------------
Running CMake
^^^^^^^^^^^^^

You may run cmake directly from a shell or cmd window.
On unix systems, the ccmake tool allows for interactive selection of CMake options.  
Available for all platforms, the CMake GUI can set the source and build directories, options,
"Configure" and "Generate" the build files all with the click of a few button.

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
It assumes your terminal/command is working in the ``\DIVA\build\release`` directory.

.. code-block :: bash

    # cmake usage : $ cmake </path/to/diva/source> -D<flags>
    $ cmake ../../src -DCMAKE_BUILD_TYPE=Release 
    # All binary and libraries will be built into the \DIVA\build\release\install directory
    # You can change the install directory like this
    $ cmake ../../src -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/opt/kitware/DIVA
    # Note you will need to create the kitware directory in /opt/ and give yourself permissions
    #
    # If you would like to build with CUDA
    $ cmake ../../src -DCMAKE_BUILD_TYPE=Release -DDIVA_BUILD_WITH_CUDA=ON
    # You can also build with CUDNN (which requires you also build with CUDA)
    $ cmake ../../src -DCMAKE_BUILD_TYPE=Release -DDIVA_BUILD_WITH_CUDA=ON -DDIVA_BUILD_WITH_CUDNN=ON
    # Note you will need to have CUDA and CUDNN installed
    # If it is not in the expected location you will need to specify the flags
    # CUDA_TOOLKIT_ROOT_DIR and CUDNN_TOOLKIT_ROOT_DIR

Using a prebuilt Fletch
~~~~~~~~~~~~~~~~~~~~~~~

If you would like to point DIVA to a prebuilt version of Fletch, specify the fletch_DIR flag to cmake.
The fletch_DIR is the fletch build directory root, which contains the fletchConfig.cmake file.

.. code-block :: bash

    $ cmake ../../src -DCMAKE_BUILD_TYPE=Release -Dfletch_DIR:PATH=<path/to/fletch/build/dir> 

You must ensure that the specified build of Fletch has enabled all the appropriate flags for use by KWIVER and DIVA.
The required flags can be found in this file : `<CMake/add_project_fletch.cmake>`_ 

Using a prebuilt KWIVER
~~~~~~~~~~~~~~~~~~~~~~~

If you would like to point DIVA to a prebuilt version of KWIVER, specify the kwiver_DIR flag to cmake.
The kwiver_DIR is the KWIVER build directory root, which contains the kwiver-config.cmake file. 
*NOTE* As KWIVER requires a Fletch directory, the build will ignore the fletch_DIR variable and use the Fletch that was used to build KWIVER. ::

    $ cmake ../../src -DCMAKE_BUILD_TYPE=Release -Dkwiver_DIR:PATH=<path/to/kwiver/build/dir> 

You must ensure that the specified build of KWIVER was build with a fletch that was built with all necessary options.
KWIVER must have also been built with all the appropriate flags for use by DIVA.
The required flags can be found in this file : `<CMake/add_project_kwiver.cmake>`_ 

Compiling
^^^^^^^^^

Once your CMake generation has completed and created the build files,
compile in the standard way for your build environment.  On Linux
this is typically running ``make``. Visual Studio users, open and build the <path/to/DIVA/build/dir>/DIVA.sln

Running DIVA
^^^^^^^^^^^^

Once you've built DIVA, you'll want to test that it's working on your system.
DIVA will create an install directory inside the DIVA build location.
From a command prompt change to this install directory and execute the following command::

  # via a bash shell
  </path/to/DIVA/build/install>$ source setup_DIVA.sh
  #
  # via a windows cmd prompt
  </path/to/DIVA/build/install> setup_DIVA.bat

Where ``</path/to/DIVA/build/install>`` is the install directory inside your DIVA CMake build directory.

This will set up your PATH and other environment variables
to allow DIVA to work conveniently within in the shell/cmd window.

You can run this simple driver to ensure your system is configured properly::

  # via a bash shell
  </path/to/DIVA/build/install>$ ./bin/schema_examples
  #
  # on windows, you will need to also be in the proper folder
  </path/to/DIVA/build/install> ./bin/diva_driver

This will generate some KPF packet messages to the terminal/command window.


What's Next
-----------
* :doc:`Checkout Algorithms in DIVA </processes>`
* :doc:`Integrate Your Algorithm in the framework </tutorials>`
