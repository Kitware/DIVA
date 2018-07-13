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

#include <sstream>
#include "diva_geometry.h"
#include "diva_label.h"
#include "diva_activity.h"
#include "diva_experiment.h"

int main(int argc, const char* argv[])
{
  diva_meta meta;// We will reuse this

  // Example of Detection/Track Logic creating a geometry file
  diva_geometry geom;
  std::stringstream geom_ss;

  meta.set_msg("Example geometry");
  meta.write(geom_ss);
  meta.set_msg("1 tracks; 50 detection");
  meta.write(geom_ss);
  meta.set_msg("min / max frame: 0 942 min / max timestamp: 0 471 ");
  meta.write(geom_ss);
  meta.set_msg("min / max geometry: 0,289 - 1278 719 ( 1279x431+0+289 )");
  meta.write(geom_ss);

  double time_s = 0;
  for (size_t i = 0; i < 50; i++)
  {
    geom.clear();
    geom.set_track_id(66);
    geom.set_detection_id(0);
    geom.set_frame_id(i);
    geom.set_frame_time(time_s);
    geom.set_evaluation(diva_geometry::evaluation::true_positive);
    geom.set_occlusion(diva_geometry::occlusion::mostly);
    geom.set_source(diva_geometry::source::truth);
    geom.set_bounding_box_pixels(104, 349, 210, 385);
    geom.get_polygon().push_back(std::pair<size_t, size_t>(100, 399));
    geom.get_polygon().push_back(std::pair<size_t, size_t>(200, 398));
    geom.get_polygon().push_back(std::pair<size_t, size_t>(300, 397));
    geom.write(geom_ss);
    time_s += 0.1;
  }
  meta.set_msg("eof");
  meta.write(geom_ss);
  std::cout << geom_ss.str() << std::endl;

  // Example of writing a label/classification file
  diva_label label;
  std::stringstream label_ss;

  meta.set_msg("Example type labels");
  meta.write(label_ss);
  meta.set_msg("Dumpsters 1");
  meta.write(label_ss);
  meta.set_msg("Vehicle 1 ");

  label.set_track_id(66);
  label.add_classification("Dumpster",1.0);
  label.write(label_ss);
  label.set_track_id(67);
  label.add_classification("Vehicle",1.0);
  label.write(label_ss);
  meta.set_msg("eof");
  meta.write(label_ss);
  std::cout << label_ss.str() << std::endl;

  // Example of writing an activity file
  diva_activity actv;
  std::stringstream actv_ss;

  meta.set_msg("Example activity");
  meta.write(actv_ss);
  meta.set_msg("vehicle_moving 2 instances");
  meta.write(actv_ss);
  meta.set_msg("activity_gesturing 0 instances");
  meta.write(actv_ss);

  actv.set_activity_names( {{std::string("vehicle_moving"), 1.0}} );
  actv.set_activity_id(1);
  actv.set_source(diva_activity::source::truth);
  // Overall timeframe of the activity
  actv.get_frame_id_span().push_back(std::pair<double, double>(2135, 2456));
  actv.get_frame_id_span().push_back(std::pair<double, double>(2479, 2503));
  // Specific actors in this activity, and their associated frames
  std::vector<std::pair<double, double>>& track_55_times = actv.get_actor_frame_id_span()[55];
  track_55_times.push_back(std::pair<double, double>(2135, 2344));
  track_55_times.push_back(std::pair<double, double>(2479, 2496));
  std::vector<std::pair<double, double>>& track_44_times = actv.get_actor_frame_id_span()[44];
  track_44_times.push_back(std::pair<double, double>(2267, 2456));
  track_44_times.push_back(std::pair<double, double>(2488, 2503));
  actv.write(actv_ss);

  //actv.clear();
  //actv.set_activity_name("vehicle_moving");
  //actv.set_activity_id(2);
  //actv.set_source(diva_source::truth);
  //// Overall timeframe of the activity
  //actv.get_frame_id_span().push_back(std::pair<size_t, size_t>(2135, 2456));
  //actv.get_frame_id_span().push_back(std::pair<size_t, size_t>(2479, 2503));
  //// Specific actors in this activity, and their associated frames
  //std::vector<std::pair<size_t, size_t>>& track_11_times = actv.get_actor_frame_id_span()[11];
  //track_11_times.push_back(std::pair<size_t, size_t>(2135, 2344));
  //track_11_times.push_back(std::pair<size_t, size_t>(2479, 2496));
  //std::vector<std::pair<size_t, size_t>>& track_22_times = actv.get_actor_frame_id_span()[22];
  //track_22_times.push_back(std::pair<size_t, size_t>(2267, 2456));
  //track_22_times.push_back(std::pair<size_t, size_t>(2488, 2503));
  //actv.write(actv_ss);

  meta.set_msg("eof");
  meta.write(actv_ss);
  std::cout << actv_ss.str() << std::endl;

  // Example of writing an experiment file
  diva_experiment exp;
  std::stringstream exp_ss;

  // This is a sample experiment file for the DIVA system.
  // This file can be used for
  //    1) Running and experiment
  //    2) Scoring the results of the experiment

  // What is the purpose of this experiment?
  exp.set_type(diva_experiment::type::object_detection);

  // Describe the inputs :
  // the dataset ID is used as the prefix for output files
  exp.set_dataset_id("VIRAT_S_000206_04_000710_000779");
  // frame_rate_Hz metadata; available via the API if you want it
  exp.set_frame_rate_Hz(30);
  // set how the input type is made available
  exp.set_transport_type(diva_experiment::transport_type::disk);
  // local path to the input data
  exp.set_input_root_dir("./etc/");
  // input source type
  exp.set_input_type(diva_experiment::input_type::file_list);
  // the instance of the input source, in this case, a file,
  // located in ${root_dir}/${source}, with filepaths of images to be processed.
  exp.set_input_source("image_list.txt");

  // Describe the outputs :
  // How will your algorithm's output be transported?
  exp.set_output_type(diva_experiment::output_type::file);
  // Where will the output be written?
  exp.set_output_root_dir("./etc/algo-out");

  // Scoring Configuration
  // Where is the scoring executable
  exp.set_score_events_executable("./bin/score_events");
  // What file do we score against
  exp.set_scoring_reference_geometry("./etc/ref-geom/VIRAT_S_000206_04_000710_000779.reduced.geom.yml");
  // Where does the scoring evaluation go?
  exp.set_scoring_evaluation_output_dir("./etc/eval-out");
  // For scoring object detections :
  // The reference labels file
  exp.set_scoring_object_detection_reference_types("./etc/ref-geom/VIRAT_S_000206_04_000710_000779.types.yml");
  // The target label to score
  exp.set_scoring_object_detection_target("Person");
  // Set the IOU
  exp.set_scoring_object_detection_iou("0.5");
  // Set the time window
  exp.set_scoring_object_detection_time_window("25:75");

  std::cout << exp.to_string() << std::endl;
}
