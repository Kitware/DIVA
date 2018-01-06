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

#include "diva_input.h"
#include "diva_experiment.h"
#include <yaml-cpp/yaml.h>
#include <vital/exceptions.h>
#include <vital/types/image.h>
#include <vital/types/image_container.h>
#include <vital/algo/video_input.h>
#include <vital/algo/image_io.h>
#include <vital/util/data_stream_reader.h>
#include <kwiversys/SystemTools.hxx>

class diva_input::pimpl
{
public:
  const diva_experiment*                exp;

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
};

diva_input::diva_input()
{
  _pimpl = new pimpl();
}

diva_input::~diva_input()
{
  delete _pimpl;
}

bool diva_input::load_experiment(const diva_experiment& exp)
{
  _pimpl->exp = &exp;

  _pimpl->frame_number = 0;
  _pimpl->default_frame_time_step_usec = static_cast<kwiver::vital::timestamp::time_t>(.3333 * 1e6); // in usec;
  switch (_pimpl->exp->get_input_type())
  {
    case diva_input_type::file_list:
    {
      std::vector< std::string > search_paths;
      search_paths.push_back(exp.get_input_root_dir());
      _pimpl->image_reader = kwiver::vital::algo::image_io::create("ocv");
      // open file and read lines
      std::ifstream ifs(exp.get_input_root_dir() + "/" + exp.get_input_source());
      if (!ifs)
        return false;

      kwiver::vital::data_stream_reader stream_reader(ifs);
      // verify and get file names in a list
      for (std::string line; stream_reader.getline(line); /* null */)
      {
        std::string resolved_file = line;
        if (!kwiversys::SystemTools::FileExists(line))
        {
          // Resolve against specified path
          resolved_file = kwiversys::SystemTools::FindFile(line, search_paths, true);
          if (resolved_file.empty())
          {
            throw kwiver::vital::file_not_found_exception(line, "could not locate file in path");
          }
        }

        _pimpl->files.push_back(resolved_file);
      } // end for
      _pimpl->current_file = _pimpl->files.begin();
      break;
    }
    case diva_input_type::video:
    {
      _pimpl->video_reader = kwiver::vital::algo::video_input::create("vidl_ffmpeg"); 
      _pimpl->video_reader->set_configuration(_pimpl->video_reader->get_configuration());// This will default the configuration 
      try
      {
        if (exp.get_transport_type() == diva_transport_type::disk)
          _pimpl->video_reader->open(exp.get_input_root_dir() + "/" + exp.get_input_source()); // throws
        else
          return false;//TODO support other transport options
      }
      catch (std::exception& ex)
      {
        return false;
      }
      // Get the capabilities for the currently opened video.
      _pimpl->video_traits = _pimpl->video_reader->get_implementation_capabilities();
      break;
    }
    default:
    {
      return false;
    }
  }
  return true;
}

bool diva_input::has_next_frame()
{
  switch (_pimpl->exp->get_input_type())
  {
  case diva_input_type::file_list:
    return _pimpl->current_file != _pimpl->files.end();
  case diva_input_type::video:
    return _pimpl->video_reader->next_frame(_pimpl->ts);
  }
  return false;
}

kwiver::vital::image_container_sptr diva_input::get_next_frame()
{
  kwiver::vital::image_container_sptr frame;
  switch (_pimpl->exp->get_input_type())
  {
    case diva_input_type::file_list:
    {
      std::string a_file = *_pimpl->current_file;
      frame = _pimpl->image_reader->load(a_file);
      // update timestamp
      ++_pimpl->frame_number;
      _pimpl->ts.set_frame(_pimpl->frame_number);
      _pimpl->ts.set_time_usec(_pimpl->frame_number * _pimpl->default_frame_time_step_usec);
      ++_pimpl->current_file;
      // TODO meta data?
      break;
    }
    case diva_input_type::video:
    {
      if (!_pimpl->video_traits.capability(kwiver::vital::algo::video_input::HAS_FRAME_DATA))
      {
        throw kwiver::vital::video_stream_exception("Video reader selected does not supply image data.");
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

  // Note this is how you load an image/frame off disk, if that is something you would want to do
  //kwiver::vital::algo::image_io_sptr ocv_io = kwiver::vital::algo::image_io::create("ocv");
  //kwiver::vital::image_container_sptr ocv_img = ocv_io->load("./image.png");


