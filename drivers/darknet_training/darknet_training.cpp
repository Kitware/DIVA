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
#include <iostream>
#include "diva_geometry.h"
#include "diva_label.h"
#include "diva_exceptions.h"

#include <kwiversys/CommandLineArguments.hxx>
#include <kwiversys/SystemTools.hxx>
#include <kwiversys/Directory.hxx>
typedef kwiversys::SystemTools ST;

#include <arrows/kpf/yaml/kpf_reader.h>
#include <arrows/kpf/yaml/kpf_yaml_parser.h>
#include <arrows/kpf/yaml/kpf_yaml_writer.h>
#include "opencv2/highgui/highgui.hpp"

/// This file will read in the diva geometry and label annotations and generate darknet training files

//
// Program options support

typedef kwiversys::CommandLineArguments argT;

struct options_t
{
  bool help;                  // did the user ask for help?
  bool clean;                 // did the user ask for a cleaning?
  std::string frames_dir;     // root directory of the image files
  std::string kpf_dir;        // root directory of the kpf truth files
  std::string image_ext;      // extension to use when looking for image files
  int exit_code;              // if we exit, exit with this code

  explicit options_t(argT& arg);
  bool check_for_sanity_and_help();
};

void ListFiles(const std::string& root_dir, const std::string& dir, std::map<std::string,std::vector<std::string>>& file_map, const std::string& mask)
{
  kwiversys::Directory kwDir;
  kwDir.Load(dir);

  // Can we Start i=2, assuming 0=/. and 1=/..
  for (unsigned long i = 0; i < kwDir.GetNumberOfFiles(); ++i)
  {
    std::string file = kwDir.GetFile(i);
    if (ST::StringEndsWith(file, ".") || ST::StringEndsWith(file, ".."))
      continue;

    std::string path = kwDir.GetPath();
    std::string file_path = path;
    file_path += "/" + file;

    if (ST::FileIsDirectory(file_path))
    {
      ListFiles(root_dir,file_path, file_map, mask);
    }
    else
    {
      //remove the root path fromt the path
      path = path.substr(root_dir.length());
      if (mask.empty())
      {
        file_map[path].push_back(file);
      }
      else
      {
        if (file.find(mask) != std::string::npos)
          file_map[path].push_back(file);
      }
    }
  }
}
void ListFiles(const std::string& dir, std::map<std::string, std::vector<std::string>>& file_map, const std::string& mask)
{
  ListFiles(dir, dir, file_map, mask);
}

void clean(const std::string& frames_dir)
{
  // Only delete all the *.txt files and leave the image files
  std::map<std::string, std::vector<std::string>> training_files;//key=dir,val=image files in that dir
  ListFiles(frames_dir, training_files, ".txt");
  for (auto itr : training_files)
    for (std::string f : itr.second)
      ST::RemoveFile(frames_dir + "/" + itr.first + "/" + f);
}

