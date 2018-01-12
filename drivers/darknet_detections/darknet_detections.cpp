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
#include "diva_experiment.h"
#include "diva_input.h"
#include "diva_exceptions.h"

// KWIVER Spcecific files to run darknet
#include "vital/exceptions.h"
#include "vital/types/image.h"
#include "vital/types/image_container.h"
#include "vital/types/detected_object.h"
#include "vital/types/detected_object_set.h"
#include "vital/algo/image_object_detector.h"
#include "vital/config/config_block.h"
#include "vital/config/config_block_io.h"
#include "vital/plugin_loader/plugin_manager.h"

//Uncomment this macro to draw detections on each frame and display it
#define DISPLAY_FRAME

#ifdef DISPLAY_FRAME
#include <kwiversys/SystemTools.hxx>
#include "opencv2/highgui/highgui.hpp"
#include "arrows/ocv/image_container.h"
#include "vital/algo/draw_detected_object_set.h"
#endif

int main(int argc, const char* argv[])
{
  diva_experiment exp;
  if (argc == 1)
  {// For this example driver, make the experiment in code if its not provided
    exp.set_type(diva_experiment::type::object_detection);
    exp.set_dataset_id("VIRAT_S_000206_06_001421_001458");
    if (true)
    {
      exp.set_input_type(diva_experiment::input_type::video);
      exp.set_input_source("VIRAT_S_000206_06_001421_001458.mp4");
    }
    else
    {
      exp.set_input_type(diva_experiment::input_type::file_list);
      exp.set_input_source("VIRAT_S_000206_06_001421_001458.txt");
    }
    exp.set_transport_type(diva_experiment::transport_type::disk);
    exp.set_frame_rate_Hz(30);
    exp.set_input_root_dir("C:/Programming/DIVA/src/data/darknet_detections");
    exp.set_output_type(diva_experiment::output_type::file);
    exp.set_output_root_dir("C:/Programming/DIVA/src/data/darknet_detections/outputs");
  }
  else if (argc == 2)
  {
    if (!exp.read_experiment(argv[1]))
      throw malformed_diva_data_exception("Invalid experiment configuration");
  }

  // Examine the experiment configuration and make sure we can run what it wants
  if(exp.get_type() != diva_experiment::type::object_detection)
    throw malformed_diva_data_exception("The calculator can only process object_detection experiments");

  // Create a stream/file to write our dectections to
  std::filebuf fb;
  fb.open(exp.get_output_filename() +"_geom.kpf", std::ios::out | std::ofstream::trunc);
  std::ostream os(&fb);

  // Initialize KWIVER
  kwiver::vital::plugin_manager::instance().load_all_plugins();
  // Instantiate Darknet KWIVER arrow
  kwiver::vital::algo::image_object_detector_sptr detector = kwiver::vital::algo::image_object_detector::create("darknet");
  // Load our own configuration file, assume its in the same location as the experiment data
  kwiver::vital::config_block_sptr config = kwiver::vital::read_config_file(exp.get_input_root_dir() + "/darknet.config");
  detector->set_configuration(config);
#ifdef DISPLAY_FRAME
  kwiver::vital::algo::draw_detected_object_set_sptr drawer = kwiver::vital::algo::draw_detected_object_set::create("ocv");
  drawer->set_configuration(drawer->get_configuration());// This will default the configuration 
#endif

  // Meta kpf packet to provide some commentary in our geomerty kpf file
  diva_meta meta;
  meta.set_msg("darknet geometry");
  meta.write(os);
  // Create a geometry kfp packet we will reuse for each frame
  diva_geometry geom;

  // Load the input
  diva_input input;
  if(!input.load_experiment(exp))
    throw malformed_diva_data_exception("Something happend in loading the experiment input");

  kwiver::vital::timestamp ts;
  kwiver::vital::image_container_sptr frame;
  size_t detection_id = 0; // Incremented for every detection on every frame
  while (input.has_next_frame())
  {
    frame = input.get_next_frame();
    ts = input.get_next_frame_timestamp();

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
      geom.set_frame_id(ts.get_frame());
      geom.set_frame_time(ts.get_time_usec());
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
     // Draw the detections onto the image and show it via kwiver and the opencv api
    kwiver::vital::image_container_sptr detections_img = drawer->draw(detections, frame);
    // Let's see what it looks like
    cv::Mat _mat = kwiver::arrows::ocv::image_container::vital_to_ocv(detections_img->get_image());
    cv::namedWindow("Darknet Detections", cv::WINDOW_AUTOSIZE);// Create a window for display.
    cv::imshow("Darknet Detections", _mat);                     // Show our image inside it.
    cv::waitKey(5);
    kwiversys::SystemTools::Delay(2000);                                       // Wait for 2s
    cvDestroyWindow("Darknet Detections");
#endif
  }// loop to the next frame
}

