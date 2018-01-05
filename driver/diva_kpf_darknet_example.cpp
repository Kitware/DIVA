/*ckwg +29
* Copyright 2017 by Kitware, Inc.
* All rights reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*
*  * Redistributions of source code must retain the above copyright notice,
*    this list of conditions and the following disclaimer.
*
*  * Redistributions in binary form must reproduce the above copyright notice,
*    this list of conditions and the following disclaimer in the documentation
*    and/or other materials provided with the distribution.
*
*  * Neither name of Kitware, Inc. nor the names of any contributors may be used
*    to endorse or promote products derived from this software without specific
*    prior written permission.
*
* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
* AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
* IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
* ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE FOR
* ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
* DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
* SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
* CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
* OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
* OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/
#include <fstream> 
#include <ostream>
#include "diva_geometry.h"
#include "diva_label.h"

// KWIVER Spcecific files to run darknet
#include "vital/exceptions.h"
#include "vital/types/image.h"
#include "vital/types/image_container.h"
#include "vital/types/detected_object.h"
#include "vital/types/detected_object_set.h"

#include "vital/algo/image_io.h"
#include <vital/algo/video_input.h>
#include "vital/algo/image_object_detector.h"

#include "vital/plugin_loader/plugin_manager.h"

//Uncomment this macro to draw detections on each frame and display it
//#define DISPLAY_FRAME

#ifdef DISPLAY_FRAME
#include <kwiversys/SystemTools.hxx>
#include "opencv2/highgui/highgui.hpp"
#include "arrows/ocv/image_container.h"
#include "vital/algo/draw_detected_object_set.h"
#endif

void darknet_geometry()
{
  // Create a stream/file to write to
  std::filebuf fb;
  fb.open("./darknet_geometry.kpf", std::ios::out | std::ofstream::trunc);
  std::ostream os(&fb);

  //  Instantiate KWIVER
  kwiver::vital::plugin_manager::instance().load_all_plugins();

  // Create a geometry kfp packet we will reuse for each frame
  diva_geometry geom;
  // Instantiate Darknet KWIVER arrow
  kwiver::vital::algo::image_object_detector_sptr detector = kwiver::vital::algo::image_object_detector::create("darknet");
  kwiver::vital::config_block_sptr config = detector->get_configuration();
  config->set_value("net_config",  std::string("C:/Programming/KWIVER/darknet/models/virat.cfg"));
  config->set_value("weight_file", std::string("C:/Programming/KWIVER/darknet/models/virat.weights"));
  config->set_value("class_names", std::string("C:/Programming/KWIVER/darknet/models/virat.names"));
  config->set_value("thresh", 0.20);
  config->set_value("hier_thresh", 0.5);
  config->set_value("gpu_index", 0);
  detector->set_configuration(config);// This will default the configuration

  // Meta kpf packet to provide some commentary in our geomerty kpf file
  diva_meta meta;
  meta.set_msg("darknet geometry");
  meta.write(os);

  // Note this is how you load an image/frame off disk, if that is something you would want to do
  //kwiver::vital::algo::image_io_sptr ocv_io = kwiver::vital::algo::image_io::create("ocv");
  //kwiver::vital::image_container_sptr ocv_img = ocv_io->load("./image.png");

  // Here we are going to open a video file off disk
  kwiver::vital::algo::video_input_sptr   video_reader = kwiver::vital::algo::video_input::create("vidl_ffmpeg");
  video_reader->set_configuration(video_reader->get_configuration());// This will default the configuration 
  video_reader->open("C:/Programming/DIVA/src/data/video.mp4"); // throws
  // Get the capabilities for the currently opened video.
  kwiver::vital::algorithm_capabilities video_traits = video_reader->get_implementation_capabilities();
 
  kwiver::vital::timestamp          ts;
  kwiver::vital::timestamp::time_t  frame_time;
  kwiver::vital::timestamp::frame_t frame_number;

  kwiver::vital::metadata_vector metadata;
  kwiver::vital::metadata_vector last_metadata;
  kwiver::vital::image_container_sptr frame;

  size_t detection_id = 0; // Incremented for every detection on every frame

  // If the video does not know its frame time step, use this as default
  kwiver::vital::timestamp::time_t  default_frame_time_step_usec = static_cast<kwiver::vital::timestamp::time_t>(.3333 * 1e6); // in usec;

#ifdef DISPLAY_FRAME
  kwiver::vital::algo::draw_detected_object_set_sptr drawer = kwiver::vital::algo::draw_detected_object_set::create("ocv");
  drawer->set_configuration(drawer->get_configuration());// This will default the configuration 
#endif

  while (video_reader->next_frame(ts))
  {
    // Get the next frame and its associated data
    frame = video_reader->frame_image();
    if (!video_traits.capability(kwiver::vital::algo::video_input::HAS_FRAME_DATA))
    {
      throw kwiver::vital::video_stream_exception("Video reader selected does not supply image data.");
    }

    // Compute the frame number
    if (video_traits.capability(kwiver::vital::algo::video_input::HAS_FRAME_NUMBERS))
    {
      frame_number = ts.get_frame();
    }
    else
    {
      ++frame_number;
      ts.set_frame(frame_number);
    }

    // Compute the frame time
    if (!video_traits.capability(kwiver::vital::algo::video_input::HAS_FRAME_TIME))
    {
      // create an internal time standard
      frame_time = frame_number * default_frame_time_step_usec;
      ts.set_time_usec(frame_time);
    }

    // If this reader/video does not have any metadata, we will just
    // return an empty vector.  That is all handled by the algorithm
    // implementation.
    metadata = video_reader->frame_metadata();
    // Since we want to try to always return valid metadata for this
    // frame - if the returned metadata is empty, then use the last
    // one we received.  The requirement is to always provide the best
    // metadata for a frame. Since metadata appears less frequently
    // than the frames, the metadata returned can be a little old, but
    // it is still the best we have.
    if (metadata.empty())
    {
      // The saved one could be empty, but it is the bewt we have.
      metadata = last_metadata;
    }
    else
    {
      // Now that we have new metadata save it in case we need it later.
      last_metadata = metadata;
    }

    // Now do detections on this frame
    kwiver::vital::detected_object_set_sptr detections = detector->detect(frame);
    // Loop over the detections and append them to the kpf geometry file
    auto ie = detections->cend();
    for (auto det = detections->cbegin(); det != ie; ++det)
    {
      geom.clear();
      //geom.set_name?
      geom.set_track_id(detection_id);
      geom.set_detection_id(detection_id++);
      geom.set_frame_id(frame_number);
      geom.set_frame_time(frame_time);
      geom.set_confidence((*det)->confidence());
      for (std::string name : (*det)->type()->class_names())
        geom.get_classification()[name] = (*det)->type()->score(name);
      const kwiver::vital::bounding_box_d bbox((*det)->bounding_box());
      geom.set_bounding_box_pixels(bbox.min_x(), bbox.min_y(), bbox.max_x(), bbox.max_y());
      //geom.set_evaluation(diva_evaluation::true_positive);
      //geom.set_occlusion(diva_occlusion::heavy);
      //geom.set_source(diva_source::truth);
      geom.write(os);
    }// Loop to the next detection

#ifdef DISPLAY_FRAME
    // Draw the detections onto the image
    kwiver::vital::image_container_sptr detections_img = drawer->draw(detections, frame);
    // Let's see what it looks like
    cv::Mat _mat = kwiver::arrows::ocv::image_container::vital_to_ocv(detections_img->get_image());
    cv::namedWindow("Darknet Detections", cv::WINDOW_AUTOSIZE);// Create a window for display.
    cv::imshow("Darknet Detections", _mat);                     // Show our image inside it.
    cv::waitKey(5);
    kwiversys::SystemTools::Delay(2000);                                       // Wait for 2s
    cvDestroyWindow("Darknet Detections");
#endif
  }// Loop to the next frame
}

