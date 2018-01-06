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
#include <arrows/kpf/yaml/kpf_yaml_writer.h>
#include <arrows/kpf/yaml/kpf_canonical_io_adapter.h>

namespace KPF = kwiver::vital::kpf;

class diva_label::pimpl
{
public:
  size_t          track_id;
  std::string     obj_type;
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
  _pimpl->obj_type = "";
}


bool diva_label::is_valid() const
{
  if (_pimpl->track_id != -1 && !_pimpl->obj_type.empty())
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

bool diva_label::has_type() const
{
  return !_pimpl->obj_type.empty();
}
std::string diva_label::get_type() const
{
  return _pimpl->obj_type;
}
void diva_label::set_type(const std::string& l)
{ 
  _pimpl->obj_type = l; 
}
void diva_label::remove_type()
{
  _pimpl->obj_type = "";
}

void diva_label::write(std::ostream& os) const
{
  if (!is_valid())
    throw malformed_diva_data_exception("label packet is invalid");

  namespace KPFC = KPF::canonical;
  KPF::record_yaml_writer w(os);

  w.set_schema(KPF::schema_style::TYPES);
  w << KPF::writer< KPFC::id_t >(_pimpl->track_id, KPFC::id_t::TRACK_ID)
    << KPF::writer< KPFC::kv_t >("obj_type", _pimpl->obj_type)
    << KPF::record_yaml_writer::endl;
}
