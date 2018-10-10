// optical_flow.cpp
// Computes optical flow frames for VIRAT dataset using OpenCV GPU based implementation
// Dependencies: OpenCV and Kwiversys
// Author: Ameya Shringi (ameya.shringi@kitware.com)
//
#define _USE_MATH_DEFINES


#include <iostream>
#include <sys/time.h>
#include <time.h>
#include <string>
#include <chrono>
#include <cmath>
#include <vector>
#include <iterator>
#include <utility>

#include <opencv2/core/core.hpp>
#include <opencv2/core/utility.hpp>
#include <opencv2/opencv.hpp>
#include "opencv2/cudaoptflow.hpp"
#include "opencv2/cudaarithm.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"

#include <kwiversys/CommandLineArguments.hxx>
#include <kwiversys/SystemTools.hxx>
#include <kwiversys/Directory.hxx>
typedef kwiversys::SystemTools ST;
typedef kwiversys::CommandLineArguments argT;


struct commandline_options_t
{
    bool help;                    // flag to determine is user asked for help
    std::string video_directory;  // root directory of virat frames
    std::string output_directory; // root directory where optical flow would be stored
    std::string image_extension;  // extension for the images
    int flow_type;                // optical flow algorithm used
    int gpu_id;                   // gpu used by optical flow
    int skip_frames;              // number of frames between current frame and previous frame
    int exit_code;                // exit with this code

    explicit commandline_options_t(argT& arg);
    bool sanity_check_and_help();
};

class ViratOpticalFlow{
    private:
        std::string video_dir_;
        std::string output_dir_;
        std::string img_extension_;
        int gpu_id_;
        int skip_frames_;
        
        // Global variables for gpu::BroxOpticalFlow
        const float alpha_ = 0.197;
        const float gamma_ = 50;
        const float scale_factor_ = 0.8;
        const int inner_iterations_ = 10;
        const int outer_iterations_ = 77;
        const int solver_iterations_ = 10;
    public:
        ViratOpticalFlow()
            :video_dir_("/data/diva/V1-Frames"),
            output_dir_("/data/diva/V1-Frames-Flow"),
            img_extension_("png"),
            gpu_id_(1),
            skip_frames_(1)
        {}

        ViratOpticalFlow(std::string video_dir,
                std::string output_dir,
                std::string img_extension,
                int gpu_id,
                int skip_frames)
            :video_dir_(video_dir),
            output_dir_(output_dir),
            img_extension_(img_extension),
            gpu_id_(gpu_id),
            skip_frames_(skip_frames)
        {}  

