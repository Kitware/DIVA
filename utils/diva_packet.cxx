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

#include "diva_packet.h"
#include "diva_exceptions.h"
#include <yaml-cpp/yaml.h>

#include <arrows/kpf/yaml/kpf_yaml_writer.h>
#include <arrows/kpf/yaml/kpf_canonical_io_adapter.h>

namespace KPF = kwiver::vital::kpf;

diva_meta::diva_meta()
{
  _msg = "";
}
diva_meta::diva_meta(const std::string& msg)
{
  _msg = msg;
}
diva_meta::~diva_meta()
{
  
}

void diva_meta::clear()
{
  _msg = "";
}
bool diva_meta::is_valid() const
{
  return !_msg.empty();
}

bool diva_meta::has_msg() const
{
  return !_msg.empty();
}
std::string diva_meta::get_msg() const
{
  return _msg;
}
void diva_meta::set_msg(const std::string& msg)
{
  _msg = msg;
}
void diva_meta::remove_msg()
{
  _msg = "";
}

void diva_meta::write(std::ostream& os) const
{
  if (!is_valid())
    throw malformed_diva_data_exception("meta packet is invalid");

  KPF::record_yaml_writer w(os);
  w << KPF::writer< KPF::canonical::meta_t >(_msg)
    << KPF::record_yaml_writer::endl;
}

std::string diva_meta::to_string() const
{
  _ss.str("");
  write(_ss);
  return _ss.str();
}
