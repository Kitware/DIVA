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
#include <utils/diva_utils_export.h>
#include <vital/exceptions/io.h>
#include <vital/exceptions/video.h>
#include <vital/types/image_container.h>
#include <vital/config/config_block.h>
#include <vital/config/config_block_io.h>

class DIVA_UTILS_EXPORT diva_input
{
protected:
  friend class diva_experiment;
  void set_configuration(kwiver::vital::config_block_sptr config);
public:

  enum class type
  {
    none = 0,
    image_list,
    video_file,
    rstp
  };

  diva_input();
  virtual ~diva_input();

  bool read(kwiver::vital::config_block_sptr config);

public:
  void clear();
  bool is_valid();

  bool has_dataset_id() const;
  void set_dataset_id(const std::string& id);
  std::string get_dataset_id() const;
  void remove_dataset_id();

  bool has_frame_rate_Hz() const;
  void set_frame_rate_Hz(size_t hz);
  size_t get_frame_rate_Hz() const;
  void remove_frame_rate_Hz();

  void clear_source();
  bool has_source() const;
  diva_input::type get_source() const;
  // Image List File
  std::string get_image_list_file() const;
  std::string get_image_list_source_dir() const;
  bool set_image_list_source(const std::string& source_dir, const std::string& list_file);
  // Video File
  std::string get_video_file_source() const;
  std::string get_video_file_source_dir() const;
  bool set_video_file_source(const std::string& source_dir, const std::string& video_file);
  // RSTP Stream
  bool set_rstp_source(const std::string& url);
  std::string get_rstp_source() const;

  bool has_next_frame();
  kwiver::vital::image_container_sptr get_next_frame();
  kwiver::vital::timestamp get_next_frame_timestamp() const;
  kwiver::vital::metadata_vector get_next_frame_metadata() const;

private:
  class pimpl;
  pimpl* _pimpl;
};
