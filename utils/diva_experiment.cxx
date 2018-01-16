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
#include "vital/config/config_block.h"
#include "vital/config/config_block_io.h"

class diva_experiment::pimpl
{
public:
  diva_experiment::type            type;
  diva_experiment::input_type      input_type;
  diva_experiment::transport_type  transport_type;
  std::string                      dataset_id;
  std::string                      input_source;
  std::string                      input_root_dir;
  diva_experiment::output_type     output_type;
  std::string                      output_root_dir;

  size_t                           frame_rate_Hz = 30;
  std::string                      source_filepath = "";
  std::string                      output_prefix = "";

  kwiver::vital::config_block_sptr config;
};

diva_experiment::diva_experiment()
{
  _pimpl = new pimpl();
  _pimpl->config = kwiver::vital::config_block::empty_config("diva_experiment");
}

diva_experiment::~diva_experiment()
{
  delete _pimpl;
}

void diva_experiment::clear()
{
  remove_type();
  remove_input_type();
  remove_transport_type();
  remove_dataset_id();
  remove_input_source();
  remove_input_root_dir();
  remove_frame_rate_Hz();
  remove_output_type();
  remove_output_root_dir();
}

bool diva_experiment::is_valid()
{
  if (!has_type())
    return false;
  if (!has_input_type())
    return false;
  if (!has_transport_type())
    return false;
  if (!has_dataset_id())
    return false;
  if (!has_input_source())
    return false;
  if (!has_input_root_dir())
    return false;
  if (!has_frame_rate_Hz())
    return false;
  if (!has_output_type())
    return false;
  if (!has_output_root_dir())
    return false;
  if (_pimpl->transport_type == diva_experiment::transport_type::rstp && _pimpl->input_type != diva_experiment::input_type::video)
    return false;
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

  if (_pimpl->config->has_value("input:dataset_id"))
    set_dataset_id(_pimpl->config->get_value<std::string>("input:dataset_id"));
  if (_pimpl->config->has_value("input:type"))
  {
    std::string t = _pimpl->config->get_value<std::string>("input:type");
    if (t == "file_list")
      set_input_type( diva_experiment::input_type::file_list);
    else if (t == "video")
      set_input_type( diva_experiment::input_type::video);
  }
  if (_pimpl->config->has_value("input:transport_type"))
  {
    std::string t = _pimpl->config->get_value<std::string>("input:transport_type");
    if (t == "disk")
      set_transport_type( diva_experiment::transport_type::disk);
    else if (t == "girder")
      set_transport_type( diva_experiment::transport_type::girder);
    else if (t == "rstp")
      set_transport_type( diva_experiment::transport_type::rstp);
  }
  if (_pimpl->config->has_value("input:source"))
    set_input_source(_pimpl->config->get_value<std::string>("input:source"));
  if (_pimpl->config->has_value("input:root_dir"))
    set_input_root_dir(_pimpl->config->get_value<std::string>("input:root_dir"));
  if (_pimpl->config->has_value("input:frame_rate_Hz"))
    set_frame_rate_Hz(_pimpl->config->get_value<size_t>("input:frame_rate_Hz"));

  if (_pimpl->config->has_value("output:type"))
  {
    std::string t = _pimpl->config->get_value<std::string>("output:type");
    if (t == "file")
      set_output_type( diva_experiment::output_type::file);
  }
  if (_pimpl->config->has_value("output:root_dir"))
    set_output_root_dir(_pimpl->config->get_value<std::string>("output:root_dir"));

  return is_valid();
}
bool diva_experiment::write_experiment(const std::string& filename)
{
  if (!is_valid())
    return false;
  kwiver::vital::write_config_file(_pimpl->config, filename);
  return true;
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

bool diva_experiment::has_input_type() const
{
  return _pimpl->input_type != ( diva_experiment::input_type)-1;
}
 diva_experiment::input_type diva_experiment::get_input_type() const
{
  return _pimpl->input_type;
}
void diva_experiment::set_input_type( diva_experiment::input_type e)
{
  _pimpl->input_type = e;
  switch (e)
  {
  case  diva_experiment::input_type::file_list:
    _pimpl->config->set_value<std::string>("input:type", "file_list");
    return;
  case  diva_experiment::input_type::video:
    _pimpl->config->set_value<std::string>("input:type", "video");
    return;
  }
}
void diva_experiment::remove_input_type()
{
  _pimpl->input_type = ( diva_experiment::input_type)-1;
  if (_pimpl->config->has_value("input:type"))
    _pimpl->config->unset_value("input:type");
}

bool diva_experiment::has_transport_type() const
{
  return _pimpl->transport_type != ( diva_experiment::transport_type)-1;
}
 diva_experiment::transport_type diva_experiment::get_transport_type() const
{
  return _pimpl->transport_type;
}
void diva_experiment::set_transport_type( diva_experiment::transport_type e)
{
  _pimpl->transport_type = e;
  switch (e)
  {
  case  diva_experiment::transport_type::disk:
    _pimpl->config->set_value<std::string>("input:transport_type", "disk");
    return;
  case  diva_experiment::transport_type::girder:
    _pimpl->config->set_value<std::string>("input:transport_type", "girder");
    return;
  case  diva_experiment::transport_type::rstp:
    _pimpl->config->set_value<std::string>("input:transport_type", "rstp");
    return;
  }
}
void diva_experiment::remove_transport_type()
{
  _pimpl->transport_type = ( diva_experiment::transport_type)-1;
  if (_pimpl->config->has_value("input:transport_type"))
    _pimpl->config->unset_value("input:transport_type");
}

bool diva_experiment::has_dataset_id() const
{
  return !_pimpl->dataset_id.empty();
}
void diva_experiment::set_dataset_id(const std::string& src)
{
  _pimpl->dataset_id = src;
  _pimpl->config->set_value<std::string>("input:dataset_id", src);
}
std::string diva_experiment::get_dataset_id() const
{
  return _pimpl->dataset_id;
}
void diva_experiment::remove_dataset_id()
{
  _pimpl->dataset_id = "";
  if (_pimpl->config->has_value("input:dataset_id"))
    _pimpl->config->unset_value("input:dataset_id");
}

bool diva_experiment::has_frame_rate_Hz() const
{
  return _pimpl->frame_rate_Hz > 0;
}
void diva_experiment::set_frame_rate_Hz(size_t hz)
{
  _pimpl->frame_rate_Hz = hz;
  _pimpl->config->set_value<size_t>("input:frame_rate_Hz", hz);
}
size_t diva_experiment::get_frame_rate_Hz() const
{
  return _pimpl->frame_rate_Hz;
}
void diva_experiment::remove_frame_rate_Hz()
{
  _pimpl->frame_rate_Hz = 0;
  if (_pimpl->config->has_value("input:frame_rate_Hz"))
    _pimpl->config->unset_value("input:frame_rate_Hz");
}

bool diva_experiment::has_input_source() const
{
  return !_pimpl->input_source.empty();
}
void diva_experiment::set_input_source(const std::string& src)
{
  _pimpl->input_source = src;
  _pimpl->config->set_value<std::string>("input:source", src);
}
std::string diva_experiment::get_input_source() const
{
  return _pimpl->input_source;
}
void diva_experiment::remove_input_source()
{
  _pimpl->input_source = "";
  if (_pimpl->config->has_value("input:source"))
    _pimpl->config->unset_value("input:source");
}

bool diva_experiment::has_input_root_dir() const
{
  return !_pimpl->input_root_dir.empty();
}
void diva_experiment::set_input_root_dir(const std::string& src)
{
  _pimpl->input_root_dir = src;
  _pimpl->config->set_value<std::string>("input:root_dir", src);
}
std::string diva_experiment::get_input_root_dir() const
{
  return _pimpl->input_root_dir;
}
void diva_experiment::remove_input_root_dir()
{
  _pimpl->input_root_dir = "";
  if (_pimpl->config->has_value("input:root_dir"))
    _pimpl->config->unset_value("input:root_dir");
}

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
  return _pimpl->output_root_dir + "/" + _pimpl->dataset_id;
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
