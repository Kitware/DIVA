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

#include "diva_experiment.h"
#include <yaml-cpp/yaml.h>
#include <vital/config/config_block.h>
#include <vital/config/config_block_io.h>

class diva_experiment::pimpl
{
public:

  diva_experiment::type            type;

  diva_input_sptr                  input;
  
  diva_experiment::output_type     output_type;
  std::string                      output_root_dir;
  std::string                      output_prefix = "";
  
  std::string                      score_events_executable = "";
  std::string                      scoring_reference_geometry = "";
  std::string                      scoring_evaluation_output_dir = "";
  std::string                      scoring_object_detection_reference_types = "";
  std::string                      scoring_object_detection_reference_target;
  std::string                      scoring_object_detection_iou = "";
  std::string                      scoring_object_detection_time_window = "";
  
  std::string                      algorithm_executable = "";
  kwiver::vital::config_block_sptr config;
};

diva_experiment::diva_experiment()
{
  _pimpl = new pimpl();
  _pimpl->config = kwiver::vital::config_block::empty_config("diva_experiment");
  _pimpl->input = std::make_shared<diva_input>();
  _pimpl->input->set_configuration(_pimpl->config);
}

diva_experiment::~diva_experiment()
{
  delete _pimpl;
}

void diva_experiment::clear()
{
  remove_type();
  _pimpl->input->clear();
  
  remove_output_type();
  remove_output_root_dir();
  
  remove_score_events_executable();
  remove_scoring_reference_geometry();
  remove_scoring_evaluation_output_dir();
  remove_scoring_object_detection_reference_types();
  remove_scoring_object_detection_target();
  remove_scoring_object_detection_iou();
  remove_scoring_object_detection_time_window();
  
  remove_algorithm_executable();
  // TODO clear algorithm parameter
}

bool diva_experiment::is_valid()
{
  if (!has_type())
  {
    std::cerr << "Experiment invalid: Does not have type" << std::endl;
    return false;
  }
  if (!_pimpl->input->is_valid())
  {
    std::cerr << "Experiment invalid: Input objec is not valid" << std::endl;
    return false;
  }
  if (!has_output_type())
  {
    std::cerr << "Experiment invalid: Does not have ouput type" << std::endl;
    return false;
  }
  if (!has_output_root_dir())
  {
    std::cerr << "Experiment invalid: Does not have output root dir" << std::endl;
    return false;
  }
  // TODO more checks for directories and files exist... 
  return true;
}

bool diva_experiment::read_experiment(const std::string& filename)
{
  clear();
  _pimpl->config = kwiver::vital::read_config_file(filename);
  if (_pimpl->config->has_value("type"))
  {
    std::string t = _pimpl->config->get_value<std::string>("type");
    if (t == "activity_detection")
      set_type(diva_experiment::type::activity_detection);
    else if (t == "object_detection")
      set_type( diva_experiment::type::object_detection);
  }

  _pimpl->input->read(_pimpl->config);

  if (_pimpl->config->has_value("output:type"))
  {
    std::string t = _pimpl->config->get_value<std::string>("output:type");
    if (t == "file")
      set_output_type( diva_experiment::output_type::file);
  }
  if (_pimpl->config->has_value("output:root_dir"))
    set_output_root_dir(_pimpl->config->get_value<std::string>("output:root_dir"));

  if (_pimpl->config->has_value("scoring:score_events"))
    set_score_events_executable(_pimpl->config->get_value<std::string>("scoring:score_events"));
  if (_pimpl->config->has_value("scoring:ref_geom"))
    set_scoring_reference_geometry(_pimpl->config->get_value<std::string>("scoring:ref_geom"));
  if (_pimpl->config->has_value("scoring:eval_output_dir"))
    set_scoring_evaluation_output_dir(_pimpl->config->get_value<std::string>("scoring:eval_output_dir"));
  if (_pimpl->config->has_value("scoring:object_detection:ref_types"))
    set_scoring_object_detection_reference_types(_pimpl->config->get_value<std::string>("scoring:object_detection:ref_types"));
  if (_pimpl->config->has_value("scoring:object_detection:target"))
    set_scoring_object_detection_target(_pimpl->config->get_value<std::string>("scoring:object_detection:target"));
  if (_pimpl->config->has_value("scoring:object_detection:iou"))
    set_scoring_object_detection_iou(_pimpl->config->get_value<std::string>("scoring:object_detection:iou"));
  if (_pimpl->config->has_value("scoring:object_detection:time_window"))
    set_scoring_object_detection_time_window(_pimpl->config->get_value<std::string>("scoring:object_detection:time_window"));

  if (_pimpl->config->has_value("output:root_dir"))
    set_algorithm_executable(_pimpl->config->get_value<std::string>("algo:command"));

  return is_valid();
}
bool diva_experiment::write_experiment(const std::string& filename)
{
  if (!is_valid())
    return false;
  kwiver::vital::write_config_file(_pimpl->config, filename);
  return true;
}

