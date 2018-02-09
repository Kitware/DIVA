Developing
==========

In the following sections, we will refer the executables from the :doc:`tutorials section</tutorials>` section, to look at how you can code using the API.
We are assuimg the same build hierarchy that is described in the tutorials section.

Python
------

We provide several example `python based drivers in the DIVA repository <https://github.com/Kitware/DIVA/tree/master/drivers>`_.
All python driver code will be put into the ``<path/to/diva/install>python`` directory for you to execute and modify as you see fit in learning the API.

While the DIVA API is written in C++, we provide full python bindings via pybind11.
These python bindings are compiled into a diva_python_utils library and will need to be made availabe on your PYTHONPATH to use the API.
Note the setup_DIVA script will add this library to your PYTHONPATH with this command:

.. code-block:: bash

  # On Linux
  export PYTHONPATH=$PYTHONPATH:<path/to/diva/install>/lib

To access the DIVA python API in your python files, simply import it with the following code

.. code-block:: python

  import diva_python_utils

Reference the :doc:`API</api>` and this `example file <https://github.com/Kitware/DIVA/blob/master/drivers/schema_examples/schema_examples.py>`_ for using the API. |br|
Currently, the python API only supports reading and writing experiment and KPF objects. |br|
(i.e. It does not support frame retrieval from the experiment data source)

C++
---

We provide several example `C++ based drivers in the DIVA repository <https://github.com/Kitware/DIVA/tree/master/drivers>`_.

Modifying the C++ Drivers
~~~~~~~~~~~~~~~~~~~~~~~~~

You may modify the cpp files in your DIVA source folder. To build a new instance of the driver, rebuild the driver project.

For example, maybe you would like to turn off the images being displayed during the execution of the darknet_detections executable.
Simply edit the `darknet_detections.cpp file <https://github.com/Kitware/DIVA/blob/master/drivers/darknet_detections/darknet_detections.cpp>`_
and comment out the following line

.. code-block:: cpp

  // Uncomment/comment this macro to turn on/off the display of each processed image with detections
  // #define DISPLAY_FRAME

Then to compile these changes, on Linux, open terminal to the DIVA build directory :

.. code-block:: bash

  cd DIVA-build
  make darknet_detections
  # Did you know you can hit tab twice after you type make to see all make targets?


The ``<path/to/DIVA/install>/bin/darknet_detections`` will be updated from your code changes and you will not get the images displayed after each detection.

As you explore and modify the provided cpp drivers, notice the use of the KWIVER API. |br|
Using the DIVA API also provides access to the powerful `KWIVER framework <https://github.com/Kitware/kwiver>`_ and its various `data types <http://kwiver.readthedocs.io/en/latest/vital/architecture.html>`_ and `algorithms <http://kwiver.readthedocs.io/en/latest/arrows/architecture.html>`_.


Building your own C++ Driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provided in the repository, is a sample `CMakeLists.txt <https://github.com/Kitware/DIVA/blob/master/example/CMakeLists.txt>`_ file. |br|
You can use this file as the basis for your own C++ executable or library that uses the DIVA API. |br|
This file, as provided, will create a simple_example executable using the basic_schema code file. |br|
You will need to run CMake explicitly on this file to create the files needed to build this example. |br|
At a minimum, you may need to supply CMake with the path to the ``<path/to/DIVA/install>``
Note that it defaults to the install folder in the ``<path/to/DIVA/build>`` folder, so if you running CMake on this file in your source and you have built the code, you do not need to provide anything.

Here is an example running cmake on this file and pointing to a DIVA build installed at /opt/kitware/DIVA |br|
Instead of /opt/kitware/DIVA, you could use any ``</path/to/a/build/directory>``, that has the diva-config.cmake file

.. code-block:: bash

  # cmake usage : $ cmake </path/to/DIVA/examples> -D<flags> </path/to/a/build/directory>
  # So running cmake from one directory up from the DIVA source root directory
  $ mkdir builds/simple_example
  $ cd builds/simple_example
  $ cmake -DCMAKE_BUILD_TYPE=Release -DDIVA_DIR=/opt/kitware/DIVA ../../DIVA/example/
  # build it
  $ make
  # run it
  $ ./simple_example
  # you will get the kpf examples printed to the terminal screen


.. |br| raw:: html

   <br />
