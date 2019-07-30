/*ckwg +29
* Copyright 2017-2018 by Kitware, Inc.
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

#include "diva_input.h"
#include <yaml-cpp/yaml.h>
#include <vital/types/image.h>
#include <vital/types/image_container.h>
#include <vital/algo/video_input.h>
#include <vital/algo/image_io.h>
#include <vital/util/data_stream_reader.h>
#include <vital/config/config_block.h>
#include <vital/config/config_block_io.h>
#include <vital/logger/logger.h>
#include <kwiversys/SystemTools.hxx>
#include <kwiversys/RegularExpression.hxx>

typedef kwiversys::SystemTools ST;

class diva_input::pimpl
{
public:

  diva_input::type                      type;
  std::string                           source;
  std::string                           source_dir;
  std::string                           dataset_id;
  size_t                                frame_rate_Hz = 30;

  kwiver::vital::timestamp              ts;
  kwiver::vital::timestamp::frame_t     frame_number;
  kwiver::vital::timestamp::time_t      default_frame_time_step_usec;
  kwiver::vital::metadata_vector        metadata;
  kwiver::vital::metadata_vector        last_metadata;

  kwiver::vital::algo::video_input_sptr video_reader;
  kwiver::vital::algorithm_capabilities video_traits;

  kwiver::vital::algo::image_io_sptr    image_reader;
  std::vector < kwiver::vital::path_t > files;
  std::vector < kwiver::vital::path_t >::const_iterator current_file;

  kwiver::vital::config_block_sptr      config;

  kwiver::vital::logger_handle_t        logger;
};

diva_input::diva_input()
{
  _pimpl = new pimpl();
  _pimpl->config = kwiver::vital::config_block::empty_config("diva_input");
  _pimpl->logger = kwiver::vital::get_logger( "diva.input" );
}

diva_input::~diva_input()
{
  delete _pimpl;
}

void diva_input::set_configuration(kwiver::vital::config_block_sptr c)
{
  _pimpl->config = c;
}

void diva_input::clear()
{
  remove_dataset_id();
  remove_frame_rate_Hz();
  clear_source();
}

bool diva_input::is_valid()
{
  if (_pimpl->type == type::none)
  {
    std::cerr << "Input invalid: Input cannot be None" << std::endl;
    return false;
  }
  switch (_pimpl->type)
  {
  case diva_input::type::image_list:
    if (_pimpl->source.empty())
    {
      std::cerr << "Input invalid: Image list file not provided" << std::endl;
      return false;
    }
    if (_pimpl->source_dir.empty())
    {
      std::cerr << "Input invalid: Image list source directory is not provided" << std::endl;
      return false;
    }
    break;
  case diva_input::type::video_file:

    if (_pimpl->source.empty())
    {
      std::cerr << "Input invalid: Video file not provided" << std::endl;
      return false;
    }
    if (_pimpl->source_dir.empty())
    {
      std::cerr << "Input invalid: Video file source directory is not provided" << std::endl;
      return false;
    }
    break;
  case diva_input::type::rtsp:
    if (_pimpl->source.empty())
    {
      std::cerr << "Input invalid: RSTP source URL is not provided" << std::endl;
      return false;
    }
    break;
  }
  if (!has_dataset_id())
  {
    std::cerr << "Input invalid: Dataset id is not provided" << std::endl;
    return false;
  }
  if (!has_frame_rate_Hz())
  {
    std::cerr << "Input invalid: Frame rate not provided" << std::endl;
    return false;
  }

  return true;
}

// ----------------------------------------------------------------------------
bool diva_input::read( kwiver::vital::config_block_sptr config )
{
  clear();
  _pimpl->config = config;
  if ( _pimpl->config->has_value( "input:dataset_id" ) )
  {
    set_dataset_id( _pimpl->config->get_value< std::string > (
                      "input:dataset_id" ) );
  }
  if ( _pimpl->config->has_value( "input:type" ) )
  {
    std::string t = _pimpl->config->get_value< std::string > ( "input:type" );
    
    if ( t == "image_list" )
    {
      if ( _pimpl->config->has_value( "input:source" ) &&
           _pimpl->config->has_value( "input:root_dir" ) )
      {
        set_image_list_source( _pimpl->config->get_value< std::string > ( "input:root_dir" ),
                               _pimpl->config->get_value< std::string > ( "input:source" ) );
      }
      else
      {
        LOG_WARN( _pimpl->logger, "input type 'image_list' does not have required config parameters" );
        return false;
      }
    }
    else if ( t == "video_file" )
    {
      if ( _pimpl->config->has_value( "input:source" ) &&
           _pimpl->config->has_value( "input:root_dir" ) )
      {
        set_video_file_source( _pimpl->config->get_value< std::string > ( "input:root_dir" ),
                               _pimpl->config->get_value< std::string > ( "input:source" ) );
      }
      else
      {
        LOG_WARN( _pimpl->logger, "input type 'video_file' does not have required config parameters" );
        return false;
      }
    }
    else if ( t == "rtsp" )
    {
      if ( _pimpl->config->has_value( "input:source" ) )
      {
        set_rtsp_source( _pimpl->config->get_value< std::string > (
                           "input:source" ) );
      }
      else
      {
        LOG_WARN( _pimpl->logger, "input type 'rtsp' does not have required config parameter" );
        return false;
      }
    }
  }
  if ( _pimpl->config->has_value( "input:frame_rate_Hz" ) )
  {
    set_frame_rate_Hz( _pimpl->config->get_value< size_t > (
                         "input:frame_rate_Hz" ) );
  }
  return true;
} // diva_input::read



bool diva_input::has_dataset_id() const
{
  return !_pimpl->dataset_id.empty();
}

void diva_input::set_dataset_id(const std::string& src)
{
  _pimpl->dataset_id = src;
  _pimpl->config->set_value<std::string>("input:dataset_id", src);
}

std::string diva_input::get_dataset_id() const
{
  return _pimpl->dataset_id;
}

void diva_input::remove_dataset_id()
{
  _pimpl->dataset_id = "";
  if (_pimpl->config->has_value("input:dataset_id"))
  {
    _pimpl->config->unset_value("input:dataset_id");
  }
}

bool diva_input::has_frame_rate_Hz() const
{
  return _pimpl->frame_rate_Hz > 0;
}

void diva_input::set_frame_rate_Hz(size_t hz)
{
  _pimpl->frame_rate_Hz = hz;
  _pimpl->config->set_value<size_t>("input:frame_rate_Hz", hz);
}

size_t diva_input::get_frame_rate_Hz() const
{
  return _pimpl->frame_rate_Hz;
}

void diva_input::remove_frame_rate_Hz()
{
  _pimpl->frame_rate_Hz = 0;
  if (_pimpl->config->has_value("input:frame_rate_Hz"))
  {
    _pimpl->config->unset_value("input:frame_rate_Hz");
  }
}

// ----------------------------------------------------------------------------
void diva_input::clear_source()
{
  _pimpl->type = type::none;
  _pimpl->source = "";
  _pimpl->source_dir = "";

  if (_pimpl->config->has_value("input:type"))
  {
    _pimpl->config->unset_value("input:type");
  }
  if (_pimpl->config->has_value("input:root_dir"))
  {
    _pimpl->config->unset_value("input:root_dir");
  }
  if (_pimpl->config->has_value("input:source"))
  {
    _pimpl->config->unset_value("input:source");
  }

  // TODO clear out all the vital objects
}

// ----------------------------------------------------------------------------
bool diva_input::has_source() const
{
  return _pimpl->type != type::none;
}

// ----------------------------------------------------------------------------
diva_input::type diva_input::get_source() const
{
  return _pimpl->type;
}

// ----------------------------------------------------------------------------
#include "vital/plugin_loader/plugin_manager.h"
bool diva_input::set_image_list_source(const std::string& source_dir, const std::string& list_file)
{
  clear_source();
  kwiver::vital::plugin_manager::instance().load_all_plugins();
  std::vector< std::string > search_paths;
  search_paths.push_back(source_dir);
  _pimpl->image_reader = kwiver::vital::algo::image_io::create("ocv");

  // open file and read lines
  std::ifstream ifs(source_dir + "/" + list_file);
  if (!ifs)
  {
    LOG_ERROR( _pimpl->logger, "Could not open file \"" << source_dir + list_file << "\"" );
    return false;
  }

  kwiver::vital::data_stream_reader stream_reader(ifs);
  // verify and get file names in a list
  for (std::string line; stream_reader.getline(line); /* null */)
  {
#ifdef _WIN32
    line = "." + line;
#endif
    std::string resolved_file = line;
    if (!kwiversys::SystemTools::FileExists(line))
    {
      // Resolve against specified path
      resolved_file = kwiversys::SystemTools::FindFile(line, search_paths, true);
      if (resolved_file.empty())
      {
        VITAL_THROW( kwiver::vital::file_not_found_exception, line, "could not locate file in path");
      }
    }
    _pimpl->files.push_back(resolved_file);
  } // end for

  _pimpl->current_file = _pimpl->files.begin();

  _pimpl->type = type::image_list;
  _pimpl->source = list_file;
  _pimpl->source_dir = source_dir;
  _pimpl->default_frame_time_step_usec = static_cast<kwiver::vital::timestamp::time_t>(.3333 * 1e6); // in usec;
  _pimpl->config->set_value<std::string>("input:type", "image_list");
  _pimpl->config->set_value<std::string>("input:source", list_file);
  _pimpl->config->set_value<std::string>("input:root_dir", source_dir);
  return true;
}