std::string diva_experiment::to_string() const
{
  std::stringstream str;
  kwiver::vital::write_config(_pimpl->config, str);
  return str.str();
}

bool diva_experiment::has_type() const
{
  return _pimpl->type != ( diva_experiment::type)-1;
}
 diva_experiment::type diva_experiment::get_type() const
{
  return _pimpl->type;
}
void diva_experiment::set_type( diva_experiment::type e)
{
  _pimpl->type = e;
  switch (e)
  {
  case  diva_experiment::type::activity_detection:
    _pimpl->config->set_value<std::string>("type","activity_detection");
    return;
  case  diva_experiment::type::object_detection:
    _pimpl->config->set_value<std::string>("type","object_detection");
    return;
  }
}
void diva_experiment::remove_type()
{
  _pimpl->type = ( diva_experiment::type)-1;
  if(_pimpl->config->has_value("type"))
    _pimpl->config->unset_value("type");
}


bool diva_experiment::has_input() const
{
  return _pimpl->input->is_valid();
}
diva_input_sptr diva_experiment::get_input()
{
  return _pimpl->input;
}
//const diva_input& diva_experiment::get_input() const
//{
//  return *_pimpl->input.get();
//}

bool diva_experiment::has_output_type() const
{
  return _pimpl->output_type != ( diva_experiment::output_type)-1;
}
 diva_experiment::output_type diva_experiment::get_output_type() const
{
  return _pimpl->output_type;
}
void diva_experiment::set_output_type( diva_experiment::output_type e)
{
  _pimpl->output_type = e;
  switch (e)
  {
  case  diva_experiment::output_type::file:
    _pimpl->config->set_value<std::string>("output:type", "file");
    return;
  }
}
void diva_experiment::remove_output_type()
{
  _pimpl->output_type = ( diva_experiment::output_type)-1;
  if (_pimpl->config->has_value("output:type"))
    _pimpl->config->unset_value("output:type");
}

bool diva_experiment::has_output_root_dir() const
{
  return !_pimpl->output_root_dir.empty();
}
void diva_experiment::set_output_root_dir(const std::string& src)
{
  _pimpl->output_root_dir = src;
  _pimpl->config->set_value<std::string>("output:root_dir", src);
}
std::string diva_experiment::get_output_root_dir() const
{
  return _pimpl->output_root_dir;
}
void diva_experiment::remove_output_root_dir()
{
  _pimpl->output_root_dir = "";
  if (_pimpl->config->has_value("output:root_dir"))
    _pimpl->config->unset_value("output:root_dir");
}

std::string diva_experiment::get_output_prefix() const
{
  return _pimpl->output_root_dir + "/" + _pimpl->input->get_dataset_id();
}

bool diva_experiment::has_score_events_executable() const
{
  return !_pimpl->score_events_executable.empty();
}
void diva_experiment::set_score_events_executable(const std::string& src)
{
  _pimpl->score_events_executable = src;
  _pimpl->config->set_value<std::string>("scoring:score_events", src);
}
std::string diva_experiment::get_score_events_executable() const
{
  return _pimpl->score_events_executable;
}
void diva_experiment::remove_score_events_executable()
{
  _pimpl->score_events_executable = "";
  if (_pimpl->config->has_value("scoring:score_events"))
    _pimpl->config->unset_value("scoring:score_events");
}

bool diva_experiment::has_scoring_reference_geometry() const
{
  return !_pimpl->scoring_reference_geometry.empty();
}
void diva_experiment::set_scoring_reference_geometry(const std::string& src)
{
  _pimpl->scoring_reference_geometry = src;
  _pimpl->config->set_value<std::string>("scoring:ref_geom", src);
}
std::string diva_experiment::get_scoring_reference_geometry() const
{
  return _pimpl->scoring_reference_geometry;
}
void diva_experiment::remove_scoring_reference_geometry()
{
  _pimpl->scoring_reference_geometry = "";
  if (_pimpl->config->has_value("scoring:ref_geom"))
    _pimpl->config->unset_value("scoring:ref_geom");
}

