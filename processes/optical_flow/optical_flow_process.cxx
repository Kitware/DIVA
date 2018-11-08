/*ckwg +29
 * Copyright 2015-2017 by Kitware, Inc.
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
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS IS''
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

#include "optical_flow_process.h"

#include <vital/vital_types.h>

#include <vital/types/image_container.h>
#include <vital/types/image.h>
#include <vital/types/timestamp.h>

#include <arrows/ocv/image_container.h>

#include <sprokit/pipeline/process_exception.h>
#include <sprokit/pipeline/datum.h>
#include <sprokit/processes/kwiver_type_traits.h>

#include <opencv2/core/core.hpp>
#include <opencv2/core/utility.hpp>
#include <opencv2/opencv.hpp>
#include "opencv2/cudaoptflow.hpp"
#include "opencv2/cudaarithm.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"

#include <cstddef>


namespace diva {

// (config-key, value-type, default-value, description )
create_config_trait( output_image_width, int, "1920",
                     "Width of output image" );
create_config_trait( output_image_height, int, "1080",
                     "height of output image");


//----------------------------------------------------------------
// Private implementation class
class optical_flow_process::priv
{
public:
  priv();
  ~priv();

  // Brox optical flow parameters
  const float alpha_ = 0.197;
  const float gamma_ = 50;
  const float scale_factor_ = 0.8;
  const int inner_iterations_ = 10;
  const int outer_iterations_ = 77;
  const int solver_iterations_ = 10;

  size_t output_image_width, output_image_height;

  kwiver::vital::image_container_sptr input_container, output_container;
  kwiver::vital::timestamp tstamp;

  // Intialization of all the matrices on cpu and gpu  
  cv::Mat frame0, frame1, frame0_32FC1, frame1_32FC1, u_out, v_out,
      img_out;
  cv::cuda::GpuMat frame0_gpu, frame1_gpu, u_gpu_out, v_gpu_out, 
      flow_gpu_out;
  cv::cuda::GpuMat flow_planes[2];
  cv::Ptr<cv::cuda::BroxOpticalFlow> brox_flow_instance = 
                                  cv::cuda::BroxOpticalFlow::create(alpha_, 
                                                                    gamma_, 
                                                                    scale_factor_, 
                                                                    inner_iterations_, 
                                                                    outer_iterations_, 
                                                                    solver_iterations_);
   
}; // end priv class


// ================================================================

optical_flow_process
::optical_flow_process( kwiver::vital::config_block_sptr const& config )
  : process( config ),
    d( new optical_flow_process::priv )
{
  make_ports();
  make_config();
}


optical_flow_process
::~optical_flow_process()
{
}


// ----------------------------------------------------------------
void optical_flow_process
::_configure()
{
  scoped_configure_instrumentation();

  // Examine the configuration
  d->output_image_width = config_value_using_trait( output_image_width );
  d->output_image_height = config_value_using_trait( output_image_width );
  // Image where there is no previous image 
  d->frame0 = cv::Mat::zeros(d->output_image_height, d->output_image_width, CV_8UC1);
}


// ----------------------------------------------------------------
void optical_flow_process
::_step()
{
  d->input_container = grab_from_port_using_trait( image );
  d->tstamp = grab_from_port_using_trait( timestamp );  
  d->frame1 = kwiver::arrows::ocv::image_container::vital_to_ocv( 
                  d->input_container->get_image(), 
                  kwiver::arrows::ocv::image_container::ColorMode::RGB_COLOR );

  
  cv::resize(d->frame1, d->frame1, cvSize( d->output_image_height, d->output_image_width));
  cv::cvtColor(d->frame1, d->frame1, cv::COLOR_RGB2GRAY);
  cv::Mat frame0_32f, frame1_32f;
  d->frame0.convertTo(frame0_32f, CV_32F, 1.0/255.0);
  d->frame1.convertTo(frame1_32f, CV_32F, 1.0/255.0);
  
  frame0_32f.convertTo(d->frame0_32FC1, CV_32FC1);
  frame1_32f.convertTo(d->frame1_32FC1, CV_32FC1);
  d->frame0_gpu.upload(d->frame0_32FC1);
  d->frame1_gpu.upload(d->frame1_32FC1);
  
   
  d->brox_flow_instance->calc(d->frame0_gpu, d->frame1_gpu, d->flow_gpu_out);
  
  cv::cuda::split(d->flow_gpu_out, d->flow_planes);
  d->flow_planes[0].download(d->u_out);
  d->flow_planes[1].download(d->v_out); 
   
  optical_flow_process::color_code(d->u_out, d->v_out, d->img_out, 20.0);
  
  d->output_container = std::make_shared< kwiver::arrows::ocv::image_container >(d->img_out,
                          kwiver::arrows::ocv::image_container::ColorMode::RGB_COLOR);
  d->frame1.copyTo( d->frame0 );
  push_to_port_using_trait( image,  d->output_container);
}


// ----------------------------------------------------------------
void optical_flow_process
::make_ports()
{
  // Set up for required ports
  sprokit::process::port_flags_t optional;
  declare_input_port_using_trait( timestamp, optional );
  declare_input_port_using_trait( image, optional );
  declare_output_port_using_trait( image, optional );
}


// ----------------------------------------------------------------
void optical_flow_process
::make_config()
{
  declare_config_using_trait( output_image_height );
  declare_config_using_trait( output_image_width );
}


// ================================================================
optical_flow_process::priv
::priv()
{
}


optical_flow_process::priv
::~priv()
{
}

void optical_flow_process::color_code(const cv::Mat &u_mat, const cv::Mat &v_mat, 
                                      cv::Mat &image, double clip_value){
    // Obtained from https://gist.github.com/denkiwakame/56667938239ab8ee5d8a
    cv::Mat magnitude, angle, saturation;
    cv::cartToPolar(u_mat, v_mat, magnitude, angle, true);
    cv::normalize(magnitude, magnitude, 0, 255, cv::NORM_MINMAX);
    saturation =  cv::Mat::ones(magnitude.size(), CV_32F);
    cv::multiply(saturation, 255, saturation);
    cv::Mat hsvPlanes[] = { angle, saturation, magnitude };
    cv::merge(hsvPlanes, 3, image);
    cv::cvtColor(image, image, cv::COLOR_HSV2BGR);
}
} // end namespace