// ----------------------------------------------------------------------------
// Note this is how you load an image/frame off disk, if that is something you would want to do
//kwiver::vital::algo::image_io_sptr ocv_io = kwiver::vital::algo::image_io::create("ocv");
//kwiver::vital::image_container_sptr ocv_img = ocv_io->load("./image.png");
std::string diva_input::get_image_list_file() const
{
  return _pimpl->source;
}

std::string diva_input::get_image_list_source_dir() const
{
  return _pimpl->source_dir;
}

#include "vital/plugin_loader/plugin_manager.h"
bool diva_input::set_video_file_source(const std::string& source_dir, const std::string& video_file)
{
  clear_source();
  kwiver::vital::plugin_manager::instance().load_all_plugins();
  _pimpl->video_reader = kwiver::vital::algo::video_input::create("ffmpeg");
  _pimpl->video_reader->set_configuration(_pimpl->video_reader->get_configuration());// This will default the configuration
  try
  {
    _pimpl->video_reader->open(source_dir + "/" + video_file);//ST::JoinPath(std::vector<std::string>({source_dir, video_file}))); // throws
  }
  catch (std::exception& ex)
  {
    LOG_ERROR( _pimpl->logger, "Caught exception while opening video reader - " << ex.what() );
    return false;
  }

  // Get the capabilities for the currently opened video.
  _pimpl->video_traits = _pimpl->video_reader->get_implementation_capabilities();

  _pimpl->type = type::video_file;
  _pimpl->source = video_file;
  _pimpl->source_dir = source_dir;
  _pimpl->frame_rate_Hz = _pimpl->video_reader->frame_rate();
  _pimpl->default_frame_time_step_usec = static_cast<kwiver::vital::timestamp::time_t>(.3333 * 1e6); // in usec;
  _pimpl->config->set_value<std::string>("input:type", "video_file");
  _pimpl->config->set_value<std::string>("input:source", video_file);
  _pimpl->config->set_value<std::string>("input:root_dir", source_dir);

  return true;
}

