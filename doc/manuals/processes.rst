Processses
==========
**Process** is used to encapsulate an algorithm. It allows developer to
define the input and output interfaces for the algorithm, 
configure the algorithm and for a given input, define a step
function that applies the algorithm on the input. For example, a classifier process
would take an image as input and produce a vector of class scores as output.
The model file would be used to configure the algorithm. The step function for
this process would be the processing logic of the classifier for the given input.

DIVA currently supports C++ and Python processes. The interface in both languages 
is fairly similar. The new process inherits ``KwiverProcess`` in Python and 
``sprokit::process`` in C++. For the purpose of configuring the process, 
`configuration parameter <config_>`_ is taken as input by the process. These
configuration can be specified at runtime by the :doc:`pipelines </pipelines>`. 
To define input and
output interfaces of a process ``port traits`` are used. A process can declare
any ports that have been defined `input/output ports list <port_>`_ . 
The ports can be declared as ``required`` or ``optional`` using ``port flags``
based on the process requirement.

.. content-tabs::

    .. tab-container:: tab1
            :title: Python
            
            .. literalinclude:: processes/sample_process.py
                :linenos:
                :language: python
                :lines: 4-21

    .. tab-container:: tab2
            :title: C++

            .. literalinclude:: processes/sample_process.cxx
                :linenos:
                :language: c++
                :lines: 7-31

The process can override ``_configure`` and ``_step`` function to implment the
algorithm. ``_configure`` is primarily used for one time setup steps creating a
model object from model definition and loading the weight file to the object.
``_step`` function is used to implment the core processsing logic of the algorithm.
For the classifier process, this would be the forward pass of the classifier. The 
output of the classifier would be a vector of double that can be push out of the 
process.

.. content-tabs::

    .. tab-container:: tab1
            :title: Python
            
            .. literalinclude:: processes/sample_process.py
                :linenos:
                :language: python
                :lines: 23-34

    .. tab-container:: tab2
            :title: C++

            .. literalinclude:: processes/sample_process.cxx
                :linenos:
                :language: c++
                :lines: 33-45

Since input handling has been completely decoupled from the algorithm, different
input source can be plugged in without making any changes to the classifier. Additionally,
Kwiver supports abstract algorithms that can configured to chose an implementation
of the algorithm during runtime. Thus the abstract classifier would be replaced by a 
concreate implementation  like InceptionNet based on the user's choice at runtime.

Loose Integration
-----------------
Now that we have a working process, we need the `Kwiver Tools`_ to detect the process.
To this end we would be registering the process with `sprokit`_ using ``__sprokit_register__`` 
in Python and ``register_factories`` method in C++.  

.. content-tabs::

    .. tab-container:: tab1
            :title: Python
            
            .. literalinclude:: processes/sample_process.py
                :linenos:
                :language: python
                :lines: 38-45

    .. tab-container:: tab2
            :title: C++

            .. literalinclude:: processes/register_processes.cxx
                :linenos:
                :language: c++

You can use `plugin_explorer`_ tool provided by Kwiver to check if the registration
was successful. All available plugin are displayed by plugin explorer. 

.. note::
    If your python process resides outside ``processes/python`` or you add a new 
    directory in ``processes/python``, you would have to modify the setup scripts 
    in CMake directory. 

.. note::
    If your algorithm uses libraries that are not available in the default paths of the 
    system, you would have to write a setup script to set the correct enviornment variables. 
    This setup script requirement is the primary limitation of loose integration that 
    would be overcome once an algorithm tightly integrated in DIVA.

.. toggle-header::
    :header: **Complete Process Definition** 

        .. content-tabs::

            .. tab-container:: tab1
                    :title: Python
                    
                    .. literalinclude:: processes/sample_process.py
                        :linenos:
                        :language: python

            .. tab-container:: tab2
                    :title: C++

                    .. literalinclude:: processes/sample_process.cxx
                        :linenos:
                        :language: c++

Tight Integration 
-----------------
.. note::
    At the moment, only C++ can be used to tightly integrate an algorithm with the
    framework
                     

Activity Detectors
------------------

Since supporting the development of activity detector is the primary objective
of DIVA, this section presents the algorithm present in the framework. The processs
in this section and the subsequent section are a small subset of the processes
available through Kwiver. A more detailed list of processes is available
`here <Kwiver Processes_>`_.

Temporal Localizers
^^^^^^^^^^^^^^^^^^^
The activity detectors in this class detect the temporal bound of the activities
in an unbounded video. 

1. RC3D :cite:`Xu2017iccv`

.. autoclass:: DIVA.processes.rc3d.rc3d_detector.RC3DDetector


Spatial Temporal Localizers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The activity detectors in this class detect the spatial and temporal bound of the 
activities in an unbounded video. They can be paired with an object detector/tracker
to detect/track the participating objects

1. ACT :cite:`kalogeiton17iccv`

.. autoclass:: DIVA.processes.act.act_detector.ACTDetector

Utility Processes
-----------------
Input
^^^^^
.. doxygenclass:: diva::diva_experiment_process
    :project: diva

RC3D
^^^^
.. autoclass:: DIVA.processes.rc3d.rc3d_json_writer.RC3DJsonWriter

.. autoclass:: DIVA.processes.rc3d.rc3d_visualizer.RC3DVisualizer

ACT
^^^
.. autoclass:: DIVA.processes.act.act_json_writer.ACTJsonWriter

.. autoclass:: DIVA.processes.act.act_visualizer.ACTVisualizer

.. autoclass:: DIVA.processes.act.modify_bbox_resolution.ModifyBboxResolution

.. autoclass:: DIVA.processes.act.merge_tubes.MergeTubes

Optical Flow
^^^^^^^^^^^^
.. doxygenclass:: diva::optical_flow_process
    :project: diva

Multi Object Trackers (Coming Soon!)
------------------------------------

.. Appendix 1: links

.. _Kwiver Processes: https://github.com/Kitware/kwiver/tree/master/sprokit/processes
.. _RC3D: https://github.com/Kitware/DIVA/tree/master/processes/python/rc3d
.. _Abstract Algorithm: https://github.com/Kitware/kwiver/tree/master/vital/algo
.. _config: https://github.com/Kitware/kwiver/tree/master/vital/config
.. _port: https://github.com/Kitware/kwiver/blob/master/sprokit/src/bindings/python/sprokit/pipeline/datum.cxx#L96
.. _Kwiver Tools: https://github.com/Kitware/kwiver/tree/master/tools
.. _sprokit: https://github.com/Kitware/kwiver/blob/master/doc/manuals/sprokit/getting-started.rst
.. _plugin_explorer: https://github.com/Kitware/kwiver/blob/master/doc/manuals/tools/plugin_explorer.rst
.. Appendix 2: Citations

.. bibliography:: processes.bib
