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

#include <processes/diva_experiment_process.h>

#include <vital/vital_types.h>
#include <vital/types/timestamp.h>
#include <vital/types/image_container.h>
#include <vital/types/image.h>

#include <sprokit/processes/kwiver_type_traits.h>

#include <sprokit/pipeline/process_exception.h>
#include <sprokit/pipeline/datum.h>

#include <utils/diva_experiment.h>

// -- DEBUG
#if defined DEBUG
#include <opencv2/highgui/highgui.hpp>
#include <arrows/ocv/image_container.h>
#endif

namespace diva {

// (config-key, value-type, default-value, description )
create_config_trait( experiment_file_name, std::string, "",
                     "Name of the experiment file." );


//----------------------------------------------------------------
// Private implementation class
class diva_experiment_process::priv
{
public:
  priv();
  ~priv();

  std::string experiment_name;

  diva_experiment experiment;

}; // end priv class


// ================================================================

diva_experiment_process
::diva_experiment_process( kwiver::vital::config_block_sptr const& config )
  : process( config ),
    d( new diva_experiment_process::priv )
{
  make_ports();
  make_config();
}


diva_experiment_process
::~diva_experiment_process()
{
}


// ----------------------------------------------------------------
void diva_experiment_process
::_configure()
{
  scoped_configure_instrumentation();

  // Examine the configuration
  d->experiment_name = config_value_using_trait( experiment_file_name );

  if ( ! d->experiment.read_experiment( d->experiment_name ))
  {
    //+ would be better to get an exception from the reader so we could report specific failures.
    throw sprokit::invalid_configuration_exception( this->name(), "Invalid experiment configuration");
  }
}


// ----------------------------------------------------------------
void diva_experiment_process
::_step()
{
  // Test for end of input
  if ( ! d->experiment.get_input()->has_next_frame())
  {
    LOG_DEBUG( logger(), "End of input reached, process terminating" );

    // indicate done
    mark_process_as_complete();
    const sprokit::datum_t dat= sprokit::datum::complete_datum();

    push_datum_to_port_using_trait( timestamp, dat );
    push_datum_to_port_using_trait( image, dat );
    return;
  }

  kwiver::vital::timestamp ts = d->experiment.get_input()->get_next_frame_timestamp();
  kwiver::vital::image_container_sptr frame = d->experiment.get_input()->get_next_frame();

  // --- debug
#if defined DEBUG
  cv::Mat cv_image = kwiver::arrows::ocv::image_container::vital_to_ocv( frame->get_image() );
  cv::namedWindow( "Display window", cv::WINDOW_NORMAL );// Create a window for display.
  cv::imshow( "Display window", cv_image ); // Show our image inside it.

  cv::waitKey(0);                 // Wait for a keystroke in the window
#endif
  // -- end debug

  push_to_port_using_trait( timestamp, ts );
  push_to_port_using_trait( image, frame );

}


// ----------------------------------------------------------------
void diva_experiment_process
::make_ports()
{
  // Set up for required ports
  sprokit::process::port_flags_t optional;

  declare_output_port_using_trait( timestamp, optional );
  declare_output_port_using_trait( image, optional );
}


// ----------------------------------------------------------------
void diva_experiment_process
::make_config()
{
  declare_config_using_trait( experiment_file_name );
}


// ================================================================
diva_experiment_process::priv
::priv()
{
}


diva_experiment_process::priv
::~priv()
{
}

} // end namespace
