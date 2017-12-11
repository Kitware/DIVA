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
#include <vital/exceptions/base.h>
#include <vital/types/image_container.h>

class malformed_kpf_exception : public kwiver::vital::vital_core_base_exception
{
public:
  /** param message     Description of the parsing circumstances */
  malformed_kpf_exception(std::string const& message) VITAL_NOTHROW;
  virtual ~malformed_kpf_exception() VITAL_NOTHROW;
  /// Given error message string
  std::string m_message;
};

class kpf_box
{
  kpf_box();
  kpf_box(double x1, double y1, double x2, double y2);
};

enum class kpf_source
{
  truth = 0
};

enum class kpf_occlusion
{
  medium = 0,
  heavy
};

enum class kpf_evaluation
{
  true_positive = 0,
  false_positive,
  false_alarm
};

enum class kpf_keyframe
{
  yes = 0,
  no
};

class kpf_packet
{
public:
  virtual ~kpf_packet() {};

  virtual void clear() = 0;
  virtual bool is_valid() = 0;

  virtual void write(std::ostream& os) = 0;
};

class kpf_meta :  public kpf_packet
{
public:
  kpf_meta(const std::string& msg);
  virtual ~kpf_meta();

  void clear();
  bool is_valid();

  void set_msg(const std::string& msg);

  void write(std::ostream& os);

private:
  class pimpl;
  pimpl* _pimpl;
};

class diva_geometry : public kpf_packet
{
public:
  diva_geometry();
  virtual ~diva_geometry();

  void clear();
  bool is_valid();

  void set_detection_id(size_t detection_id);
  void set_track_id(size_t detection_id);
  void set_frame_id(size_t detection_id);
  void set_frame_time(double time_s);
  void set_absolute_time(double time_us);

  void set_bounding_box_pixels(size_t x1, size_t y1, size_t x2, size_t y2);
  void set_source(kpf_source src);
  void set_evaluation(kpf_evaluation src);
  void set_occlusion(kpf_occlusion src);
  void set_keyframe(kpf_keyframe src);
  void set_polygon_pixels(size_t x1, size_t y1, size_t x2, size_t y2);

  void write(std::ostream& os);
private:
  class pimpl;
  pimpl* _pimpl;
};

class diva_label : public kpf_packet
{
public:
  diva_label();
  virtual ~diva_label();

  void clear();
  bool is_valid();

  void set_track_id(size_t track_id);
  void set_label(const std::string& label);

  void write(std::ostream& os);
private:
  class pimpl;
  pimpl* _pimpl;
};

class diva_activity : public kpf_packet
{
public:
  diva_activity();
  virtual ~diva_activity();

  void clear();
  bool is_valid();

  void set_activity_id(size_t activity_id);
  void set_label(const std::string& label);
  void set_source(kpf_source src);
  void set_time_span(double start_time, double end_time);
  void add_actor_frame_span(size_t track_id, size_t start_frame, size_t end_frame);
  void add_actor_time_span(size_t track_id, double start_time_s, double end_time_s);
  void add_actor_absolute_time_span(size_t track_id, double start_time_us, double end_time_us);

  void write(std::ostream& os);
private:
  class pimpl;
  pimpl* _pimpl;
};

class diva_region : public kpf_packet
{
public:
  diva_region();
  virtual ~diva_region();

  bool is_valid();

  void set_label(size_t activity_id, const std::string& label);
  void set_source(size_t activity_id, kpf_source src);
  void set_time_span(size_t activity_id, double start_time, double end_time);
  void add_actor_time_span(size_t activity_id, size_t track_id, double start_time, double end_time);

  void write(std::ostream& os);
private:
  class pimpl;
  pimpl* _pimpl;
};


class diva_experiment
{
public:
  diva_experiment();
  virtual ~diva_experiment();

  bool is_valid();

  bool read_experiment(const std::string& file_name);
  void write_experiment(const std::string& file_name);

  // The experiment properties
  void set_frame_rate_Hz(size_t hz);
  size_t get_frame_rate_Hz();

  void set_source(const std::string& src);
  std::string& get_source();

  void set_kpf_output(const std::string& dst);
  std::string& get_kpf_output();

  bool has_next_frame();
  kwiver::vital::image_container_sptr get_next_frame();

private:
  class pimpl;
  pimpl* _pimpl;
};

