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
#include <map>

class diva_activity_impl;

class DIVA_UTILS_EXPORT diva_activity : public diva_packet
{
  friend struct diva_activity_adapter;
public:
  diva_activity();
  virtual ~diva_activity();

  void clear();
  bool is_valid() const;

  bool has_activity_name() const;
  std::string get_activity_name() const;
  void set_activity_name(const std::string& name);
  void remove_activity_name();

  bool has_activity_id() const;
  size_t get_activity_id() const;
  void set_activity_id(size_t id);
  void remove_activity_id();

  bool has_source() const;
  diva_source get_source() const;
  void set_source(diva_source s);
  void remove_source();

  bool has_frame_id_span() const;
  std::vector<std::pair<size_t, size_t>>& get_frame_id_span();
  const std::vector<std::pair<size_t, size_t>>& get_frame_id_span() const;
  void remove_frame_id_span();

  bool has_frame_time_span() const;
  std::vector<std::pair<double, double>>& get_frame_time_span();
  const std::vector<std::pair<double, double>>& get_frame_time_span() const;
  void remove_frame_time_span();

  bool has_frame_absolute_time_span() const;
  std::vector<std::pair<double, double>>& get_frame_absolute_time_span();
  const std::vector<std::pair<double, double>>& get_frame_absolute_time_span() const;
  void remove_frame_absolute_time_span();

  bool has_actor_frame_id_span() const;
  std::map<size_t,std::vector<std::pair<size_t, size_t>>>& get_actor_frame_id_span();
  const std::map<size_t, std::vector<std::pair<size_t, size_t>>>& get_actor_frame_id_span() const;
  void remove_actor_frame_id_span();

  bool has_actor_frame_time_span() const;
  std::map<size_t, std::vector<std::pair<double, double>>>& get_actor_frame_time_span();
  const std::map<size_t, std::vector<std::pair<double, double>>>& get_actor_frame_time_span() const;
  void remove_actor_frame_time_span();

  bool has_actor_frame_absolute_time_span() const;
  std::map<size_t, std::vector<std::pair<double, double>>>& get_actor_frame_absolute_time_span();
  const std::map<size_t, std::vector<std::pair<double, double>>>& get_actor_frame_absolute_time_span() const;
  void remove_actor_frame_absolute_time_span();

  void write(std::ostream& os) const;
private:
  diva_activity_impl* _pimpl;
};
