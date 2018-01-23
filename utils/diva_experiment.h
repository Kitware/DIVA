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
#include <string>

class DIVA_UTILS_EXPORT diva_experiment
{
public:
  enum class type
  {
    object_detection = 0,
    activity_detection
  };

  enum class input_type
  {
    file_list = 0,
    video
  };

  enum class transport_type
  {
    disk = 0,
    girder,
    rstp
  };

  enum class output_type
  {
    file = 0
  };

  diva_experiment();
  virtual ~diva_experiment();

  void clear();
  bool is_valid();

  bool read_experiment(const std::string& filename);
  bool write_experiment(const std::string& filename);

  bool has_type() const;
  type get_type() const;
  void set_type(type s);
  void remove_type();

  bool has_input_type() const;
  input_type get_input_type() const;
  void set_input_type(input_type s);
  void remove_input_type();

  bool has_transport_type() const;
  transport_type get_transport_type() const;
  void set_transport_type(transport_type s);
  void remove_transport_type();

  bool has_dataset_id() const;
  void set_dataset_id(const std::string& id);
  std::string get_dataset_id() const;
  void remove_dataset_id();

  bool has_input_source() const;
  void set_input_source(const std::string& id);
  std::string get_input_source() const;
  void remove_input_source();

  bool has_input_root_dir() const;
  void set_input_root_dir(const std::string& id);
  std::string get_input_root_dir() const;
  void remove_input_root_dir();

  bool has_frame_rate_Hz() const;
  void set_frame_rate_Hz(size_t hz);
  size_t get_frame_rate_Hz() const;
  void remove_frame_rate_Hz();

  bool has_output_type() const;
  output_type get_output_type() const;
  void set_output_type(output_type s);
  void remove_output_type();

  bool has_output_root_dir() const;
  void set_output_root_dir(const std::string& id);
  std::string get_output_root_dir() const;
  void remove_output_root_dir();

  std::string get_output_filename() const;// Full path with no extension!

private:
  class pimpl;
  pimpl* _pimpl;
};

