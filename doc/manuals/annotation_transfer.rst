Annotation Transfer
===================

This document describes the process of transfering DIVA annotations from one camera to another via a Kwiver pipeline.  In this walkthrough we'll provided public links to video, annotation, and camera files needed to run the example pipeline.  Here's what you will need to get started:

* KPF formatted annoations from the perspective of the source camera:

.. code-block:: bash

  curl https://gitlab.kitware.com/meva/meva-data-repo/raw/master/annotation/DIVA-phase-2/MEVA/meva-annotations/2018-03-11/16/2018-03-11.16-15-01.16-20-01.school.G336.geom.yml > G336.geom.yml

* Video footage from the destination camera:
  
.. code-block:: bash

  curl https://mevadata-public-01.s3.amazonaws.com/drop-01/2018-03-11/16/2018-03-11.16-15-08.16-20-08.hospital.G436.avi > G436.avi

* Camera files for both source and destination cameras:

.. code-block:: bash

  curl https://gitlab.kitware.com/meva/meva-data-repo/raw/master/metadata/camera-models/2018-03/cameras/G436.krtd > G436.krtd
  curl https://gitlab.kitware.com/meva/meva-data-repo/raw/master/metadata/camera-models/2018-03/cameras/G336.krtd > G336.krtd

* A frame offset, i.e. how many frames ahead is the destination camera relative to the source camera.  In this case we'll use the value `-228`

**NOTE** -- This annotation transfer pipeline is intended as an infrastructure demonstration, rather than a complete algorithmic solution for the annotation transfer task. It uses simple camera-to-camera geometric transfer, with no 3D model information or content-based refinement. In particular, note that transferred boxes may be above or below the ground plane implied by the camera models.
  
The pipeline file
-----------------

We include the pipeline file inline here as a convenience, it can also be found at: `example_annotation_transfer.pipe`_

The pipeline::

  # ================================================================
  process video
    :: video_input

    # File path to the input video (from the destination camera)
    video_filename = G436.avi
    video_reader:type = ffmpeg
  
  # ================================================================
  process cam2cam
    :: detected_object_filter
  
    filter:type = transform_detected_object_set

    # Our source and destination KRTD camera files
    filter:transform_detected_object_set:src_camera_krtd_file_name = G336.krtd
    filter:transform_detected_object_set:dest_camera_krtd_file_name = G436.krtd
  
  # ================================================================
  process kpf_in
    :: detected_object_input
  
    # KPF formatted annotation file path
    file_name = G336.geom.yml
    reader:type = kpf_input
  
  # ================================================================
  process shift
    :: shift_detected_object_set

    # Frame offset between the source and destination cameras; a value
    # of -228 here means that frame 229 in the source video
    # corresponds to frame 1 in the destination camera
    offset = -228
  
  # ================================================================
  process draw
    :: draw_detected_object_set

    draw_algo:type = ocv
    draw_algo:ocv:default_line_thickness = 3
  
  # ================================================================
  process imagewriter
    :: image_writer

    # Writes out the annotated video frames from the destination
    # camera, starting from image00001.jpg.  Note that frames will 
    # only be written out while there are annotations to consume
    file_name_template = G436_output_frames/image%05d.jpg
    image_writer:type = ocv
  
  # ================================================================
  # connections
  connect from video.image
   	to draw.image
  
  connect from kpf_in.detected_object_set
          to shift.detected_object_set
  
  connect from shift.detected_object_set
          to cam2cam.detected_object_set
  
  connect from cam2cam.detected_object_set
  	to draw.detected_object_set
  
  connect from draw.image
  	to imagewriter.image
  
  # -- end of file --

Running the pipeline
--------------------

In the same directory where we've copied down the input files, first we make a directory for the annotated output frames:

.. code-block:: bash

  mkdir G436_output_frames

Next, we call `kwiver runner` on the pipeline file:

.. code-block:: bash

  kwiver runner example_annotation_transfer.pipe

The process may take a few minutes to finish, though the annotated output frames will be generated as the pipeline runs.

Once it finishes, you can find the annotated output frames in the `G436_output_frames` directory.

We can then reconstitute the output frames into a video file using `ffmpeg`:

.. code-block:: bash

  ffmpeg -r 30 -i G436_output_frames/image%05d.jpg G336-to-G436.avi

.. Appendix 1: Links

.. _example_annotation_transfer.pipe: pipelines/example_annotation_transfer.pipe
