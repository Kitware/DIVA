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


Features
########
1. :doc:`KPF </kpf>` Kwiver packet format for persistence
2. :doc:`API </api>` DIVA specific structure for definining an experiment, reading input and writing output in standard format
3. :doc:`Processes </algorithm>` Collection of algorithms present in the repository 
4. :doc:`Pipelines </pipelines>` Collection of pipelines for activity and object detection

What's Next
###########
* :doc:`Build DIVA </install>`
* `Learn about Kwiver`_
* :doc:`Checkout Algorithms in DIVA </algorithm>`
* :doc:`Integrate Your Algorithm in the framework </tutorials>`
* :doc:`Contents <index>`

.. Appendix 1: links

.. _IARPA: https://www.iarpa.gov/index.php/research-programs/diva
.. _Build DIVA: https://github.com/Kitware/DIVA#building-diva
.. _Learn about Kwiver: https://github.com/Kitware/kwiver
.. _plugable modules: https://github.com/Kitware/kwiver/tree/master/sprokit/processes
.. _pipeline: https://github.com/Kitware/kwiver/tree/master/examples/pipelines
.. _BSD license: https://github.com/Kitware/DIVA/blob/master/LICENSE.txt
