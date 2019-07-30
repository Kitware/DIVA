import argparse
import os
import warnings
import json

def main(args):
    if not os.path.exists(args.chunk_json):
        raise OSError("Invalid path {0} provided for Chunk.json".format(args.chunk_json))
    chunks = json.load(open(args.chunk_json, 'r'))
    for chunk_id in chunks.keys():
        chunk_file = "{0}.json".format(chunk_id)
        chunk_path = os.path.join(args.cache_dir, chunk_file)
        if os.path.exists( chunk_path ):
            print("Removing {0}".format(chunk_path))
            os.remove(chunk_path)
        else:
            warnings.warn("Json file associated with {0} not found in {1}".format( chunk_id, args.cache_dir))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunk-json", help="JSON file with all the chunks")
    parser.add_argument("--cache-dir", help="Cache directory with the json files")
    args = parser.parse_args()
    main(args)
