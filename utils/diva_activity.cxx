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

#include "diva_activity.h"
#include "diva_exceptions.h"

#include <yaml-cpp/yaml.h>
#include <arrows/kpf/yaml/kpf_reader.h>
#include <arrows/kpf/yaml/kpf_yaml_parser.h>
#include <arrows/kpf/yaml/kpf_yaml_writer.h>
#include <arrows/kpf/yaml/kpf_canonical_io_adapter.h>
namespace KPF = kwiver::vital::kpf;

class diva_activity_impl
{
public:
  std::map< std::string, double >                          activity_names;
  size_t                                                   activity_id;
  diva_activity::source                                    source;
  std::vector<std::pair<double, double>>                   frame_id_span;
  std::vector<std::pair<double, double>>                   frame_time_span;
  std::vector<std::pair<double, double>>                   frame_absolute_time_span;
  std::map<size_t, std::vector<std::pair<double, double>>> actor_frame_id_span;
  std::map<size_t, std::vector<std::pair<double, double>>> actor_frame_time_span;
  std::map<size_t, std::vector<std::pair<double, double>>> actor_frame_absolute_time_span;

  std::stringstream ss;
};

const int DIVA_ACTIVITY_DOMAIN = 2;
const int DIVA_TRACK_DOMAIN = 2;

//
// The KPF activity object is complex, and requires an adapter.
//

