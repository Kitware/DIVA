/*ckwg +29
 * Copyright 2018 by Kitware, Inc.
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

#ifndef DIVA_EXPERIMENT_PROCESS_H
#define DIVA_EXPERIMENT_PROCESS_H

#include <sprokit/pipeline/process.h>
#include <processes/diva_experiment/diva_processes_export.h>

#include <memory>

namespace diva {

// ----------------------------------------------------------------
/** Parse experiment file to provide input for other processes.
 *
 * * Input Ports
 *  * None
 * 
 * * Output Ports
 *  * ``image`` Image obtained from experiment source specified in the experiment file (Required)
 *  * ``timestamp`` Frame number associated with the image (Required)
 *  * ``file_name`` Input source (Required)
 *
 * * Configuration
 *  * ``experiment_file_name`` DIVA experiment file 
 *
 */
class DIVA_PROCESSES_NO_EXPORT diva_experiment_process
  : public sprokit::process
{
public:
  /*
   * Constructor for diva_experiment_process
   * @param config Configuration for diva_experiment_process
   */
  diva_experiment_process( kwiver::vital::config_block_sptr const& config );
  /*
   * Destructor for diva_experiment_process
   */
  virtual ~diva_experiment_process();

protected:
  /*
   * Configure diva_experiment_process
   */
  virtual void _configure();
  /*
   * Step function for diva_experiment_process
   */
  virtual void _step();

private:
  /*
   * Helper function to make ports of the process
   */
  void make_ports();
  /*
   * Helper function to make configuration of the process
   */
  void make_config();

  class priv;
  const std::unique_ptr<priv> d;
}; // end class diva_experiment_process

}  // end namespace

#endif // DIVA_EXPERIMENT_PROCESS_H
