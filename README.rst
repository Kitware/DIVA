.. image:: doc/DIVA_Final_Logo_72dpi.png
   :alt: DIVA
   
Deep Intermodal Video Analytics
===============================

The DIVA program intends to develop robust automated activity detection for a multi-camera streaming video environment. 
As an essential aspect of DIVA, activities will be enriched by person and object detection, 
as well as recognition at multiple levels of granularity.
DIVA provides a common framework and software prototype for activity detection, 
person/object detection and recognition across a multi-camera network. 
This framework supports the development of tools for forensic analysis, 
as well as real-time alerting for userdefined threat scenarios.

For more information on how DIVA achieves this goal,
and how to use DIVA visit our `documentation site <http://kwiver-diva.readthedocs.io/en/latest/>`_

Directory Structure and Provided Functionality
==============================================

================ ===========================================================
`<CMake>`_       CMake helper scripts
`<doc>`_         Documentation, manuals, release notes
`<driver>`_      The algorithm plugin modules
`<utils>`_       The DIVA API 
================ ===========================================================

Building DIVA
===============

Dependencies
------------
DIVA requires, at a minimum, Git, CMake, a C++ compiler, and a Python 2.7 compiler.

DIVA is built on top of the `KWIVER <https://github.com/Kitware/kwiver>`_ toolkit.
which is in turn built on the `Fletch <https://github.com/Kitware/fletch>`_ super build system.
To make it easier to build DIVA, a "super-build" is provided to build both KWIVER and Fletch.
It will pull both projects, configure them for DIVA, and build them for you.
If you wish, you may point the DIVA build to use your own builds of KWIVER or Fletch for DIVA to use.


Running CMake
-------------

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
It assumes your terminal/command is working in the ``\DIVA\build\release`` directory. ::

    # cmake usage : $ cmake </path/to/kwiver/source> -D<flags>
    $ cmake ../../src -DCMAKE_BUILD_TYPE=Release 

Using a prebuilt Fletch
~~~~~~~~~~~~~~~~~~~~~~~

If you would like to point DIVA to a prebuilt version of Fletch, specify the fletch_DIR flag to cmake.
The fletch_DIR is the fletch build directory root, which contains the fletchConfig.cmake file. ::

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
---------

Once your CMake generation has completed and created the build files,
compile in the standard way for your build environment.  On Linux
this is typically running ``make``. Visual Studio users, open the <path/to/DIVA/build/dir>/DIVA.sln

Running DIVA
============

Once you've built DIVA, you'll want to test that it's working on your system.
From a command prompt execute the following command::

  # via a bash shell
  source </path/to/DIVA/build>/DIVA-build$ setup_DIVA.sh
  #
  # via a windows cmd prompt
  </path/to/DIVA/build>/DIVA-build setup_DIVA.bat

Where `</path/to/DIVA/build>` is the actual path of your DIVA CMake build directory.

This will set up your PATH and other environment variables
to allow DIVA to work conveniently within in the shell/cmd window.

You can run this simple driver to ensure your system is configured properly::

  # via a bash shell
  </path/to/DIVA/build>/DIVA-build/driver$./diva_driver
  #
  # on windows, you will need to also be in the proper folder
  </path/to/DIVA/build>/DIVA-build/driver diva_driver

This will generate some KPF packet messages to the terminal/command window.

Getting Help
============

Please join the
`kwiver-users <http://public.kitware.com/mailman/listinfo/kwiver-users>`_
mailing list to discuss DIVA/KWIVER or to ask for help with using DIVA/KWIVER.
For announcements about DIVA and other projects built on KWIVER, please join the
`kwiver-announce <http://public.kitware.com/mailman/listinfo/kwiver-announce>`_
mailing list.
