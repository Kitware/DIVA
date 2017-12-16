API
===

**NOTE The API is currently in an early alpha stage**

**Email diva-te@kitware.com to provide comments and/or feedback**

DIVA provides an Application Programming Interface (API) that provides the following funtionality :

 - Experiment Configuration I/O : Reads and writes the experiment configuration that informs a performer what the inputs are and goals are of the experiement.
 - KPF Evaluation I/O : Reads and writes evaluation files to be use by the scoring and evaluation tool
 - Frame Provider : Takes an input source(s) and is able to pull out individual frames on demand

Experiment Configuration
------------------------

The experiment configuration schema is currently implemented via `this class <https://github.com/Kitware/DIVA/blob/master/utils/diva_experiment.h>`_

KPF Evaluation
--------------

Geometry Schema API
~~~~~~~~~~~~~~~~~~~

The geometry schema is currently implemented via `this class <https://github.com/Kitware/DIVA/blob/master/utils/diva_geometry.h>`_

Label Classification API
~~~~~~~~~~~~~~~~~~~~~~~~

The label schema is currently implemented via `this class <https://github.com/Kitware/DIVA/blob/master/utils/diva_label.h>`_

Activity API
~~~~~~~~~~~~

The activity schema is currently implemented via `this class <https://github.com/Kitware/DIVA/blob/master/utils/diva_activity.h>`_

Frame Provider
--------------

The frame provider is still under design but will leverage the KWIVER `image_container <https://github.com/Kitware/kwiver/blob/master/vital/types/image_container.h>`_ class
  

