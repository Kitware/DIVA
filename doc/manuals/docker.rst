Docker
======

A Docker image is available as an alternative to building DIVA from scratch.

DIVA Docker Image
-----------------

Kitware maintains a `Docker <https://www.docker.com/>`_ image with DIVA prebuilt.
The Dockerfile used to build the image can be found `here <Dockerfile>`_.

Pull the image from Dockerhub::

 "docker pull kitware/diva:latest"

(`https://hub.docker.com/r/kitware/diva <https://hub.docker.com/r/kitware/diva>`_)

or build the DIVA image using the dockerfile::

 "docker build -t diva:tagname ."
