/*ckwg +29
* Copyright 2017,2018 by Kitware, Inc.
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

#include <cstdlib>
#include <fstream>
#include <ostream>
#include "diva_experiment.h"
#include "diva_input.h"
#include "diva_exceptions.h"

// KWIVER Spcecific files for images
#include "vital/exceptions.h"
#include "vital/types/image_container.h"
#include "vital/plugin_loader/plugin_manager.h"

#include <kwiversys/CommandLineArguments.hxx>
#include <kwiversys/SystemTools.hxx>

// We will show the frames provided by the input API in an OCV window
#include "opencv2/highgui/highgui.hpp"
#include "arrows/ocv/image_container.h"


//
// Program options support

typedef kwiversys::CommandLineArguments argT;

struct options_t
{
  bool help;                  // did the user ask for help?
  std::string sample_exp_fn;  // location to write sample experiment file
  std::string user_exp_fn;    // location of user's experiment file
  int exit_code;              // if we exit, exit with this code

  explicit options_t( argT& arg );
  bool check_for_sanity_and_help();
};

//
// prototypes
//

bool write_sample_experiment( const std::string& fn );
bool display_experiment_frames( const std::string& fn );

// ----------------------------------------
// main
// ----------------------------------------

int main(int argc, const char* argv[])
{
  //
  // Parse and check the options
  //

  argT arg;
  arg.Initialize( argc, argv );
  options_t options( arg );

  if ( ! arg.Parse() )
  {
    std::cerr << "Problem parsing arguments\n";
    exit( EXIT_FAILURE );
  }

  if ( options.check_for_sanity_and_help() )
  {
    exit( options.exit_code );
  }

  //
  // If requested, write out sample experiment file
  //

  if ( ! options.sample_exp_fn.empty() )
  {
    bool okay = write_sample_experiment( options.sample_exp_fn );
    const std::string& status = okay? std::string("success") : std::string("error");
    std::cout << status << " writing sample experiment file to '" << options.sample_exp_fn << "'\n";
  }

  //
  // If requested, run the experiment
  //

  if ( ! options.user_exp_fn.empty() )
  {
    bool okay = display_experiment_frames( options.user_exp_fn );
    const std::string& status = okay? std::string("success") : std::string("error");
    std::cout << status << " running experiment '" << options.user_exp_fn << "'\n";
  }

  //
  // all done
  //
}

// =================================================================

//
// constructor for the options
//

options_t
::options_t( argT& arg):
  help(false), sample_exp_fn(""), user_exp_fn(""), exit_code( EXIT_SUCCESS )
{
  arg.AddArgument( "-h",       argT::NO_ARGUMENT, &(this->help),
                   "Display usage information" );
  arg.AddArgument( "--help",   argT::NO_ARGUMENT, &(this->help),
                   "Display usage information" );
  arg.AddArgument( "-s",       argT::SPACE_ARGUMENT, &(this->sample_exp_fn),
                   "Write sample experiment file to filename and exit" );
  arg.AddArgument( "--sample", argT::EQUAL_ARGUMENT, &(this->sample_exp_fn),
                   "Write sample experiment file to filename and exit" );
  arg.AddArgument( "-d",       argT::SPACE_ARGUMENT, &(this->user_exp_fn),
                   "Run the experiment named by the file" );
  arg.AddArgument( "--display",    argT::EQUAL_ARGUMENT, &(this->user_exp_fn),
                   "Run the experiment named by the file" );
}

//
// some sanity checking
//

bool
options_t
::check_for_sanity_and_help()
{
  bool main_should_exit( false ), print_help( this->help );
  std::string err_msg("");
  if ( ! this->help )
  {
    if ( (! this->sample_exp_fn.empty()) && (! this->user_exp_fn.empty()))
    {
      err_msg = "Must set only one of '-d' or '-s'";
    }
    else if (this->sample_exp_fn.empty() && this->user_exp_fn.empty())
    {
      err_msg = "Must set at least one of '-d' or '-s'";
    }
    else if ((! this->sample_exp_fn.empty())
             && kwiversys::SystemTools::FileExists( this->sample_exp_fn ))
    {
      err_msg = "Won't write sample over existing file";
    }
    if (! err_msg.empty() )
    {
      print_help = true;
      main_should_exit = true;
      this->exit_code = EXIT_FAILURE;
    }
  }
  if (print_help)
  {
    std::cout
      << "This program can do 2 things.\n"
      << " * Write an example experiment file\n"
      << " * Read an example experiment file and display the frames of the experiment source with the input API\n"
      << "\n"
      << "Options are:\n"
      << "  -h / --help          display this message and exit\n"
      << "  -d FN / --display=FN show the frames from the experiment file FN\n"
      << "  -s FN / --sample=FN  write a sample experiment to FN and exit\n"
      << "\n";
  }

  if (! err_msg.empty())
  {
    std::cerr << "Error: " << err_msg << std::endl;
  }

  return main_should_exit;
}

// =================================================================

//
// Create a sample experiment file and write it out to the given
// filename. Return true if successful.
//

bool
write_sample_experiment( const std::string& fn )
{
  diva_experiment ex;

  ex.set_type(diva_experiment::type::object_detection);
  ex.set_dataset_id( "VIRAT_S_000000" );

  // You can set input type to either a video file
  // or a file listing individual frame images

  // ex.set_input_type(diva_experiment::input_type::video);
  // ex.set_input_source("VIRAT_S_000000.mp4");
  ex.set_input_type(diva_experiment::input_type::file_list);
  ex.set_input_source( "VIRAT_S_000000.frames.txt" );

  ex.set_transport_type(diva_experiment::transport_type::disk);
  ex.set_frame_rate_Hz(30);

  ex.set_input_root_dir( "/your/path/to/input_root_directory" );
  ex.set_output_type(diva_experiment::output_type::file);
  ex.set_output_root_dir( "/your/path/to/output_root_directory" );

  return ex.write_experiment( fn );
}

// =================================================================

bool
display_experiment_frames( const std::string& fn )
{
  namespace KV=kwiver::vital;

  //
  // Framework: initialization
  //
  // The following code loads the experiment, ensures that it's an object_detection
  // task, and opens our output file
  //

  diva_experiment ex;
  if (!ex.read_experiment( fn ))
  {
    throw malformed_diva_data_exception("Invalid experiment configuration");
  }
 
  //
  // KWIVER: initialization
  //
  // The following code initializes KWIVER
  KV::plugin_manager::instance().load_all_plugins();

  //
  // Framework: loading the experiment
  //
  // This code creates a diva input point and initializes it via the
  // experiment file.

  diva_input input;
  if(!input.load_experiment( ex ))
  {
    throw malformed_diva_data_exception( "Failed to initialize experiment input source" );
  }

  
  //
  // Framework:
  // -- looping over input frames specified by the experiment
  kwiver::vital::timestamp ts;
  kwiver::vital::image_container_sptr frame;
  while (input.has_next_frame())
  {
    frame = input.get_next_frame();
    ts = input.get_next_frame_timestamp();

    // Convert the frame to opencv formate and display
    cv::Mat _mat = kwiver::arrows::ocv::image_container::vital_to_ocv(frame->get_image());
    cv::namedWindow("Input Frame", cv::WINDOW_AUTOSIZE);// Create a window for display.
    cv::imshow("Input Frame", _mat);                    // Show our image inside it.
    cv::waitKey(2000);                                  // Wait for 2s
    cvDestroyWindow("Input Frame");

  } // ...for all the frames in the input

  return true;
}