std::string diva_input::get_video_file_source() const
{
  return _pimpl->source;
}

std::string diva_input::get_video_file_source_dir() const
{
  return _pimpl->source_dir;
}

#include "vital/plugin_loader/plugin_manager.h"
bool diva_input::set_rtsp_source(const std::string& url)
{
  clear_source();
  kwiver::vital::plugin_manager::instance().load_all_plugins();
  _pimpl->video_reader = kwiver::vital::algo::video_input::create("vidl_ffmpeg");
  _pimpl->video_reader->set_configuration(_pimpl->video_reader->get_configuration());// This will default the configuration
  try
  {
    _pimpl->video_reader->open( url ); // throws
  }
  catch (std::exception& ex)
  {
    LOG_ERROR( _pimpl->logger, "Caught exception while opening video reader - " << ex.what() );
    return false;
  }

  // Get the capabilities for the currently opened video.
  _pimpl->video_traits = _pimpl->video_reader->get_implementation_capabilities();

  _pimpl->type = type::rtsp;
  _pimpl->source = url;
  _pimpl->source_dir = url;
  _pimpl->frame_rate_Hz = 0;// TODO Get this from kwiver
  _pimpl->default_frame_time_step_usec = static_cast<kwiver::vital::timestamp::time_t>(.3333 * 1e6); // in usec;
  _pimpl->config->set_value<std::string>("input:type", "rtsp");
  _pimpl->config->set_value<std::string>("input:source", url);
  _pimpl->config->set_value<std::string>("input:root_dir", url);

  return true;
}

