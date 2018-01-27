API
===

**NOTE The API is currently in an early alpha stage**

**Email diva-te@kitware.com to provide comments and/or feedback**

DIVA provides an Application Programming Interface (API) that provides the following funtionality :

* Read and Write an experiment file
* Read and Write scorable results files
* Recieve image frames from the input source specified for an experiment

The provided API library is intended to be linked into a performer C++ executable, or imported into peformer Python scripts.

The following classes are provided in the API to assist performers read and write data files for execution and scoring 

=================================================================================== =========================================================================================================================================================================
`Experiment <https://github.com/Kitware/DIVA/blob/master/utils/diva_experiment.h>`_  Describes the task parameters a performer is to execute      
`Meta <https://github.com/Kitware/DIVA/blob/master/utils/diva_packet.h>`_            Used to add comments and context to Geometry and Activity files     
`Geometry <https://github.com/Kitware/DIVA/blob/master/utils/diva_geometry.h>`_      Describes the detection and tracking of objects in a scene   
`Label <https://github.com/Kitware/DIVA/blob/master/utils/diva_label.h>`_            Provides a classification description associated with Geometry tracks     
`Activity <https://github.com/Kitware/DIVA/blob/master/utils/diva_activity.h>`_      Describes the detection and tracking of activities in a scene
`Input Frame <https://github.com/Kitware/DIVA/blob/master/utils/diva_input.h>`_      Provides individual frames from an experiment source as a `KWIVER Vital Image Container <https://github.com/Kitware/kwiver/blob/master/vital/types/image_container.h>`_ 
=================================================================================== =========================================================================================================================================================================

Experiment Configuration
------------------------

Reads and writes the experiment configuration that informs a performer what the inputs are and goals are of the experiement. |br|
The experiment configuration schema is currently implemented via `this class <https://github.com/Kitware/DIVA/blob/master/utils/diva_experiment.h>`_



KPF Evaluation
--------------

Reads and writes evaluation files to be use by the scoring and evaluation tool



Frame Provider
--------------

Takes an input source(s) and is able to pull out individual frames on demand

  

.. |br| raw:: html

   <br />
