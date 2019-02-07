API
===

**NOTE The API is currently in an early alpha stage**

**Email diva-te@kitware.com to provide comments and/or feedback**

DIVA provides an Application Programming Interface (API) with the following functionality :

* Read and Write an experiment file
* Accessors for kpf annotations associated with the data
* Iterator iterface for image frames from ``image_list``, ``video`` and ``rtsp``
  stream as specified in the experiment file.

The api is written in C++ with Python bindings to support development in either
languages.  


Experiment Configuration
------------------------

The `Experiment API <https://github.com/Kitware/DIVA/blob/master/utils/diva_experiment.h>`_ reads and writes the file that informs a performer what the inputs are and goals are of and experiment. |br|

The experiment file holds the following data
 
* input - A set of properties specifying and describing the input
* output - A set of properties specifying the location and format for the outputs
* scoring - A set of properties specifying the experiment baseline data and scoring directives
* algo - A set of properties for executing and configuring a specific algorithm implementation

The DIVA experiment file, `drivers/data/image_experiment.yml <https://github.com/Kitware/DIVA/blob/master/drivers/data/image_experiment.yml.in>`_ will be used in the experiment tutorials.

KPF Evaluation
--------------

The KPF Evaluation API consists of several class to read and write KPF packets to files that will be evaluated by the the scoring and evaluation tool. |br|
These classes are intended to be simple data intefaces that can easily be instantiated and populated within a performers application (C++ or Python) to provide a common data format for scoring. 

=================================================================================== =======================================================================
`Meta <https://github.com/Kitware/DIVA/blob/master/utils/diva_packet.h>`_            Used to add comments and context to Geometry and Activity files     
`Geometry <https://github.com/Kitware/DIVA/blob/master/utils/diva_geometry.h>`_      Describes the detection and tracking of objects in a scene   
`Label <https://github.com/Kitware/DIVA/blob/master/utils/diva_label.h>`_            Provides a classification description associated with Geometry tracks     
`Activity <https://github.com/Kitware/DIVA/blob/master/utils/diva_activity.h>`_      Describes the detection and tracking of activities in a scene
=================================================================================== =======================================================================

Frame Provider
--------------

The `Input Frame API <https://github.com/Kitware/DIVA/blob/master/utils/diva_input.h>`_  takes the input source, specified in the experiment file, and is able to pull out individual frames on demand.

  

.. |br| raw:: html

   <br />