        /*
         * Create optical flow image from u and v vectors of optical flow  
         */
        void color_code(const cv::Mat &u_mat, const cv::Mat &v_mat, 
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

        /*
         * Write the optical flow image in the output path. The function 
         * recusively creates directories if they don't exist
         */
        bool write_image(const cv::Mat &img_out, std::string output_path){
            std::string output_dir = ST::GetParentDirectory(output_path);
            if (!ST::FileExists(output_dir, false)){
                bool dir_made = ST::MakeDirectory(output_dir);
                if (!dir_made){
                    return dir_made;
                }
            }
            return cv::imwrite(output_path, img_out);                  
        }

        /*
         * Determine the previous image name based on the current image name for
         * optical flow image pairs 
         */
        std::string get_prev_image(std::string image_name){
            image_name = ST::SplitString(image_name, '.').at(0);
            const int num_chars = image_name.size();
            try
            {
                const int image_number = std::stoi(image_name, nullptr);
                const int prev_number = image_number - skip_frames_;
                std::string prev_image_name = std::to_string(prev_number);
                const int leading_zeros = num_chars - prev_image_name.size();
                prev_image_name = std::string(leading_zeros, '0').append(prev_image_name);
                prev_image_name += img_extension_;
                return prev_image_name;
            } catch (const std::invalid_argument& ia){
                std::cerr << "Invalid image number, " << ia.what() << std::endl;
                return std::string();
            }
        }

        /*
         * Recursively iterate through directories to find files that match the 
         * mask
         */
        void ListFilePairs(const std::string& dir, 
                std::vector<std::pair<std::string,std::string>>& image_pairs, 
                const std::string& mask)
        {
            kwiversys::Directory kwDir;
            kwDir.Load(dir);
            // Can we Start i=2, assuming 0=/. and 1=/..
            for (unsigned long i = 0; i < kwDir.GetNumberOfFiles(); ++i)
            {
                std::string file = kwDir.GetFile(i);
                if (ST::StringEndsWith(file, ".") || 
                    ST::StringEndsWith(file, "..") || 
                    ST::StringEndsWith(file, "@Recycle")) continue;
                  
                std::string path = kwDir.GetPath();
                std::string file_path = path;
                file_path += "/" + file;
                if (ST::FileIsDirectory(file_path))
                {
                    ListFilePairs(file_path, image_pairs, mask);
                }else
                {
                    std::string prev_file = get_prev_image(file);
                    if (prev_file.empty()){
                        std::cerr << "Previous file not found substituting it with current file" 
                                    << std::endl;
                        prev_file = file;
                    }
                    std::string prev_file_path = path;
                    prev_file_path += "/" + prev_file;
                    if (!ST::FileExists(prev_file_path, true)){
                        prev_file_path = file_path;
                    }
                    
                    std::pair <std::string, std::string> image_pair(file_path,
                            prev_file_path);
                    if (file.find(mask) != std::string::npos && 
                        prev_file.find(mask) != std::string::npos){
                            image_pairs.push_back(image_pair);
                    }
                }
            }
        }

        void ListFiles(const std::string& dir, 
                std::vector<std::string>& image_paths,
                const std::string& mask){
            kwiversys::Directory kwDir;
            kwDir.Load(dir);
            // Can we Start i=2, assuming 0=/. and 1=/..
            for (unsigned long i = 0; i < kwDir.GetNumberOfFiles(); ++i)
            {
                std::string file = kwDir.GetFile(i);
                if (ST::StringEndsWith(file, ".") || 
                    ST::StringEndsWith(file, "..")) continue; 
                std::string path = kwDir.GetPath();
                std::string file_path = path;
                file_path += "/" + file;
                if (ST::FileIsDirectory(file_path))
                {
                    ListFiles(file_path, image_paths, mask);
                }else
                {
                    if (file.find(mask) != std::string::npos){
                        image_paths.push_back(file_path);
                    }            
                }
            }
        }
        
        /*
         * compute optical flow for all the images in the video_directory
         */
        void compute_flow(const int flow_type){
            // Verify gpu info
            cv::cuda::setDevice(gpu_id_);
            cv::cuda::printShortCudaDeviceInfo(cv::cuda::getDevice());
          
            // Intialization of all the matrices on cpu and gpu  
            cv::Mat frame0, frame1, frame0_32FC1, frame1_32FC1, u_out, v_out,
                img_out;
            cv::cuda::GpuMat frame0_gpu, frame1_gpu, u_gpu_out, v_gpu_out, 
                flow_gpu_out;
            cv::cuda::GpuMat flow_planes[2];
            
            // optical flow instances
            cv::Ptr<cv::cuda::BroxOpticalFlow> brox_flow_instance = 
                    cv::cuda::BroxOpticalFlow::create(alpha_, gamma_, 
                            scale_factor_, inner_iterations_, 
                            outer_iterations_, solver_iterations_);
            cv::Ptr<cv::cuda::OpticalFlowDual_TVL1> tvl_flow_instance = 
                    cv::cuda::OpticalFlowDual_TVL1::create();
            
            if (!ST::FileExists(video_dir_, false)){
                std::cerr << "Video root: " << video_dir_ << " missing" << std::endl;
                return;
            }
            if (!ST::FileExists(output_dir_, false)){
                std::cerr << "Output base: " << output_dir_ << " missing" << std::endl;
                return;                    
            }

            // Create image pair
            std::vector<std::pair<std::string, std::string>> image_pairs;
            ListFilePairs(video_dir_, image_pairs, img_extension_);
            
            // Iterate through image pairs
            std::vector<std::pair<std::string, std::string>>::iterator 
                image_pair_itr;
            std::string current_image, previous_image, output_path;
            for (image_pair_itr=image_pairs.begin(); 
                    image_pair_itr<image_pairs.end(); image_pair_itr++){
                current_image = image_pair_itr->first;
                previous_image = image_pair_itr->second;
                output_path = current_image;
                // Output has same path except different root directory
                ST::ReplaceString(output_path, video_dir_, 
                        output_dir_);
                if (ST::FileExists(output_path, true)){
                    //std::cout << output_path << " already exits." << std::endl;
                    continue;
                }
           
                auto start = std::chrono::high_resolution_clock::now();
                // Read image and appropriate convert the matrix into 
                // CV_32FC1 as it is the only format supported by cuda optflow
                frame0 = cv::imread(previous_image.c_str(), 
                                CV_LOAD_IMAGE_GRAYSCALE);
                frame1 = cv::imread(current_image.c_str(),
                                 CV_LOAD_IMAGE_GRAYSCALE);
                if (frame0.empty() || frame1.empty()){
                    std::cerr << "Skipping: " << current_image  << std::endl;
                    continue;
                }

                frame0.convertTo(frame0, CV_32F, 1.0/255.0);
                frame1.convertTo(frame1, CV_32F, 1.0/255.0);

                frame0.convertTo(frame0_32FC1, CV_32FC1);
                frame1.convertTo(frame1_32FC1, CV_32FC1);
                frame0_gpu.upload(frame0_32FC1);
                frame1_gpu.upload(frame1_32FC1);
                // Computing optical flow
                if (flow_type == 0){
                    brox_flow_instance->calc(frame0_gpu, frame1_gpu, flow_gpu_out);
                }else{
                    tvl_flow_instance->calc(frame0_gpu, frame1_gpu, flow_gpu_out);
                }
                cv::cuda::split(flow_gpu_out, flow_planes);
                flow_planes[0].download(u_out);
                flow_planes[1].download(v_out); 
                // Create flow images and write them
                if (!u_out.empty() and !v_out.empty()){
                    color_code(u_out, v_out, img_out, 20.0);
                    bool write_successful = write_image(img_out, 
                                                      output_path);
                    if (!write_successful){
                        std::cerr << "Failed to write " << 
                                  output_path << std::endl;
                    }
                }else{
                    std::cerr << "No flow image created" << std::endl;
                }
                
                auto finish = std::chrono::high_resolution_clock::now();
                std::chrono::duration<double> elapsed = finish - start;
                std::cout << "Elapsed time: " << elapsed.count() << " s\n";

            }
        }

        void verify_flow(const int flow_type){
            // Intialization of all the matrices on cpu and gpu  
            cv::Mat frame0, frame1, frame0_32FC1, frame1_32FC1, u_out, v_out,
                img_out, flow_image;
            cv::cuda::GpuMat frame0_gpu, frame1_gpu, u_gpu_out, v_gpu_out, 
                flow_gpu_out;
            cv::cuda::GpuMat flow_planes[2];
            
            // optical flow instances
            cv::Ptr<cv::cuda::BroxOpticalFlow> brox_flow_instance = 
                    cv::cuda::BroxOpticalFlow::create(alpha_, gamma_, 
                            scale_factor_, inner_iterations_, 
                            outer_iterations_, solver_iterations_);
            cv::Ptr<cv::cuda::OpticalFlowDual_TVL1> tvl_flow_instance = 
                    cv::cuda::OpticalFlowDual_TVL1::create();
            std::vector<std::string> flow_paths;
            ListFiles(output_dir_, flow_paths, img_extension_);
            std::cout << "Number of images: " << flow_paths.size() << std::endl;
            std::vector<std::string>::iterator flow_iterator;
            std::string current_path, previous_path, flow_path;
            for (flow_iterator=flow_paths.begin(); flow_iterator<flow_paths.end();
                    flow_iterator++){
                flow_path = *flow_iterator;
                if (ST::FileExists(flow_path, true)){
                    flow_image = cv::imread(flow_path.c_str());
                    
                    if (flow_image.data == NULL){
                        std::cout << "Corrupt image" << flow_path << std::endl;
                        auto start = std::chrono::high_resolution_clock::now();
                        current_path = flow_path;
                        ST::ReplaceString(current_path, output_dir_, 
                                video_dir_);
                        std::string current_image_name = 
                            ST::GetFilenameName(current_path);
                        std::string prev_image_name = 
                            get_prev_image(current_image_name);
                        std::string parent_directory = 
                            ST::GetParentDirectory(current_path);
                        std::string prev_image_path = parent_directory + "/" +
                                                    prev_image_name;
                        std::cout << "flow path:" << flow_path << std::endl;
                        std::cout << "image path: " << current_path << std::endl;
                        std::cout << "previous image path: " << prev_image_path <<
                            std::endl;
                        if (!ST::FileExists(prev_image_path, true)){
                            ST::ReplaceString(prev_image_path, prev_image_name,
                                                current_image_name);
                        }
                        frame0 = cv::imread(prev_image_path.c_str(), 
                                            CV_LOAD_IMAGE_GRAYSCALE);
                        frame1 = cv::imread(current_path.c_str(),
                                             CV_LOAD_IMAGE_GRAYSCALE);
                        if (frame0.empty() || frame1.empty()){
                            std::cerr << "Skipping: " << current_image_name
                                          << std::endl;
                            continue;
                        }

                        frame0.convertTo(frame0, CV_32F, 1.0/255.0);
                        frame1.convertTo(frame1, CV_32F, 1.0/255.0);

                        frame0.convertTo(frame0_32FC1, CV_32FC1);
                        frame1.convertTo(frame1_32FC1, CV_32FC1);
                        frame0_gpu.upload(frame0_32FC1);
                        frame1_gpu.upload(frame1_32FC1);
                        // Computing optical flow
                        if (flow_type == 0){
                            brox_flow_instance->calc(frame0_gpu, frame1_gpu, 
                                    flow_gpu_out);
                        }else{
                            tvl_flow_instance->calc(frame0_gpu, frame1_gpu, 
                                    flow_gpu_out);
                        }
                        cv::cuda::split(flow_gpu_out, flow_planes);
                        flow_planes[0].download(u_out);
                        flow_planes[1].download(v_out); 
                        // Create flow images and write them
                        if (!u_out.empty() and !v_out.empty()){
                            color_code(u_out, v_out, img_out, 20.0);
                            bool write_successful = write_image(img_out, 
                                                              flow_path);
                            if (!write_successful){
                                std::cerr << "Failed to write " << 
                                          flow_path << std::endl;
                            }else{
                                std::cout << "Writing: " << 
                                        flow_path << std::endl;
                            }
                        }else{
                            std::cerr << "No flow image created" << std::endl;
                        }
                        
                        auto finish = std::chrono::high_resolution_clock::now();
                        std::chrono::duration<double> elapsed = finish - start;
                        std::cout << "Elapsed time: " << elapsed.count() << " s\n";

                    }
                }
            }
        }
};   


int main(int argc, char *argv[]){
    argT commandline_args;
    commandline_args.Initialize(argc, argv);
    commandline_options_t options(commandline_args);
    if (!commandline_args.Parse()){
        std::cerr << "Unable to parse arguments" << std::endl;
        exit(EXIT_FAILURE);
    }

    if (options.sanity_check_and_help()){
        exit(options.exit_code);
    }
    ViratOpticalFlow virat_optical_flow = ViratOpticalFlow(options.video_directory,
                                    options.output_directory, options.image_extension,
                                    options.gpu_id, options.skip_frames);
    virat_optical_flow.compute_flow(options.flow_type);
    std::cout << "Verifying flow images" << std::endl;
    virat_optical_flow.verify_flow(options.flow_type);
}


commandline_options_t::commandline_options_t(argT& arg):
    help(false), 
    video_directory("/data/diva/v1-frames"), 
    output_directory("/data/diva/v1-flow-brox"), 
    image_extension(".png"), 
    flow_type(0), gpu_id(0), skip_frames(1),  exit_code(EXIT_SUCCESS){
        arg.AddArgument("-h", argT::NO_ARGUMENT, &(this->help), 
                "Display usage information");
        arg.AddArgument("--help", argT::NO_ARGUMENT, &(this->help), 
                "Display usage information");
        arg.AddArgument("--video_directory", argT::EQUAL_ARGUMENT, 
                &(this->video_directory), "path to virat v1 frames directory");
        arg.AddArgument("--output_directory", argT::EQUAL_ARGUMENT,
                &(this->output_directory), "path to output directory");
        arg.AddArgument("--image_extension", argT::EQUAL_ARGUMENT,
                &(this->image_extension), "Extension of the image");
        arg.AddArgument("--gpu_id", argT::EQUAL_ARGUMENT,
                &(this->gpu_id), "Gpu where optical flow is extracted");
        arg.AddArgument("--skip_frames", argT::EQUAL_ARGUMENT,
                &(this->skip_frames), "frames skipped between consecutive frames");
        arg.AddArgument("--flow_type", argT::EQUAL_ARGUMENT,
                &(this->flow_type), "Optical flow algorithm used (0: Brox, 1:TVL1)");
    }

bool commandline_options_t::sanity_check_and_help(){
    bool main_should_exit(false), print_help(this->help);
    if (!ST::StringStartsWith(image_extension, ".")){
        image_extension = "." + image_extension;
    }

    if (print_help){
        main_should_exit = true;
        std::cout << "Compute optical from successive frames and store it as image files\n" 
                << "--video_directory     Root directory where virat frames are stored\n" 
                << "--output_directory     Root directory where optical flow frames are stored\n"
                << "--image_extension     Extension of the images in dataset\n" 
                << "--gpu_id     Gpu on which optical flow runs\n" 
                << "--skip_frames   Skip frames between consecutive frames\n" 
                << "-h  --help  Display usage information and exit\n";    
    }
    return main_should_exit;
}

