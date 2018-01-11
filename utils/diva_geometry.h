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

#pragma once
#include "diva_packet.h"


class diva_geometry_impl;

class DIVA_UTILS_EXPORT diva_geometry : public diva_packet
{
public:

  enum class source
  {
    truth = 0
  };

  enum class occlusion
  {
    medium = 0,
    heavy
  };

  enum class evaluation
  {
    true_positive = 0,
    false_positive,
    false_alarm
  };

  enum class keyframe
  {
    yes = 0,
    no
  }; 

  struct bounding_box_pixels
  {
    size_t get_x1() const { return x1; }
    size_t get_y1() const { return y1; }
    size_t get_x2() const { return x2; }
    size_t get_y2() const { return y2; }
    size_t x1, y1, x2, y2;
  };

  diva_geometry();
  virtual ~diva_geometry();

  void clear();
  bool is_valid() const;

  bool has_detection_id() const;
  size_t get_detection_id() const;
  void set_detection_id(size_t id);
  void remove_detection_id();

  bool has_track_id() const;
  size_t get_track_id() const;
  void set_track_id(size_t id);
  void remove_track_id();
  
  bool has_frame_id() const;
  size_t get_frame_id() const;
  void set_frame_id(size_t id);
  void remove_frame_id();
  
  bool has_frame_time() const;
  double get_frame_time() const;
  void set_frame_time(double time_s);
  void remove_frame_time();

  bool has_frame_absolute_time() const;
  double get_frame_absolute_time() const;
  void set_frame_absolute_time(double time_us);
  void remove_frame_absolute_time();
  
  bool has_confidence() const;
  double get_confidence() const;
  void set_confidence(double conf);
  void remove_confidence();
  
  bool has_bounding_box_pixels() const;
  const bounding_box_pixels& get_bounding_box_pixels() const;
  void set_bounding_box_pixels(size_t x1, size_t y1, size_t x2, size_t y2);
  void remove_bounding_box_pixels();
  
  bool has_source() const;
  source get_source() const;
  void set_source(source s);
  void remove_source();

  bool has_evaluation() const;
  evaluation get_evaluation() const;
  void set_evaluation(evaluation e);
  void remove_evaluation();

  bool has_occlusion() const;
  occlusion get_occlusion() const;
  void set_occlusion(occlusion o);
  void remove_occlusion();

  bool has_keyframe() const;
  keyframe get_keyframe() const;
  void set_keyframe(keyframe kf);
  void remove_keyframe();

  bool has_classification() const;
  std::map<std::string,double>& get_classification();
  const std::map<std::string, double>& get_classification() const;
  void add_classification(const std::string& name, double probability);
  void remove_classification();
  
  bool has_polygon() const;
  std::vector<std::pair<size_t, size_t>>& get_polygon();
  const std::vector<std::pair<size_t, size_t>>& get_polygon() const;
  void add_polygon_point(const std::pair<size_t, size_t>&);
  void remove_polygon();

  void write(std::ostream& os) const;
  std::string to_string() const;
private:
  diva_geometry_impl* _pimpl;
};
