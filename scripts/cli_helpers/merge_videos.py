import argparse
import os
import json

def merge_video_json( json_dict, video_json, current_activity_id ):
    json_dict["filesProcessed"].extend(video_json["filesProcessed"])
    for activity in video_json["activities"]:
        activity["activityID"] += current_activity_id
        json_dict["activities"].append(activity)
    current_activity_id += len(video_json["activities"])
    return json_dict, current_activity_id

def main(args):
    if not os.path.exists(args.chunk_json):
        raise OSError("Invalid path {0} provided for Chunk.json".format(args.chunk_json))
    if not os.path.exists(args.chunk_json):
        raise OSError("Invalid path {0} provided for video_root"\
                .format(args.video_root))
    chunks = json.load(open(args.chunk_json, 'r'))
    json_dict = { "filesProcessed": [],
                  "activities": []
                }
    current_activity_id = 1
    if args.chunk_id in chunks.keys():
        chunk_files = chunks[args.chunk_id]["files"]
        for video_name in chunk_files:
            video_folder, _ = os.path.splitext(video_name)
            json_path = os.path.join(args.video_root,
                                        video_folder + ".json")
            video_json = json.load(open(json_path, 'r'))
            if not os.path.exists(json_path):
                raise OSError("Not output found for {0}"\
                        .format(video_name))
            json_dict, current_activity_id = merge_video_json(json_dict, video_json,
                                                               current_activity_id)
        chunk_file_name = args.chunk_id + ".json"
        chunk_path = os.path.join(args.out_chunk_root, chunk_file_name)
        json.dump(json_dict, open(chunk_path, 'w'), indent=2)
    else:
        raise KeyError("Invalid chunk id {0} provided".format(args.chunk_id))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunk-id",
            help="Chunk id over which the pipeline would run")
    parser.add_argument("--chunk-json", help="JSON file with all the chunks")
    parser.add_argument("--video-root",
            help="Root folder where json file for a video is saved")
    parser.add_argument("--out-chunk-root",
            help="Root folder where json file for a chunk is saved")
    args = parser.parse_args()
    main(args)
