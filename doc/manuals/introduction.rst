Introduction
============

DIVA is a framework for deploying video analytics in a multi-camera
environment, funded by `IARPA`_ and licensed under `BSD license`_.

DIVA is being developed as an open source, end to end system for incorporating 
state of the art activity detection algorithms into multi-camera streaming video 
environments. These algorithms include both traditional and deep learning approaches 
for activity detection. Since almost all these algorithms are designed to work in 
offline single stream environment, porting them to online multi-stream environment requires
significant effort on part of the researchers and developers. DIVA  
seeks to reduce this effort and streamline the process by providing an open standard 
for reasoning across multiple video streams obtained from geographically and 
topologically diverse environment. 

The DIVA framework is based on Kitware's Open Source `KWIVER_` framework for developing 
heterogeneous computer vision systems.  KWIVER provides support for integrating for integrating
a variety of 3rd party tools into a dynamic, plugin based environment for building
complex computer vision based systems. KWIVER's Sprokit framework provides a pipeline
processing framework optimized for video processing that simplifies building multi-threaded
and or distributed processing chains.

The process of integrating a DIVA activity detector into the DIVA framework primarily 
consists of creating a plugin or collection of plugins chiefly be implementing a configuration
and frame processing function and combining them with other provided processes (such as I/O
processes) into sophisticated processing pipelines.

Integrating an Activity Detector
#################################

To create a pluggable modules that the DIVA framework can detect/use during deployment, you will 
use the Sprokit ``process`` interface. This ensures consistency in the data flow, allowing
different ``process`` nodes to interact with each other. An algorithm can be expressed 
as a single process or a pipeline of processes based on developer's requirements. Currently, 
the DIVA framework supports Python and C++ processes that are created by inheriting 
``KWIVERProcess`` and  ``sprokit::process`` respectively. Implementing the process interface
can be divided into three components: 

    1. Defining Ports: The data flow amongst processes is managed using 
       ``ports``. The input ``ports`` indicate input for the algorithm. Similarly,
       the output ``ports`` indicate the output of the algorithm. 
       For example,  the DIVA baseline algorithm ``RC3DDetector`` declares ``image``, ``timestamp`` and ``file_name`` as 
       input ports and ``detected_object_set`` as its only  
       output port. These ``ports`` use  `Vital types <complex data types_>`_ to transmit
       complex data structures designed for vision based applications. 
       Additionally, if these types do not cover an algorithms input/output requirement,
       additional Vital types can be created. Refer to the tutorial on `Extending Vital Types`_   
       for additional information.

    2. Adding Configuration Parameters: `Configuration parameter <config_>`_ are 
       used to specify algorithm parameters. These parameters are declared by a 
       process and can be specified when the process is added to a pipeline or 
       at runtime.  In addition to traditional configuration parameters, processes
       frequently make use of KWIVER's ``AbstractAlgorithm`` capability to allow a
       configuration parameter to select among several implementations of the processes
       algorithm.  Refer to the tutorial on :doc:`Tight Integration </tutorials>` and 
       `Extending KWIVER`_ for details.

    3. Overriding ``_configure`` and ``_step`` functions: The ``_configure`` function
       is called process instantiation and is responsible for retrieving and applying
       configuration parameters.  The ``_step`` function is called for each processing step
       (typically for each frame of video input) and retrieves data from the process input
       ports, manipulates and transforms that data in some way and puts the resulting data
       on its output port for processing by down stream nodes in the pipeline.

For more details about sprokit processes, refer to :doc:`Processes </processes>`.

The data flow amongst the modules is defined as a `pipeline`_ (actually a directed
acyclic graph of processing nodes). The pipeline
declares the process present, provides configuration parameters
for every process and connects the ports for the process. The framework supports
expressing pipelines using plain text file or programmatically in Python or C++.
Refer to :doc:`Pipelines </pipelines>` for more additional information.

To execute a plain text pipeline file, the DIVA framework uses an executable
provided by KWIVER, ``pipeline_runner``.  The executable accepts a ``.pipe`` file
as input along with any configuration parameter adjustments and runs the pipeline::

 pipeline_runner -p test.pipe --set test_process:configuration_name=test

The usage information for pipeline_runner is documented in detail `here <pipeline_runner>`_.


Features
########

As noted, the DIVA framework is based on `KWIVER_`, leveraging existing algorithms
and infrastructure.  The major features of KWIVER that are used by DIVA include