struct diva_activity_adapter : public KPF::kpf_act_adapter< diva_activity_impl >
{
  diva_activity_adapter() :
    kpf_act_adapter< diva_activity_impl >(
      // reads the canonical activity "a" into the user_activity "u"
      [](const KPF::canonical::activity_t& a, diva_activity_impl& u)
  {
    if(a.activity_id.domain != DIVA_ACTIVITY_DOMAIN)
      throw malformed_diva_data_exception("activty domain must be " + DIVA_ACTIVITY_DOMAIN);
    // load the activity ID, name, and start and stop frames
    u.activity_id = a.activity_id.t.d;
    u.activity_names = a.activity_labels.d;
    // load in our overall activity time spans
    for (const auto& ts : a.timespan)
    {
      switch (ts.domain)
      {
      case 0:
        u.frame_id_span.push_back(std::pair<double, double>(ts.t.start, ts.t.stop));
        break;
      case 1:
        u.frame_time_span.push_back(std::pair<double, double>(ts.t.start, ts.t.stop));
        break;
      case 2:
        u.frame_absolute_time_span.push_back(std::pair<double, double>(ts.t.start, ts.t.stop));
        break;
      }
    }
    // load in our actor ID/time spans
    for (const auto& actor : a.actors)
    {
      if (actor.actor_id.domain != DIVA_TRACK_DOMAIN)
        throw malformed_diva_data_exception("activty actor domain must be "+ DIVA_TRACK_DOMAIN);
      for (const auto& ts : actor.actor_timespan)
      {
        switch (ts.domain)
        {
          case 0:
          {
            std::vector<std::pair<double, double>>& track_times = u.actor_frame_id_span[actor.actor_id.t.d];
            track_times.push_back(std::pair<double, double>(ts.t.start, ts.t.stop));
            break;
          }
          case 1:
          {
            std::vector<std::pair<double, double>>& track_times = u.actor_frame_time_span[actor.actor_id.t.d];
            track_times.push_back(std::pair<double, double>(ts.t.start, ts.t.stop));
            break;
          }
          case 2:
          {
            std::vector<std::pair<double, double>>& track_times = u.actor_frame_absolute_time_span[actor.actor_id.t.d];
            track_times.push_back(std::pair<double, double>(ts.t.start, ts.t.stop));
            break;
          }
        }
      }
    }
    // look for any key/value pairs
    /*for (const auto& kv : a.attributes)
    {
      if (kv.key == "")
      {
        u.something = stod(kv.val);
      }
    }*/
  },

      // converts a user_activity "a" into a canonical activity and returns it
    [](const diva_activity_impl& u)
  {
    KPF::canonical::activity_t a;
    // set the name, ID, and domain
    a.activity_labels.d = u.activity_names;
    a.activity_id.t.d = u.activity_id;
    a.activity_id.domain = DIVA_ACTIVITY_DOMAIN;

    // set the start / stop time (as frame numbers)
    for (const auto& ts : u.frame_id_span)
    {
      KPF::canonical::scoped< KPF::canonical::timestamp_range_t > tsr;
      tsr.domain = KPF::canonical::timestamp_t::FRAME_NUMBER;
      tsr.t.start = ts.first;
      tsr.t.stop = ts.second;
      a.timespan.push_back(tsr);
    }
    /*for (const auto& ts : u.frame_time_span)
    {
      KPF::canonical::scoped< KPF::canonical::timestamp_range_t > tsr;
      tsr.domain = KPF::canonical::timestamp_t::FRAME_TIME;
      tsr.t.start = ts.first;
      tsr.t.stop = ts.second;
      a.timespan.push_back(tsr);
    }
    for (const auto& ts : u.frame_absolute_time_span)
    {
      KKPF::canonical::scoped< KPF::canonical::timestamp_range_t > tsr;
      tsr.domain = KPF::canonical::timestamp_t::FRAME_ABSOLUTE_TIME;
      tsr.t.start = ts.first;
      tsr.t.stop = ts.second;
      a.timespan.push_back(tsr);
    }*/

    // also use the activity start/stop time for each actor
    for (const auto& map : u.actor_frame_id_span)
    {
      KPF::canonical::activity_t::actor_t act;
      act.actor_id.t.d = map.first;
      act.actor_id.domain = DIVA_TRACK_DOMAIN;
      for (const auto& ts : map.second)
      {
        KPF::canonical::scoped< KPF::canonical::timestamp_range_t > tsr;
        tsr.domain = KPF::canonical::timestamp_t::FRAME_NUMBER;
        tsr.t.start = ts.first;
        tsr.t.stop = ts.second;
        act.actor_timespan.push_back(tsr);
      }
      a.actors.push_back(act);
    }
    /*for (const auto& map : u.actor_frame_id_span)
    {
      KPF::canonical::scoped< KPF::canonical::timestamp_range_t > tsr;
      act.id.d = map.first;
      act.id_domain = TRACK_DOMAIN;
      for (const auto& ts : map.second)
      {
        KPF::canonical::activity_t::scoped_tsr_t tsr;
        tsr.domain = KPF::canonical::timestamp_t::FRAME_TIME;
        tsr.t.start = ts.first;
        tsr.t.stop = ts.second;
        act.actor_timespan.push_back(tsr);
      }
      a.actors.push_back(act);
    }
    for (const auto& map : u.actor_frame_id_span)
    {
      KPF::canonical::scoped< KPF::canonical::timestamp_range_t > tsr;
      act.id.d = map.first;
      act.id_domain = TRACK_DOMAIN;
      for (const auto& ts : map.second)
      {
        KPF::canonical::activity_t::scoped_tsr_t tsr;
        tsr.domain = KPF::canonical::timestamp_t::FRAME_ABSOLUTE_TIME;
        tsr.t.start = ts.first;
        tsr.t.stop = ts.second;
        act.actor_timespan.push_back(tsr);
      }
      a.actors.push_back(act);
    }*/

    return a;
  })
  {}
};


diva_activity::diva_activity()
{
  _pimpl = new diva_activity_impl();
}
diva_activity::~diva_activity()
{
  delete _pimpl;
}

void diva_activity::clear()
{
  _pimpl->activity_names.clear();
  _pimpl->activity_id = -1;
  _pimpl->source = (diva_activity::source )-1;
  _pimpl->frame_id_span.clear();
  _pimpl->frame_time_span.clear();
  _pimpl->frame_absolute_time_span.clear();
  _pimpl->actor_frame_id_span.clear();
  _pimpl->actor_frame_time_span.clear();
  _pimpl->actor_frame_absolute_time_span.clear();
}

bool diva_activity::is_valid() const
{
  return true;
}

bool diva_activity::has_activity_names() const
{
  return !_pimpl->activity_names.empty();
}
std::map<std::string, double> diva_activity::get_activity_names() const
{
  return _pimpl->activity_names;
}
void diva_activity::set_activity_names(const std::map<std::string, double>& names)
{
  _pimpl->activity_names = names;
}
std::string diva_activity::get_max_activity_name() const
{
  if (!has_activity_names())
    return "";
  double max = -1;
  std::string name;
  for (auto c : _pimpl->activity_names)
    if (c.second > max)
      name = c.first;
  return name;
}
void diva_activity::remove_activity_names()
{
  _pimpl->activity_names.clear();
}

