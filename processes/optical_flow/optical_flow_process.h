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

#ifndef OPTICAL_FLOW_PROCESS_H
#define OPTICAL_FLOW_PROCESS_H

#include <sprokit/pipeline/process.h>
#include <processes/optical_flow/diva_optical_flow_export.h>

#include <memory>
#include <opencv2/core/core.hpp>

namespace diva {

// ----------------------------------------------------------------
/** Online GPU based Optical Flow using Opencv's Brox Optical Flow using successive images.
 *
 * * Input Ports
 *  * ``image`` Image obtained input source (Required)
 *  * ``timestamp`` Frame number associated with the image (Required)
 * 
 * * Output Ports
 *  * ``image`` RGB representation of the optical flow image (Required)
 *
 * * Configuration
 *  * ``output_image_width`` Width of the output image
 *  * ``output_image_height`` Height of the output image 
 *
 */
class DIVA_OPTICAL_FLOW_NO_EXPORT optical_flow_process
  : public sprokit::process
{
public:
  optical_flow_process( kwiver::vital::config_block_sptr const& config );
  virtual ~optical_flow_process();
  void color_code(const cv::Mat &u_mat, const cv::Mat &v_mat, 
                  cv::Mat &image, double clip_value);
protected:
  virtual void _configure();
  virtual void _step();

private:
  void make_ports();
  void make_config();

  class priv;
  const std::unique_ptr<priv> d;
}; // end class optical_flow_process

}  // end namespace

#endif // OPTICAL_FLOW_PROCESS_H
