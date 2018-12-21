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
topologically diverse environment. Additionally, the algorithms in the framework 
are represented as `plugable modules`_ in a configurable `pipeline`_ to natually
support online stream of input while abstracting away the input complexity that 
stems from multiple streams. 

How to Integrate An Activity Detector?
######################################

- To create a pluggable modules that DIVA can detect/use during deployement, the
  framework relies on ``process`` interface. This ensures consistency in the data flow when
  different ``process`` interact with each other. An algorithm can be expressed 
  as a process or a set of processes based on developer's requirement. Currently, 
  DIVA supports Python and C++ processes that are created by inherting 
  ``KwiverProcess`` and  ``sprokit::process`` respectively. Overriding the interface
  would be divided into three components: 
  
    1. Defining Ports: The data flow amongst processes is managed using 
       ``ports``. The input ``ports`` indicate input for the algorithm. Similarly,
       the output ``ports`` indicate the output of the algorithm. 
       Eg, ``RC3DDetector`` declares ``image``, ``timestamp`` and ``file_name`` as 
       input ports and ``detected_object_set`` as 
       output port. These ``ports`` use  `Vital types <complex data types_>`_ to send 
       across complex data structures that were designed for vision based applications. 
       Additionally, if these types do not cover an algorithms input/output requirement,
       Vital types can be extensible. Refer to the tutorial on `Extending Vital Types`_   
       for additional information.

    2. Adding Configuration Parameters: `Configuration parameter <config_>`_ are 
       used to specify algorithm parameters. These parameters are declared by a 
       process and can be specified when the process is added to a pipeline or 
       during runtime. Alongwith the traditional use of ``key: value`` based 
       mechanism to provide parameters to algorithms, DIVA provides ``AbstractAlgorithm`` 
       that makes the algorithm implementation a configuration parameter. 
       Pipelines assembled using abstract algorithms are configurable based on 
       implementation selected during runtime. Refer to the tutorial on 
       :doc:`Tight Integration </tutorials>` and `Extending Kwiver`_ for details.
    
    3. Overriding ``_configure`` and ``_step`` functions: ``_configure`` is used
       for one time configuration during instantiation. ``_step`` is input/output
       dependent functionality of the process and is primarily used to express the
       core functionality of the algorithm.  
  For example and details about syntax, refer to :doc:`Processes </processes>` section.

- The data flow amongst the modules is defined using a `pipeline`_. The pipeline
  declares the process present in the detector, provides configuration parameters
  for every process and connects the ports for the process. The framework supports
  expressing pipelines using plaintext file or programatically in Python and C++.
  The data flow is used as input to `Sprokit`_ which provides the benefits of the 
  framework listed below. Refer to :doc:`Pipelines </pipelines>` for more additional
  infomation.   

- To execute a plaintext pipeline file, the DIVA uses ``pipeline_runner``. 
  pipeline_runner support ``--set`` flag to modify any configuration at runtime. Eg. ::
    pipeline_runner -p test.pipe --set test_process:configuration_name=test
  The usage information for pipeline_runner is documented in detail `here <pipeline_runner>`_.    


Features
########
DIVA builds upon `Kwiver`_ to leverage the algorithms and infrastructure provided 
by Kwiver. The major features of Kwiver that are used by DIVA include

1. Abstract Algorithms: Kwiver seperates the definition and implementation of standard
   algorithms. This allows the user to have multiple implementation of an algorithm that
   can be selected at runtime as a configuration parameter. The definition and implementations
   are extensible in c++ which allows user to integrate their algorithms at different levels
   of abstraction in the framework. Out of the box, Kwiver supports numerous algorithm
   definition and implementation that can be found in `algorithms`_ and `arrows`_ directory.
2. Data Types: Alongwith the standard types, Kwiver provides a set of `complex data types`_
   designed for the computer vision algorithms, eg. BoundingBox. These types provide
   a standard input/output interface for the algorithms to pass data. Thereby
   allowing users to chain algorithms and exchange data between them. 
3. Interprocess communication: With deep networks becoming state of the art for 
   almost all computer vision task, GPU footprint of the components of a large
   system is a major concern. For example, creating an instance of activity detector 
   with `ACT`_ to localize activities and `Faster RCNN`_ to localize participants 
   in the activity would require ~15Gb of GPU memory and would rely on multiple
   GPUs. To manage the communication between the algorithms and synchronizing the
   input/outputs, Kwiver uses `ZeroMQ`_'s. This allows the user to distribute 
   the components of their system to any networked system with the resource to 
   run it.   
4. Multi-threaded reconfigurable pipelines: The chaining mechanism in Kwiver are
   called pipelines. A pipeline defines the relationship of the components of 
   a system in text format or programtically. The pipelines are agnostic 
   to the language in which the process are written and can use any and all the 
   processes that kwiver and DIVA provides. By default pipelines are multi-threaded
   and can be paired with ZeroMQ to distribute the components of a pipeline 
   across the network.

Additionally, to support development of multi-stream activity detectors, DIVA 
standardizes the input and annotations using the following interfaces 

1. KPF: The standard annotation format used to persist object detections, tracks,
   activities and associated metadata. The primary objective of KPF is to provide
   unambiguous representation of objects, tracks and activites both semantically
   and syntactically. Additionally, it provides transport agnostic representation 
   that can be extended to include changes in data like adding more activity labels.
   The semantics of KPF are discussed in more detail :doc:`here </kpf>`.
2. DIVA API: The objective of DIVA api is two-fold

    1 To provide an interface to access KPF annotations in C++ and python. 
    
    2 To define an experiment interface that defines input source,
    output mechanism and the algorithm used the experiment in yml format. The
    API support reading images, videos and rtsp stream based on the experiment
    file.

What's Next
###########
* :doc:`Build DIVA </install>`
* `Learn about Kwiver <Kwiver_>`_
* :doc:`Checkout Algorithms in DIVA </processes>`
* :doc:`Integrate Your Algorithm in the framework </tutorials>`
* :doc:`Contents <index>`

.. Appendix 1: links

.. _IARPA: https://www.iarpa.gov/index.php/research-programs/diva
.. _Build DIVA: https://github.com/Kitware/DIVA#building-diva
.. _Kwiver: https://github.com/Kitware/kwiver
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
.. _Extending Kwiver: https://github.com/Kitware/kwiver/blob/master/doc/manuals/extentions.rst 
.. _Sprokit: https://github.com/Kitware/kwiver/blob/master/doc/manuals/sprokit/getting-started.rst
.. _pipeline_runner: https://github.com/Kitware/kwiver/blob/master/doc/manuals/tools/pipeline_runner.rst