bool diva_activity::has_activity_id() const
{
  return _pimpl->activity_id != -1;
}
size_t diva_activity::get_activity_id() const
{
  return _pimpl->activity_id;
}
void diva_activity::set_activity_id(size_t id)
{
  _pimpl->activity_id = id;
}
void diva_activity::remove_activity_id()
{
  _pimpl->activity_id = -1;
}

bool diva_activity::has_source() const
{
  return _pimpl->source != static_cast<diva_activity::source>( -1 );
}
diva_activity::source diva_activity::get_source() const
{
  return _pimpl->source;
}
void diva_activity::set_source(diva_activity::source s)
{
  _pimpl->source = s;
}
void diva_activity::remove_source()
{
  _pimpl->source = static_cast<diva_activity::source>( -1 );
}

bool diva_activity::has_frame_id_span() const
{
  return _pimpl->frame_id_span.size() > 0;
}
std::vector<std::pair<double, double>>& diva_activity::get_frame_id_span()
{
  return _pimpl->frame_id_span;
}
const std::vector<std::pair<double, double>>& diva_activity::get_frame_id_span() const
{
  return _pimpl->frame_id_span;
}
void diva_activity::add_frame_id_span(const std::pair<double, double>& start_end)
{
  _pimpl->frame_id_span.push_back(start_end);
}
void diva_activity::remove_frame_id_span()
{
  _pimpl->frame_id_span.clear();
}

bool diva_activity::has_frame_time_span() const
{
  return _pimpl->frame_time_span.size() > 0;
}
std::vector<std::pair<double, double>>& diva_activity::get_frame_time_span()
{
  return _pimpl->frame_time_span;
}
const std::vector<std::pair<double, double>>& diva_activity::get_frame_time_span() const
{
  return _pimpl->frame_time_span;
}
void diva_activity::add_frame_time_span(const std::pair<double, double>& start_end)
{
  _pimpl->frame_time_span.push_back(start_end);
}
void diva_activity::remove_frame_time_span()
{
  _pimpl->frame_time_span.clear();
}

bool diva_activity::has_frame_absolute_time_span() const
{
  return _pimpl->frame_absolute_time_span.size() > 0;
}
std::vector<std::pair<double, double>>& diva_activity::get_frame_absolute_time_span()
{
  return _pimpl->frame_absolute_time_span;
}
const std::vector<std::pair<double, double>>& diva_activity::get_frame_absolute_time_span() const
{
  return _pimpl->frame_absolute_time_span;
}
void diva_activity::add_frame_absolute_time_span(const std::pair<double, double>& start_end)
{
  _pimpl->frame_absolute_time_span.push_back(start_end);
}
void diva_activity::remove_frame_absolute_time_span()
{
  _pimpl->frame_absolute_time_span.clear();
}

bool diva_activity::has_actor_frame_id_span() const
{
  return _pimpl->actor_frame_id_span.size() > 0;
}
std::map<size_t, std::vector<std::pair<double, double>>>& diva_activity::get_actor_frame_id_span()
{
  return _pimpl->actor_frame_id_span;
}
const std::map<size_t, std::vector<std::pair<double, double>>>& diva_activity::get_actor_frame_id_span() const
{
  return _pimpl->actor_frame_id_span;
}
void diva_activity::add_actor_frame_id_span(size_t id, const std::pair<double, double>& start_end)
{
  std::vector<std::pair<double, double>>& v = _pimpl->actor_frame_id_span[id];
  v.push_back(start_end);
}
void diva_activity::remove_actor_frame_id_span()
{
  _pimpl->actor_frame_id_span.clear();
}

bool diva_activity::has_actor_frame_time_span() const
{
  return _pimpl->actor_frame_time_span.size() > 0;
}
std::map<size_t, std::vector<std::pair<double, double>>>& diva_activity::get_actor_frame_time_span()
{
  return _pimpl->actor_frame_time_span;
}
const std::map<size_t, std::vector<std::pair<double, double>>>& diva_activity::get_actor_frame_time_span() const
{
  return _pimpl->actor_frame_time_span;
}
void diva_activity::add_actor_frame_time_span(size_t id, const std::pair<double, double>& start_end)
{
  std::vector<std::pair<double, double>>& v = _pimpl->actor_frame_time_span[id];
  v.push_back(start_end);
}
void diva_activity::remove_actor_frame_time_span()
{
  _pimpl->actor_frame_time_span.clear();
}