namespace KPF = kwiver::vital::kpf;
bool create_training_files(const std::string& frames_dir, const std::string& kpf_dir)
{
  clean(frames_dir);

  std::string file;
  // DIVA Detection classes
  std::vector<std::string> types;
  types.push_back("Vehicle");
  types.push_back("Person");
  types.push_back("Tree");
  types.push_back("Umbrella");
  types.push_back("Construction_Barrier");
  types.push_back("Door");
  types.push_back("Prop");
  types.push_back("Bike");
  types.push_back("Parking_Meter");
  types.push_back("Push_Pulled_Object");
  types.push_back("Trees");
  types.push_back("Dumpster");
  types.push_back("Construction_Vehicle");
  types.push_back("Receptacle");
  types.push_back("Other");
  types.push_back("ATM");
  types.push_back("Animal");
  types.push_back("Articulated_Infrastructure");
  
  // Create our data file
  file = frames_dir + "/darknet.data.txt";
  std::cout << "Creating file : " << file << std::endl;
  std::ofstream dfile;
  dfile.open(file);
  dfile << "classes=" << types.size() << std::endl;
  dfile << "train = train.darknet.txt" << std::endl;
  dfile << "test = test.darknet.txt" << std::endl;
  dfile << "names = darknet.names.txt" << std::endl;
  dfile << "backup = /" << std::endl;
  dfile.close();

  // Create our names file
  file = frames_dir + "/darknet.names.txt";
  std::cout << "Creating file : " << file << std::endl;
  std::ofstream nfile;
  nfile.open(file);
  for (std::string t : types)
    nfile << t << std::endl;
  nfile.close();

  // Create our train file that lists every image we will use
  file = frames_dir + "/train.darknet.txt";
  std::cout << "Creating file : " << file << std::endl;
  std::ofstream train_file;
  train_file.open(file);

  std::vector<std::string> split;
  std::map<std::string,std::vector<std::string>> frame_files;//key=dir,val=image files in that dir
  std::map<std::string,std::vector<std::string>> kpf_files;//key=dir,val=yaml files in that dir

  ListFiles(kpf_dir, kpf_files, ".yml");
  ListFiles(frames_dir, frame_files, ".png");
  // This will look thourgh the frames_dir for frame files, then try to find the same directory
  // under the kpf_dir
  // - kpf_dir directorires that have no matching frames directory will be ignored
  // - frames_dir directoryes that have no matching truth directory will be ignored
  std::string line;
  std::string geom_file;
  std::string label_file;
  std::map<size_t,diva_label*> labels;
  std::map<size_t,std::vector<diva_geometry*>> geoms;

  // Look for the corresponding kpf files associated with this frames directory
  for (auto fItr : frame_files)
  {
    geom_file = "";
    label_file = "";
    // The yaml files we are looking for are based on the frames directory name
    ST::SplitPath(fItr.first, split);
    std::string search = split[split.size() - 1];
    // Check to see if the kpf directory structure is the same as the frames directory structure
    // Then we just need to look there instead of everywhere
    {// Intential scope addition
      auto kpfItr = kpf_files.find(fItr.first);
      if (kpfItr != kpf_files.end())
      {
        for (auto yaml_file : kpfItr->second)
        {
          if (yaml_file == search + ".geom.yml")
            geom_file = kpf_dir + "/" + kpfItr->first + "/" + yaml_file;
          else if ((yaml_file == search + ".types.yml"))
            label_file = kpf_dir + "/" + kpfItr->first + "/" + yaml_file;
        }
      }
      else
      {
        // Well, the directory sturcture is not matching,
        // Let's just iterate through everything and look for our yml files
        for (auto kpf : kpf_files)
        {
          for (auto yaml_file : kpf.second)
          {
            if (ST::StringStartsWith(yaml_file, search.c_str()))
            {
              if (yaml_file == search + ".geom.yml")
                geom_file = kpf_dir + "/" + kpf.first + "/" + yaml_file;
              else if (yaml_file == search + ".types.yml")
                label_file = kpf_dir + "/" + kpf.first + "/" + yaml_file;
            }
          }
        }
      }
    }
   
    // Make sure we have a geom_file
    if (geom_file.empty())
    {
      std::cout << "Could not find an associated geom file, skipping frame set" << std::endl;
      continue;
    }
    std::ifstream geom_stream(geom_file);
    if (!geom_stream)
    {
      std::cerr << "Could not open geom file " << geom_file << std::endl;
      continue;
    }
    if (label_file.empty())
    {
      std::cout << "Could not find an associated label file, skipping frame set" << std::endl;
      continue;
    }
    std::ifstream types_stream(label_file);
    if (!types_stream)
    {
      std::cerr << "Could not open types file " << label_file << std::endl;
      continue;
    }

    int cnt = 0;
    std::cout << "Reading geom file " << geom_file;
    while (std::getline(geom_stream, line))
    {
      // Only grab the geom packets
      if (line.find("geom:") != std::string::npos)
      {
        if (cnt++ > 50)
        {
          std::cout << ".";
          cnt = 0;
        }
        diva_geometry* g = new diva_geometry();
        g->from_string(line);
        geoms[g->get_frame_id()].push_back(g);
      }
    }
    std::cout << std::endl;

    std::cout << "Reading label file " << label_file;
    while (std::getline(types_stream, line))
    {
      // Only grab the geom packets
      if (line.find("types:") != std::string::npos)
      {
        std::cout << ".";
        diva_label* label = new diva_label();
        label->from_string(line);
        labels[label->get_track_id()] = label;
      }
    }
    std::cout << std::endl;

    // Loop over the image files associated with this training set/video
    int fid = -1;
    for (auto image : fItr.second)
    {
      fid++;
      ST::MakeDirectory(frames_dir + "/" + fItr.first);
      // Create dir/file in the dest_location for this labels file
      file = frames_dir + "/" + fItr.first + "/" + image;
      // Load this image file up in open cv and get its width/height
      cv::Mat img = cv::imread(file);
      int image_width = img.size().width;
      int image_height = img.size().height;
      img.release();
      // Add the image file to our list of images to train with
      train_file << file << std::endl;
      //Write out the detections associated with this image
      ST::ReplaceString(file, ".png", ".txt");
      std::cout << "Creating file : " << file << std::endl;
      std::ofstream tfile;
      tfile.open(file);

      // Loop over the geoms and add a line in the labels file for each bounding box
      for (diva_geometry* g : geoms[fid])
      {
        diva_label* label = labels[g->get_track_id()];
        size_t label_idx = std::distance(types.begin(), find(types.begin(), types.end(), label->get_max_classification()));

        // convert pixel coordinates to the percentages darknet wants
        double dw = 1. / image_width;
        double dh = 1. / image_height;
        double  x = (g->get_bounding_box_pixels().get_x1() + g->get_bounding_box_pixels().get_x2()) / 2.0;
        double  y = (g->get_bounding_box_pixels().get_y1() + g->get_bounding_box_pixels().get_y2()) / 2.0;
        double  w = g->get_bounding_box_pixels().get_x2() - g->get_bounding_box_pixels().get_x1();
        double  h = g->get_bounding_box_pixels().get_y2() - g->get_bounding_box_pixels().get_y1();
        tfile << label_idx << " " << x*dw << " " << y*dh << " " << w*dw << " " << h*dh << std::endl;
      }
      tfile.close();
    }// end loop over image files

     // Clear out things from examining this directory set
    if (!geoms.empty())
    {
      for (auto f : geoms)
        for (auto g : f.second)
          delete g;
      geoms.clear();
    }
    if (!labels.empty())
    {
      for (auto i : labels)
        delete i.second;
    }
    labels.clear();

  }// end loop over image directories
  train_file.close();

  return true;
}


