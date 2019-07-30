import diva.utils as du
import os
import argparse
import json

def _generate_dummy_output(diva_experiment):
    """
    Fill output attributes of diva_experiment to pass the validity test
    :params diva_experiments: An instance of diva_experiment
    :return diva_experiment instance with the dummy output values
    """
    diva_experiment.set_output_type(du.experiment_output_type.file)
    # Add dummy values for algorithm
    diva_experiment.set_output_root_dir(".")
    diva_experiment.set_algorithm_executable("./bin/darknet_detections -r $expfn")
    return diva_experiment

def generate_experiment_file_from_videos(video_root, experiment_root, video_name):
    """
    Generate experiment files from video
    :param video_root: Root folder of the videos
    :param experiment_root: Root folder where experiment specification would be stored in yml file
    :param video_name: Name of the video
    :return None
    """
    experiment_file_name = os.path.splitext(video_name)[0] + "_experiment.yml"
    diva_experiment = du.experiment()
    diva_experiment.set_type(du.experiment_type.activity_detection)
    diva_input = diva_experiment.get_input()
    diva_input.set_dataset_id(video_name)
    diva_input.set_frame_rate_Hz(30)
    diva_input.set_video_file_source(video_root, video_name)
    _generate_dummy_output(diva_experiment)
    if diva_experiment.is_valid():
        diva_experiment.write_experiment(os.path.join(experiment_root, experiment_file_name))
    else:
        raise Exception("Invalid experiment file")

def generate_experiment_file_from_images(image_root, experiment_root, imagelist_root,
                                         video_name):
    """
    Generate experiment files from images
    :param image_root: Root folder with images
    :param experiment_root: Root folder where experiment specification would be stored in yml file
    :param imagelist_root: Root folder where a text file containing path to images of a video would be stored
    :param video_name: Name of the video
    :return None
    """
    experiment_file_name = os.path.basename(image_root) + "_experiment.yml"
    imagelist_file_name = os.path.basename(image_root) + "_imagelist.txt"

    with open(os.path.join(imagelist_root, imagelist_file_name), "w") as f:
        for image_name in sorted(os.listdir(image_root)):
            image_path = os.path.join(image_root, image_name)
            f.write(image_path + "\n")
    diva_experiment = du.experiment()
    diva_experiment.set_type(du.experiment_type.activity_detection)
    diva_input = diva_experiment.get_input()
    diva_input.set_dataset_id(video_name)
    diva_input.set_frame_rate_Hz(30)
    diva_input.set_image_list_source(imagelist_root,
                                     imagelist_file_name)
    _generate_dummy_output(diva_experiment)
    if diva_experiment.is_valid():
        diva_experiment.write_experiment(os.path.join(experiment_root, experiment_file_name))
    else:
        raise Exception("Invalid experiment file")

def main(args):
    """
    Main function
    :param args: Command line arguments from argparser
    """
    if not os.path.exists(args.chunk_json):
        raise OSError("Invalid path {0} provided for Chunk.json".format(args.chunk_json))
    if not os.path.exists(args.data_root):
        raise OSError("Invalid path {0} provided for data root".format(args.data_root))

    all_videos = os.listdir(args.data_root)
    chunks = json.load(open(args.chunk_json, 'r'))

    if not os.path.exists(args.experiment_root):
        print("{0} not found. Creating {0}.".format(args.experiment_root))
        os.makedirs(args.experiment_root)
    if args.imagelist_root is not None:
        if not os.path.exists(args.imagelist_root):
            print("{0} not found. Creating {0}.".format(args.imagelist_root))
            os.makedirs(args.imagelist_root)

    if args.chunk_id in chunks.keys():
        chunk_files = chunks[args.chunk_id]["files"]
        for video_name in chunk_files:
            if args.use_videos:
                if video_name not in all_videos:
                    raise OSError("{0} is not present in {1}".format(video_name,
                                                                     args.data_root))
                generate_experiment_file_from_videos(args.data_root,
                                                     args.experiment_root,
                                                     video_name)
            else:
                video_folder, _ = os.path.splitext(video_name)
                if video_folder not in all_videos:
                   raise OSError("{0} is not present in {1}".format(video_name,
                                                                    args.data_root))
                generate_experiment_file_from_images(os.path.join(args.data_root, video_folder),
                                                     args.experiment_root,
                                                     args.imagelist_root,
                                                     video_name)
    else:
        raise KeyError("Invalid chunk id {0} provided".format(args.chunk_id))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunk-id",
                help="Chunk id for which experiment file would be generated")
    parser.add_argument("--chunk-json", help="JSON file with all the chunks")
    parser.add_argument("--data-root", help="Root folder for image directory")
    parser.add_argument("--experiment-root", help="Root folder where experiment.yml would be stored")
    parser.add_argument("--imagelist-root", help="Root folder where imagelist.txt would be stored")
    parser.add_argument("--use-videos", action='store_true',
            help="Flag to specify that videos instead of image folders are present in data-root")
    parser.set_defaults(use_videos=False)
    args = parser.parse_args()
    main(args)
