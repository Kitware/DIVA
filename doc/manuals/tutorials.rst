Tutorials
=========

The following sections describe a set of DIVA tutorials. |br|
Visit the `repository <https://github.com/Kitware/DIVA>`_ on how to get and build the DIVA code base. |br|
All the source code mentioned here are provided in the `driver directory of the repository <https://github.com/Kitware/DIVA/tree/master/drivers>`_. 


As always, we would be happy to hear your comments and receive your contributions on any tutorial.

Basic KPF I/O
-------------

:doc:`KPF</kpf>` is the data/file format DIVA will use for specifying an experiment and its results for scoring. |br|
DIVA provides a C++ and Python utility library that contains API's for reading and writing experiment files as well as the various results files for scoring particular algorithms. |br|
The API libraries provided are intended to be linked into a performer executable. By using these API classes performers will be able to easily:

* Read and interpret an experiment file
* Write scorable results files
* Recieve image frames from the input source specified for an experiment

The following classes are provided in the API to assist performers read and write data files for execution and scoring 

=================================================================================== ==========================================================================================
`Experiment <https://github.com/Kitware/DIVA/blob/master/utils/diva_experiment.h>`_  Describes the task parameters a performer is to execute      
`Meta <https://github.com/Kitware/DIVA/blob/master/utils/diva_packet.h>`_            Used to add comments and context to Geometry and Activity files     
`Geometry <https://github.com/Kitware/DIVA/blob/master/utils/diva_geometry.h>`_      Describes the detection and tracking of objects in a scene       
`Activity <https://github.com/Kitware/DIVA/blob/master/utils/diva_activity.h>`_      Describes the detection and tracking of activities in a scene
=================================================================================== ==========================================================================================

We provide a simple C++ and Python examples that utilize the API to write out some KPF Files |br|
Before you run these examples, please set your enviroment by running the appropriate setup_DIVA script ::

  </path/to/DIVA/build>/DIVA-build$ source setup_DIVA.sh

C++
~~~

A simple `C++ executable <https://github.com/Kitware/DIVA/blob/master/drivers/schema_examples/schema_examples.cpp>`_ is provided to generate some KPF objects. To run this example, do the following ::

  </path/to/DIVA/build>/DIVA-build/drivers/schema_examples$./schema_examples
  # You will get the following output
  - { meta: Example geometry }
  - { meta: 1 tracks; 50 detection }
  - { meta: min / max frame: 0 942 min / max timestamp: 0 471  }
  - { meta: min / max geometry: 0,289 - 1278 719 ( 1279x431+0+289 ) }
  - { geom: { id0: 0, id1: 66, ts0: 0, g0: 104 349 210 385, src: truth, eval_type: tp, occlusion: heavy, poly0: [[ 100, 399 ],[ 200, 398 ],[ 300, 397 ],],  } }
  ...


Python
~~~~~~

A simple `Python script <https://github.com/Kitware/DIVA/blob/master/drivers/schema_examples/schema_examples.py>`_ is provided to generate some KPF objects. To run this example, do the following ::
 
  </path/to/DIVA/Source>/drivers/schema_examples$python schema_examples.py
  # You will get the following output
  Geometry Content
  - { meta: Example geometry }
  - { meta: 1 tracks; 50 detection }
  - { meta: min / max frame: 0 942 min / max timestamp: 0 471  }
  - { meta: min / max geometry: 0,289 - 1278 719 ( 1279x431+0+289 ) }
  - { geom: { id0: 0, id1: 66, ts0: 0, g0: 104 349 210 385, src: truth, eval_type: tp, occlusion: heavy, poly0: [[ 100, 399 ],[ 200, 398 ],[ 300, 397 ],],  } }
  ...

Basic Experiment
----------------

As we mentioned above, the DIVA API can provide image frames from the input source specified for an experiment. In this example we will look at how to do this.


Object Detection
----------------


Scoring
~~~~~~~

Coming Soon!!


Activity Detection
------------------

Coming Soon!!

.. |br| raw:: html

   <br />