// ----------------------------------------
// main
// ----------------------------------------

int main(int argc, const char* argv[])
{
  //
  // Parse and check the options
  //

  argT arg;
  arg.Initialize(argc, argv);
  options_t options(arg);

  if (!arg.Parse())
  {
    std::cerr << "Problem parsing arguments\n";
    exit(EXIT_FAILURE);
  }

  if (options.check_for_sanity_and_help())
  {
    exit(options.exit_code);
  }

  // If a cleaning was requested
  if (options.clean)
    clean(options.frames_dir);

  // If kpf is provided, generate training files
  if (!options.kpf_dir.empty())
  {
    bool okay = create_training_files(options.frames_dir,options.kpf_dir);
    const std::string& status = okay ? std::string("success") : std::string("error");
    std::cout << status << " Building training file from frame_dir " << options.frames_dir << " using truth kpgs from kpf_dir " << options.kpf_dir << "'\n";
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
::options_t(argT& arg) :
  help(false), clean(false), frames_dir(""), kpf_dir(""), image_ext(".png"), exit_code(EXIT_SUCCESS)
{
  arg.AddArgument("-h", argT::NO_ARGUMENT, &(this->help),
    "Display usage information");
  arg.AddArgument("--help", argT::NO_ARGUMENT, &(this->help),
    "Display usage information");
  arg.AddArgument("-f", argT::SPACE_ARGUMENT, &(this->frames_dir),
    "Directory containing frames files");
  arg.AddArgument("--frames", argT::EQUAL_ARGUMENT, &(this->frames_dir),
    "Directory containing frames files"); 
  arg.AddArgument("-t", argT::SPACE_ARGUMENT, &(this->kpf_dir),
    "Directory containing truth kpf files");
  arg.AddArgument("--truth", argT::EQUAL_ARGUMENT, &(this->kpf_dir),
    "Directory containing truth kpf files"); 
  arg.AddArgument("-e", argT::SPACE_ARGUMENT, &(this->image_ext),
    "File extension to use when searching for all images to train against");
  arg.AddArgument("--ext", argT::EQUAL_ARGUMENT, &(this->image_ext),
    "File extension to use when searching for all images to train against");
  arg.AddArgument("-c", argT::NO_ARGUMENT, &(this->clean),
    "Delete training files from the frames_dir");
  arg.AddArgument("--clean", argT::NO_ARGUMENT, &(this->clean),
    "Delete training files from the frames_dir");
}

//
// some sanity checking
//

bool
options_t
::check_for_sanity_and_help()
{
  bool main_should_exit(false), print_help(this->help);

  if (frames_dir.empty())
    print_help = true;

  if (!ST::StringStartsWith(image_ext, "."))
    image_ext = "." + image_ext;

  if (print_help)
  {
    main_should_exit = true;
    std::cout
      << "You MUST provide a root directory containing the image frames\n"
      << "This program generates training files for darknet in the frames directory .\n"
      << "  -f DIR / --frames=DIR   Root directory containing frames\n"
      << "This program will recursivily search for all image files under this directory\n"
      << "This program assumes each directory of image files is alphabetically/numerically named to presere the ordered where the first frame is first file\n"
      << "  i.e. 00001.png, 00002.png, 00003.png, etc...\n"
      << "\n"
      << "To generate training files, you MUST provide a directory of kpf truth files with the option: \n"
      << "  -t DIR / --truth=DIR    Root directory containing truth kpf files\n"
      << "Trianing files are generated for each image directory located under the root frames directory.\n"
      << "This program will use the name of all directories containing image files, and look for kpf files whose names\n"
      << "are the same as those image directories. Once 1 or more image directories are associated with kpf files, \n"
      << "this program will generate a training txt file for each image file in the corresponding image directory.\n"
      << "Other training files will be generated in the frames root directory needed by darknet.\n"
      << "!! NOTE, You will still need to provide either a pretraing convolutional weights file, or a network cfg file !!\n"
      << "Our training was done using :\n"
      << "  - The pretrained Imagenet file https://pjreddie.com/media/files/darknet19_448.conv.23 \n"
      << "  - The yolo-voc.2.0.cfg file https://github.com/pjreddie/darknet/blob/master/cfg/yolov2-voc.cfg \n"
      << "      - Change 'classes=20' to 'classes=18' near the end of the cfg file.\n"
      << "Using : darknet.exe detector train darknet.data.txt yolo-voc.2.0.cfg darknet19_448.conv.23\n"
      << "\n"
      << "You may choose to clean out the generated training files, without generating new files with the option: \n"
      << "  -c / --clean            clean out all training files from the frames_dir\n"
      << "\n"
      << "Other Options are:\n"
      << "  -h / --help             Display this message and exit\n"
      << "  -e / --ext              Change the image extentsion used to search for images under the frames root directory, the default is '.png'\n"
      << "\n";
  }

  return main_should_exit;
}

// =================================================================