std::string diva_input::get_rtsp_source() const
{
  return _pimpl->source;
}

bool diva_input::has_next_frame()
{
  switch (_pimpl->type)
  {
  case diva_input::type::image_list:
    return _pimpl->current_file != _pimpl->files.end();
  case diva_input::type::rtsp:
  case diva_input::type::video_file:
    return _pimpl->video_reader->next_frame(_pimpl->ts);
  }
  return false;
}

kwiver::vital::image_container_sptr diva_input::get_next_frame()
{
  kwiver::vital::image_container_sptr frame;
  switch (_pimpl->type)
  {
    case diva_input::type::image_list:
    {
      std::string a_file = *_pimpl->current_file;
      frame = _pimpl->image_reader->load(a_file);
      // update timestamp
      kwiversys::RegularExpression frame_num_re("([0-9]+)\\.[^\\.]+$");
      if (!frame_num_re.find(a_file))
      {
        ++_pimpl->frame_number;
      }
      else
      {
        _pimpl->frame_number = std::stoi(frame_num_re.match(1));
      }
      _pimpl->ts.set_frame(_pimpl->frame_number);
      _pimpl->ts.set_time_usec(_pimpl->frame_number * _pimpl->default_frame_time_step_usec);
      ++_pimpl->current_file;
      // TODO meta data?
      break;
    }
    // rtsp is using the same vidl ffmpeg 
    case diva_input::type::rtsp:
    case diva_input::type::video_file:
    {
      if (!_pimpl->video_traits.capability(kwiver::vital::algo::video_input::HAS_FRAME_DATA))
      {
        VITAL_THROW( kwiver::vital::video_stream_exception, "Video reader selected does not supply image data.");
      }
      frame = _pimpl->video_reader->frame_image();

      // Compute the frame number if its not in the timestamp
      if (!_pimpl->video_traits.capability(kwiver::vital::algo::video_input::HAS_FRAME_NUMBERS))
      {
        ++_pimpl->frame_number;
        _pimpl->ts.set_frame(_pimpl->frame_number);
      }

      // Compute a frame time if its not in the time stamp
      if (!_pimpl->video_traits.capability(kwiver::vital::algo::video_input::HAS_FRAME_TIME))
      {
        // If the video does not know its frame time step, compute with the experiment request
        _pimpl->ts.set_time_usec(_pimpl->frame_number * _pimpl->default_frame_time_step_usec);
      }

      // If this reader/video does not have any metadata, we will just
      // return an empty vector.  That is all handled by the algorithm
      // implementation.
      _pimpl->metadata = _pimpl->video_reader->frame_metadata();
      // Since we want to try to always return valid metadata for this
      // frame - if the returned metadata is empty, then use the last
      // one we received.  The requirement is to always provide the best
      // metadata for a frame. Since metadata appears less frequently
      // than the frames, the metadata returned can be a little old, but
      // it is still the best we have.
      if (_pimpl->metadata.empty())
      {
        // The saved one could be empty, but it is the bewt we have.
        _pimpl->metadata = _pimpl->last_metadata;
      }
      else
      {
        // Now that we have new metadata save it in case we need it later.
        _pimpl->last_metadata = _pimpl->metadata;
      }
      break;
    }
  }
  return frame;
}

kwiver::vital::timestamp diva_input::get_next_frame_timestamp() const
{
  return _pimpl->ts;
}

kwiver::vital::metadata_vector diva_input::get_next_frame_metadata() const
{
  return _pimpl->metadata;
}
