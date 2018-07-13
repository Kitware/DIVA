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

#include "diva_label.h"
#include "diva_exceptions.h"

#include <yaml-cpp/yaml.h>
#include <arrows/kpf/yaml/kpf_reader.h>
#include <arrows/kpf/yaml/kpf_yaml_parser.h>
#include <arrows/kpf/yaml/kpf_yaml_writer.h>
#include <arrows/kpf/yaml/kpf_canonical_io_adapter.h>
#include <fstream> 
#include <ostream>

namespace KPF = kwiver::vital::kpf;

class diva_label::pimpl
{
public:
  size_t                        track_id;
  std::map<std::string, double> classification;

  std::stringstream ss;
};

diva_label::diva_label()
{
  _pimpl = new pimpl();
}
diva_label::~diva_label()
{
  delete _pimpl;
}

void diva_label::clear()
{
  _pimpl->track_id = -1;
  _pimpl->classification.clear();
}


bool diva_label::is_valid() const
{
  if (_pimpl->track_id != -1 && !_pimpl->classification.empty())
    return true;
  return false;
}

bool diva_label::has_track_id() const
{
  return _pimpl->track_id != -1;
}
size_t diva_label::get_track_id() const
{
  return _pimpl->track_id;
}
void diva_label::set_track_id(size_t id) 
{
  _pimpl->track_id = id; 
}
void diva_label::remove_track_id()
{
  _pimpl->track_id = -1;
}

bool diva_label::has_classification() const
{
  return _pimpl->classification.size() > 0;
}
std::map<std::string, double>& diva_label::get_classification()
{
  return _pimpl->classification;
}
const std::map<std::string, double>& diva_label::get_classification() const
{
  return _pimpl->classification;
}
void diva_label::add_classification(const std::string& name, double probability)
{
  _pimpl->classification.insert(std::pair <std::string, double>(name, probability));
}
void diva_label::remove_classification()
{
  _pimpl->classification.clear();
}
std::string diva_label::get_max_classification() const
{
  double prob=-1;
  std::string type = "";
  for (auto itr : _pimpl->classification)
    if (itr.second > prob)
      type = itr.first;
  return type;
}

void diva_label::write(std::ostream& os) const
{
  if (!is_valid())
    throw malformed_diva_data_exception("label packet is invalid");

  namespace KPFC = KPF::canonical;
  KPF::record_yaml_writer w(os);
  const int DIVA_DOMAIN = 3; // DIVA objects

  w.set_schema(KPF::schema_style::TYPES);
  w << KPF::writer< KPFC::id_t >(_pimpl->track_id, KPFC::id_t::TRACK_ID);
  KPFC::cset_t type_map;
  for (auto i : _pimpl->classification)
    type_map.d.insert(std::make_pair(i.first, i.second));
  w << KPF::writer< KPFC::cset_t>(type_map, DIVA_DOMAIN);
  w << KPF::record_yaml_writer::endl;
}

std::string diva_label::to_string() const
{
  _pimpl->ss.str("");
  write(_pimpl->ss);
  return _pimpl->ss.str();
}


void diva_label::from_string(const std::string& p)
{
  clear();

  std::istringstream str(p);
  namespace KPFC = KPF::canonical;
  KPF::kpf_yaml_parser_t parser(str);
  KPF::kpf_reader_t reader(parser);
  const int DIVA_DOMAIN = 3; // DIVA objects

  reader >> KPF::reader< KPFC::id_t >(_pimpl->track_id, KPFC::id_t::TRACK_ID);
  auto type_probe = reader.transfer_packet_from_buffer(
    KPF::packet_header_t(KPF::packet_style::CSET, DIVA_DOMAIN));
  if (type_probe.first)
  {
    for (auto i : type_probe.second.cset->d)
      _pimpl->classification.insert(std::make_pair(i.first, i.second));
  }
}