bool diva_activity::has_actor_frame_absolute_time_span() const
{
  return _pimpl->actor_frame_absolute_time_span.size() > 0;
}
std::map<size_t, std::vector<std::pair<double, double>>>& diva_activity::get_actor_frame_absolute_time_span()
{
  return _pimpl->actor_frame_absolute_time_span;
}
const std::map<size_t, std::vector<std::pair<double, double>>>& diva_activity::get_actor_frame_absolute_time_span() const
{
  return _pimpl->actor_frame_absolute_time_span;
}
void diva_activity::add_actor_frame_absolute_time_span(size_t id, const std::pair<double, double>& start_end)
{
  std::vector<std::pair<double, double>>& v = _pimpl->actor_frame_absolute_time_span[id];
  v.push_back(start_end);
}
void diva_activity::remove_actor_frame_absolute_time_span()
{
  _pimpl->actor_frame_absolute_time_span.clear();
}

void diva_activity::write(std::ostream& os) const
{
  if (!is_valid())
    throw malformed_diva_data_exception("activity packet is invalid");

  namespace KPFC = KPF::canonical;
  diva_activity_adapter act_adapter;

  KPF::record_yaml_writer w(os);
  w.set_schema(KPF::schema_style::ACT);
  w << KPF::writer< KPFC::activity_t >(act_adapter(*_pimpl), DIVA_ACTIVITY_DOMAIN)
    << KPF::record_yaml_writer::endl;
}

std::string diva_activity::to_string() const
{
  _pimpl->ss.str("");
  write(_pimpl->ss);
  return _pimpl->ss.str();
}

void diva_activity::from_string(const std::string& p)
{
  clear();

  std::istringstream str(p);
  namespace KPFC = KPF::canonical;
  KPF::kpf_yaml_parser_t parser(str);
  KPF::kpf_reader_t reader(parser);
  const int DIVA_DOMAIN = 3; // DIVA objects

  auto act = reader.transfer_packet_from_buffer(KPF::packet_header_t(KPF::packet_style::ACT, DIVA_ACTIVITY_DOMAIN));
  if (act.first)
  {
    _pimpl->activity_id = act.second.activity.activity_id.t.d;
    for (auto i : act.second.activity.activity_labels.d)
      _pimpl->activity_names.insert(std::make_pair(i.first, i.second));
    for (auto attr : act.second.activity.attributes)
    {
      if (attr.key == "src")
      {
        if (attr.val == "truth")
          _pimpl->source = diva_activity::source::truth;
        else
          std::cout << "Unsupported src value " << attr.val << std::endl;
      }
    }
    for (auto ts : act.second.activity.timespan)
    {
      switch(ts.domain)
      {
      case(0):
        _pimpl->frame_id_span.push_back(std::pair<double, double>(ts.t.start, ts.t.stop));
        break;
      case(1):
        _pimpl->frame_time_span.push_back(std::pair<double, double>(ts.t.start, ts.t.stop));
        break;
      case(2):
        _pimpl->frame_absolute_time_span.push_back(std::pair<double, double>(ts.t.start, ts.t.stop));
        break;
      default:
        std::cout << "Unsupported timespan domain " << ts.domain << std::endl;
      }
    }
    for (auto actor : act.second.activity.actors)
    {
      // I am assuming actor.domain is in the DIVA domain
      for (auto ts : actor.actor_timespan)
      {
        switch(ts.domain)
        {
        case(0):
          _pimpl->actor_frame_id_span[actor.actor_id.t.d].push_back(std::pair<double, double>(ts.t.start,ts.t.stop));
          break;
        case(1):
          _pimpl->actor_frame_time_span[actor.actor_id.t.d].push_back(std::pair<double, double>(ts.t.start, ts.t.stop));
          break;
        case(2):
          _pimpl->actor_frame_absolute_time_span[actor.actor_id.t.d].push_back(std::pair<double, double>(ts.t.start, ts.t.stop));
          break;
        default:
          std::cout << "Unsupported actor timespan domain " << ts.domain << std::endl;
        }
      }
    }
  }
}

