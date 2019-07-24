import argparse
import os
import warnings
import json

def remove_file(file_path):
    if os.path.exists(file_path):
        print("Removing {0}".format(file_path))
        os.remove(file_path)
    else:
        warnings.warn("{0} not found".format(file_path))

def main(args):
    if not os.path.exists(args.chunk_json):
        raise OSError("Invalid path {0} provided for Chunk.json".format(args.chunk_json))
    chunks = json.load(open(args.chunk_json, 'r'))
    if args.chunk_id in chunks.keys():
        video_names = chunks[args.chunk_id]["files"]
        for video_name in video_names:
            video_name = os.path.splitext(video_name)[0]
            json_file = "{0}.json".format(video_name)
            yml_file = "{0}_experiment.yml".format(video_name)
            imagelist_file = "{0}_imagelist.txt".format(video_name)
            json_path = os.path.join(args.cache_dir, json_file)
            yml_path  =  os.path.join(args.cache_dir, yml_file)
            imagelist_path = os.path.join(args.cache_dir, imagelist_file)
            remove_file(json_path)
            remove_file(yml_path)
            if os.path.exists(imagelist_path):
                remove_file(imagelist_path)
    else:
        raise KeyError("Invalid chunk id {0} provided".format(args.chunk_id))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunk-id", help="Chunk id")
    parser.add_argument("--chunk-json", help="JSON file with all the chunks")
    parser.add_argument("--cache-dir", help="Cache directory with the json files")
    args = parser.parse_args()
    main(args)