1. Abstract Algorithms: KWIVER separates the definition and implementation of standard
   algorithms. This allows the user to have multiple implementation of an algorithm that
   can be selected at runtime as a configuration parameter. The definition and implementations
   are extensible in c++ which allows user to integrate their algorithms at different levels
   of abstraction in the framework. Out of the box, KWIVER supports numerous algorithm
   definition and implementation that can be found in `algorithms`_ and `arrows`_ directory.
2. Data Types: Along with the standard types, KWIVER provides a set of `complex data types`_
   designed for the computer vision algorithms, e.g. BoundingBox. These types provide
   a standard input/output interface for the algorithms to pass data. Thereby
   allowing users to chain algorithms and exchange data between them. 
3. Multi-threaded reconfigurable pipelines: The chaining mechanism in KWIVER are
   called pipelines. A pipeline defines the relationship of the components of 
   a system in text format or programmatically. The pipelines are agnostic 
   to the language in which the process are written and can use any and all the 
   processes that KWIVER and DIVA provides. By default pipelines are multi-threaded
   and can be paired with ZeroMQ to distribute the components of a pipeline 
   across the network.
4. Interprocess communication: With deep networks becoming state of the art for 
   almost all computer vision task, GPU footprint of the components of a large
   system is a major concern. For example, creating an instance of activity detector 
   with `ACT`_ to localize activities and `Faster RCNN`_ to localize participants 
   in the activity would require ~15Gb of GPU memory and would rely on multiple
   GPUs. To manage the communication between the algorithms and synchronizing the
   input/outputs, KWIVER uses `ZeroMQ`_'s. This allows the user to distribute 
   the components of their system to any networked system with the resource to 
   run it.   

Additionally, to support development of multi-stream activity detectors, DIVA 
standardizes the input and annotations using the following interfaces 

1. KPF: The standard annotation format used to persist object detections, tracks,
   activities and associated metadata. The primary objective of KPF is to provide
   unambiguous representation of objects, tracks and activities both semantically
   and syntactically. Additionally, it provides transport agnostic representation 
   that can be extended to include changes in data like adding more activity labels.
   The semantics of KPF are discussed in more detail :doc:`here </kpf>`.
2. DIVA API: The objective of DIVA API is two-fold

    1 To provide an interface to access KPF annotations in C++ and python. 
    
    2 To define an experiment interface that defines input source,
    output mechanism and the algorithm used the experiment in YML format. The
    API support reading images, videos and RTSP stream based on the experiment
    file.

What's Next
###########
* :doc:`Build DIVA </install>`
* `Learn about KWIVER <KWIVER_>`_
* :doc:`Checkout Algorithms in DIVA </processes>`
* :doc:`Integrate Your Algorithm in the framework </tutorials>`
* :doc:`Contents <index>`

.. Appendix 1: links

.. _IARPA: https://www.iarpa.gov/index.php/research-programs/diva
.. _Build DIVA: https://github.com/Kitware/DIVA#building-diva
.. _KWIVER: https://github.com/Kitware/kwiver
.. _plugable modules: https://github.com/Kitware/kwiver/tree/master/sprokit/processes
.. _pipeline: https://github.com/Kitware/kwiver/tree/master/examples/pipelines
.. _BSD license: https://github.com/Kitware/DIVA/blob/master/LICENSE.txt
.. _arrows: https://github.com/Kitware/kwiver/tree/master/arrows
.. _algorithms: https://github.com/Kitware/kwiver/tree/master/vital/algo
.. _complex data types: https://github.com/Kitware/kwiver/blob/master/doc/manuals/vital/architecture.rst
.. _ACT: https://thoth.inrialpes.fr/src/ACTdetector/
.. _Faster RCNN: https://github.com/rbgirshick/py-faster-rcnn
.. _ZeroMQ: http://zeromq.org/
.. _Extending Vital Types: https://github.com/Kitware/kwiver/tree/master/doc/manuals/vital
.. _config: https://github.com/Kitware/kwiver/blob/master/doc/manuals/vital/configuration.rst
.. _Extending KWIVER: https://github.com/Kitware/kwiver/blob/master/doc/manuals/extentions.rst 
.. _Sprokit: https://github.com/Kitware/kwiver/blob/master/doc/manuals/sprokit/getting-started.rst
.. _pipeline_runner: https://github.com/Kitware/kwiver/blob/master/doc/manuals/tools/pipeline_runner.rst
