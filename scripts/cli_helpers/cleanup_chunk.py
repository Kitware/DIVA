import argparse
import os
import warnings
import json

def main(args):
    if not os.path.exists(args.chunk_json):
        raise OSError("Invalid path {0} provided for Chunk.json".format(args.chunk_json))
    chunks = json.load(open(args.chunk_json, 'r'))
    if args.chunk_id in chunks.keys():
        video_names = chunks[args.chunk_id]["files"]
        for video_name in video_names:
            video_file = "{0}.json".format(os.path.splitext(video_name)[0])
            video_path = os.path.join(args.cache_dir, video_file)
            if os.path.exists(video_path):
                print("Removing {0}".format(video_path))
                os.remove(video_path)
            else:
                warnings.warn("Json file associated with {0} not found in {1}".format( video_name, args.cache_dir))
    else:
        raise KeyError("Invalid chunk id {0} provided".format(args.chunk_id))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunk-id", help="Chunk id")
    parser.add_argument("--chunk-json", help="JSON file with all the chunks")
    parser.add_argument("--cache-dir", help="Cache directory with the json files")
    args = parser.parse_args()
    main(args)