bool diva_experiment::has_scoring_evaluation_output_dir() const
{
  return !_pimpl->scoring_evaluation_output_dir.empty();
}
void diva_experiment::set_scoring_evaluation_output_dir(const std::string& src)
{
  _pimpl->scoring_evaluation_output_dir = src;
  _pimpl->config->set_value<std::string>("scoring:eval_output_dir", src);
}
std::string diva_experiment::get_scoring_evaluation_output_dir() const
{
  return _pimpl->scoring_evaluation_output_dir;
}
void diva_experiment::remove_scoring_evaluation_output_dir()
{
  _pimpl->scoring_evaluation_output_dir = "";
  if (_pimpl->config->has_value("scoring:eval_output_dir"))
    _pimpl->config->unset_value("scoring:eval_output_dir");
}

bool diva_experiment::has_scoring_object_detection_reference_types() const
{
  return !_pimpl->scoring_object_detection_reference_types.empty();
}
void diva_experiment::set_scoring_object_detection_reference_types(const std::string& src)
{
  _pimpl->scoring_object_detection_reference_types = src;
  _pimpl->config->set_value<std::string>("scoring:object_detection:ref_types", src);
}
std::string diva_experiment::get_scoring_object_detection_reference_types() const
{
  return _pimpl->scoring_object_detection_reference_types;
}
void diva_experiment::remove_scoring_object_detection_reference_types()
{
  _pimpl->scoring_object_detection_reference_types = "";
  if (_pimpl->config->has_value("scoring:object_detection:ref_types"))
    _pimpl->config->unset_value("scoring:object_detection:ref_types");
}

bool diva_experiment::has_scoring_object_detection_target() const
{
  return !_pimpl->scoring_object_detection_reference_target.empty();
}
void diva_experiment::set_scoring_object_detection_target(const std::string& src)
{
  _pimpl->scoring_object_detection_reference_target = src;
  _pimpl->config->set_value<std::string>("scoring:object_detection:target", src);
}
std::string diva_experiment::get_scoring_object_detection_target() const
{
  return _pimpl->scoring_object_detection_reference_target;
}
void diva_experiment::remove_scoring_object_detection_target()
{
  _pimpl->scoring_object_detection_reference_target = "";
  if (_pimpl->config->has_value("scoring:object_detection:target"))
    _pimpl->config->unset_value("scoring:object_detection:target");
}

bool diva_experiment::has_scoring_object_detection_iou() const
{
  return !_pimpl->scoring_object_detection_iou.empty();
}
void diva_experiment::set_scoring_object_detection_iou(const std::string& src)
{
  _pimpl->scoring_object_detection_iou = src;
  _pimpl->config->set_value<std::string>("scoring:object_detection:iou", src);
}
std::string diva_experiment::get_scoring_object_detection_iou() const
{
  return _pimpl->scoring_object_detection_iou;
}
void diva_experiment::remove_scoring_object_detection_iou()
{
  _pimpl->scoring_object_detection_iou = "";
  if (_pimpl->config->has_value("scoring:object_detection:iou"))
    _pimpl->config->unset_value("scoring:object_detection:iou");
}

bool diva_experiment::has_scoring_object_detection_time_window() const
{
  return !_pimpl->scoring_object_detection_time_window.empty();
}
void diva_experiment::set_scoring_object_detection_time_window(const std::string& src)
{
  _pimpl->scoring_object_detection_time_window = src;
  _pimpl->config->set_value<std::string>("scoring:object_detection:time_window", src);
}
std::string diva_experiment::get_scoring_object_detection_time_window() const
{
  return _pimpl->scoring_object_detection_time_window;
}
void diva_experiment::remove_scoring_object_detection_time_window()
{
  _pimpl->scoring_object_detection_time_window = "";
  if (_pimpl->config->has_value("scoring:object_detection:time_window"))
    _pimpl->config->unset_value("scoring:object_detection:time_window");
}

bool diva_experiment::has_algorithm_executable() const
{
  return !_pimpl->algorithm_executable.empty();
}
void diva_experiment::set_algorithm_executable(const std::string& src)
{
  _pimpl->algorithm_executable = src;
  _pimpl->config->set_value<std::string>("algo:command", src);
}
std::string diva_experiment::get_algorithm_executable() const
{
  return _pimpl->algorithm_executable;
}
void diva_experiment::remove_algorithm_executable()
{
  _pimpl->algorithm_executable = "";
  if (_pimpl->config->has_value("algo:command"))
    _pimpl->config->unset_value("algo:command");
}

void diva_experiment::set_algorithm_parameter( const std::string& key, const std::string& val )
{
  _pimpl->config->set_value< std::string >( "algo:"+key, val );
}
std::string diva_experiment::get_algorithm_parameter( const std::string& key ) const
{
  return
    _pimpl->config->has_value( "algo:"+key )
    ? _pimpl->config->get_value< std::string >( "algo:"+key )
    : "";
}
