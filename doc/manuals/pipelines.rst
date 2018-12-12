Pipelines
=========

**Pipelines** are used to provide a plug and play environment that can be used 
for quick prototyping and experimentation. Addtionally, ``port`` checks implemented
by the framework ensures consistency in data as the ``processes``  are connected
to work in sync with each other. 

Pipeline is used to express the data flow in a system. The data flow is the input
for the workhorse of framework, `Sprokit`_. Sprokit handles every aspect of
execution for the pipeline. This includes

1. Finding registered processes (including out-of-box processes from `Kwiver`_).
2. Enforcing ``port`` checks based on the ``port_traits`` declared by the process.
3. Scheduling and synchronizing the ``processes`` in a pipeline.
4. Providing introspection capbabilities during the development for optimization.
5. Providing tools for execution and visualization of the pipeline.

Pipelines can be written as plaintext file or can be embedded in Python or C++ program.
To execute the plaintext file, `pipeline_runner`_ is provided by Kwiver. Furthermore,
plaintext file can be translated into their Python/C++ counterpart using `bake` 
utility provided by Kwiver. The `semantics`_ and `design`_ guidelines for pipelines is
provided by Kwiver. Kindly refer to those before creating new pipelines.

Although, Sprokit implicitly supports multi-threaded pipelines, the pipelines are
restricted to a single machine. The framework relies on `ZeroMQ` for providing distributed 
pipelines. These pipelines use ``zeromq_transport_send`` and 
``zeromq_transport_receive`` processes to communicate over the network. Currently,
ZeroMQ based pipelines support publisher-subscriber pattern with multiple publishers 
and subscribers. 

Every algorithm present in DIVA has a dedicated local and ZeroMQ pipeline to replicate
the offline behavior of the algorithm in an online enviornment on a single system or
on multiple systems. These pipelines have been pictorially documented below for the 
ease of understanding.

Local Pipelines
---------------

Object Detection
^^^^^^^^^^^^^^^^
.. graphviz:: _pipe/darknet.dot

Optical Flow
^^^^^^^^^^^^
.. graphviz:: _pipe/optical_flow.dot

Activity Detection
^^^^^^^^^^^^^^^^^^

Temporal Localization
"""""""""""""""""""""

**RC3D Pipeline**

.. graphviz:: _pipe/rc3d/rc3d.dot

**ACT Pipeline**

.. graphviz:: _pipe/act/act.dot

Spatial Temporal Localization
"""""""""""""""""""""""""""""

**ACT Pipeline**

.. graphviz:: _pipe/act/act_aod.dot

ZeroMQ Pipelines
----------------

Image Sender
^^^^^^^^^^^^
.. graphviz:: _pipe/image_sender.dot

Activity Detection
^^^^^^^^^^^^^^^^^^

Temporal Localization
"""""""""""""""""""""
**RC3D Pipeline**

.. graphviz:: _pipe/rc3d/rc3d_zmq.dot

**ACT Pipeline**

.. graphviz:: _pipe/act/act_zmq.dot

Spatial Temporal Localization
"""""""""""""""""""""""""""""

**ACT Pipeline**

.. graphviz:: _pipe/act/act_aod_zmq.dot

.. Appendix 1: Links

.. _Sprokit: https://github.com/Kitware/kwiver/blob/master/doc/manuals/sprokit/getting-started.rst
.. _Kwiver: https://github.com/Kitware/kwiver/tree/master/sprokit/processes
.. _pipeline_runner: https://github.com/Kitware/kwiver/blob/master/doc/manuals/tools/pipeline_runner.rst
.. _semantics: https://github.com/Kitware/kwiver/blob/master/doc/manuals/sprokit/pipeline_declaration.rst
.. _design: https://github.com/Kitware/kwiver/blob/master/doc/manuals/sprokit/pipeline_design.rst
