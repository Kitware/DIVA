import argparse
import json
import os

def main(args):
    if not os.path.exists(args.chunk_json):
        raise OSError("Invalid path {0} provided for Chunk.json".format(args.chunk_json))
    if not os.path.exists(args.experiment_root):
        raise OSError("Invalid path {0} provided for experiment_root"\
                .format(args.experiment_root))
    if not os.path.exists(args.out_video_root):
        raise OSError("Invalid path {0} provided for json_root"\
                .format(args.out_video_root))

    chunks = json.load(open(args.chunk_json, 'r'))
    if args.chunk_id in chunks.keys():
        chunk_files = chunks[args.chunk_id]["files"]
        for video_name in chunk_files:
            video_folder, _ = os.path.splitext(video_name)
            experiment_file_name = video_folder + "_experiment.yml"
            experiment_path = os.path.join(args.experiment_root,
                                            experiment_file_name)
            json_path = os.path.join(args.out_video_root,
                                        video_folder + ".json")
            if not os.path.exists(experiment_path):
                raise OSError("Invalid path {0} provided for experiment_path"\
                        .format(experiment_path))
            print("Json path: {0}".format(json_path))
            pipeline_command = ("pipeline_runner -p pipelines/rc3d.pipe " + \
                                "--set exp:experiment_file_name={0} " + \
                                "--set json_writer:json_path={1} " + \
                                "--set json_writer:activity_index={2}")\
                                .format(experiment_path, json_path, args.activity_index)
            has_pipeline_failed = os.system(pipeline_command)
            if has_pipeline_failed:
                raise Exception("Unable to finish processing the chunk")

    else:
        raise KeyError("Invalid chunk id {0} provided".format(args.chunk_id))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunk-id",
            help="Chunk id over which the pipeline would run")
    parser.add_argument("--chunk-json", help="JSON file with all the chunks")
    parser.add_argument("--experiment-root",
            help="Root folder where experiment.yml are stored")
    parser.add_argument("--out-video-root",
            help="Root folder where json file for a video is saved")
    parser.add_argument("--activity-index", default="",
            help="Activity index provided by NIST")
    args = parser.parse_args()
    main(args)
