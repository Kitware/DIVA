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

#include "kpf_experiment.h"
#include <yaml-cpp/yaml.h>

#include <arrows/kpf/yaml/kpf_reader.h>
#include <arrows/kpf/yaml/kpf_yaml_parser.h>
#include <arrows/kpf/yaml/kpf_yaml_writer.h>
#include <arrows/kpf/yaml/kpf_canonical_io_adapter.h>

struct kpf_geom
{
  size_t         _detection_id;
  size_t         _track_id;
  size_t         _frame_id;
  double         _bbox_x1;
  double         _bbox_y1;
  double         _bbox_x2;
  double         _bbox_y2;
  double         _poly_x1;
  double         _poly_y1;
  double         _poly_x2;
  double         _poly_y2;
  kpf::source    _source;
  kpf::occlusion _occlusion;
  kpf::eval      _eval;
  kpf::keyframe  _keyframe;

  bool           _has_detection_id;
  bool           _has_track_id;
  bool           _has_frame_id;

  void Clear()
  {
    _has_detection_id = false;
    _has_track_id = false;
    _has_frame_id = false;
    _bbox_x1 = -1; _bbox_y1 = -1;
    _bbox_x2 = -1; _bbox_y2 = -1;
    _poly_x1 = -1; _poly_y1 = -1;
    _poly_x2 = -1; _poly_y2 = -1;
    _source = (kpf::source)-1;
    _occlusion = (kpf::occlusion)-1;
    _eval = (kpf::eval)-1;
    _keyframe = (kpf::keyframe)-1;
  }
};

class diva_experiment::pimpl
{
public:
  size_t      frame_rate_Hz = 0;
  std::string source = "";
  std::string output = "";
};

diva_experiment::diva_experiment()
{
  _pimpl = new pimpl();
}

diva_experiment::~diva_experiment()
{
  delete _pimpl;
}

bool diva_experiment::is_valid()
{
  // Make sure source and output are defined and point to something that exists?
  return true;
}

bool diva_experiment::has_next_frame()
{
  return true;
}

kwiver::vital::image_container_sptr diva_experiment::get_next_frame()
{
  return kwiver::vital::image_container_sptr(nullptr);
}

bool diva_experiment::read_experiment(const std::string& file_name)
{
  YAML::Node config = YAML::LoadFile(file_name);
  _pimpl->frame_rate_Hz = config["frame_rate_Hz"].as<size_t>();
  _pimpl->source = config["source"].as<std::string>();
  _pimpl->output = config["output"].as<std::string>();

  return is_valid();
}
void diva_experiment::write_experiment(const std::string& file_name)
{

}


void diva_experiment::set_frame_rate_Hz(size_t hz)
{
  _pimpl->frame_rate_Hz = hz;
}
size_t diva_experiment::get_frame_rate_Hz()
{
  return _pimpl->frame_rate_Hz;
}

void diva_experiment::set_source(const std::string& src)
{
  _pimpl->source = src;
}
std::string& diva_experiment::get_source()
{
  return _pimpl->source;
}

void diva_experiment::set_kpf_output(const std::string& dst)
{
  _pimpl->output = dst;
}
std::string& diva_experiment::get_kpf_output()
{
  return _pimpl->output;
}

