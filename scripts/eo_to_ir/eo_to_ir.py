#!/usr/bin/env python3

import argparse
import os
import re
import itertools
from functools import reduce

import yaml

from lib.homography import load_homography_file, apply_homography


def load_yaml(path):
    with open(path, 'r') as inf:
        try:
            return yaml.safe_load(inf)
        except yaml.YAMLError as exc:
            print(exc)
            exit(1)


def load_yaml_list(path):
    out_recs = []
    with open(path, 'rb') as inf:
        for line in inf:
            try:
                out_recs.extend(yaml.safe_load(line))
            except yaml.YAMLError as exc:
                print(exc)
                exit(1)

    return out_recs


def parse_activities_yaml(path):
    yaml_activities = load_yaml(path)
    actor_lookup = {}
    for item in yaml_activities:
        if 'act' not in item:
            continue

        # Build an actor lookup table so that we can update their time
        # extents more easily ("id1" is is the actor ID)
        for actor_rec in item.get('act').get('actors', []):
            actor_lookup.setdefault(actor_rec.get('id1'), []).append(
                item.get('act'))

    return yaml_activities, actor_lookup


def parse_geom_yaml(path):
    yaml_geom = load_yaml_list(path)
    geoms_by_actor = {}
    non_geom_records = []
    for item in yaml_geom:
        if 'geom' not in item:
            non_geom_records.append(item)
            continue

        geom_rec = item.get('geom')
        geoms_by_actor.setdefault(geom_rec.get('id1'), []).append(geom_rec)

    return yaml_geom, non_geom_records, geoms_by_actor


def kpf_yaml_dump(obj):
    if isinstance(obj, dict):
        kv_strs = []
        for k, v in obj.items():
            k_str = kpf_yaml_dump(k)
            bare_v_str = kpf_yaml_dump(v)
            if k_str == "meta" and isinstance(v, str):
                v_str = f"\"{bare_v_str}\""
            else:
                v_str = bare_v_str

            kv_strs.append(f"{k_str}: {v_str}")

        return "{{ {} }}".format(
            ", ".join(kv_strs))
    elif isinstance(obj, list):
        return "[{}]".format(', '.join(map(kpf_yaml_dump, obj)))
    else:
        return str(obj)


def _build_cropper(crop_bounds):
    min_x, min_y = 0.0, 0.0
    max_x, max_y = crop_bounds

    def _f(bounds):
        x0, y0, x1, y1 = bounds
        c_x0 = min(max(x0, min_x), max_x)
        c_x1 = min(max(x1, min_x), max_x)
        c_y0 = min(max(y0, min_y), max_y)
        c_y1 = min(max(y1, min_y), max_y)
        return (c_x0, c_y0, c_x1, c_y1)

    return _f


def map_and_crop_geoms(geoms_by_actor, crop_bounds, map_fn=None):
    # The map_fn (function) parameter function, should modify the
    # geom_rec in place
    cropper_fn = _build_cropper(crop_bounds)

    def _geom_reducer(init, geom_rec):
        if map_fn is not None:
            map_fn(geom_rec)

        x0, y0, x1, y1 = cropper_fn(map(float, geom_rec.get('g0').split(' ')))

        # Only keep geoms with bounding boxes that have a non-zero
        # area (i.e. that haven't been cropped to nothing)
        if x0 != x1 and y0 != y1:
            geom_rec['g0'] = ' '.join(map(str, (x0, y0, x1, y1)))
            init.append(geom_rec)

        return init

    cropped_geoms_by_actor = {}
    for actor_id, geom_recs in geoms_by_actor.items():
        cropped_geoms_by_actor[actor_id] = reduce(_geom_reducer, geom_recs, [])

    return cropped_geoms_by_actor


def _build_homography_mapper(homography_file):
    homography = load_homography_file(homography_file)

    def _apply_homography(geom_rec):
        new_bounds = apply_homography(
            homography,
            [float(b) for b in geom_rec.get('g0').split(' ')])

        geom_rec['g0'] = ' '.join(map(str, new_bounds))

        # geom_rect is modified in place, so returning here is just a
        # convenience
        return geom_rec

    return _apply_homography


def _build_time_shifter(frame_offset, framerate):
    time_offset = frame_offset / framerate

    def _apply_offset(geom_rec):
        geom_rec['ts0'] += frame_offset
        # NOTE ** Formatting our timestamps to 3 decimal places
        geom_rec['ts1'] = float("%0.3f" % (geom_rec['ts1'] + time_offset))

        # geom_rect is modified in place, so returning here is just a
        # convenience
        return geom_rec

    return _apply_offset


def compose(f, g):
    def _h(*args):
        return f(g(*args))
    return _h


def dump_geoms_as_kw18(geoms, num_track_frames_lookup, outdir):
    outpath = os.path.join(outdir, "output.geom.kw18")

    with open(outpath, 'w') as of:
        for geom in geoms:
            track_id = geom.get('id1')
            x0, y0, x1, y1 = map(float, geom.get('g0').split())
            cx = (x0 + x1) / 2
            cy = (y0 + y1) / 2
            kw18_rec = (track_id,
                        num_track_frames_lookup.get(track_id, 0),
                        geom.get('ts0'),
                        cx,
                        cy,
                        0.0,
                        0.0,
                        cx,
                        cy,
                        x0,
                        y0,
                        x1,
                        y1,
                        (x1 - x0) * (y1 - y0),
                        0.0,
                        0.0,
                        0.0,
                        geom.get('ts1'))

            print(" ".join(map(str, kw18_rec)), file=of)


def main(args):
    yaml_activities, actor_activity_lookup =\
        parse_activities_yaml(args.input_activities)

    yaml_geoms, non_geom_records, geoms_by_actor =\
        parse_geom_yaml(args.input_geom)

    geom_mapper_fns = []
    if args.homography_file is not None:
        geom_mapper_fns.append(
            _build_homography_mapper(args.homography_file))

    if args.frame_offset is not None:
        geom_mapper_fns.append(
            _build_time_shifter(args.frame_offset,
                                args.framerate))

    geom_mapper_fn = reduce(compose, geom_mapper_fns, lambda x: x)
    crop_bounds = map(float, args.crop_bounds.split('x'))
    cropped_geoms_by_actor = map_and_crop_geoms(
        geoms_by_actor,
        crop_bounds,
        map_fn=geom_mapper_fn)

    os.makedirs(args.output_dir, exist_ok=True)

    # This is needed for when we dump out the kw18
    num_frames_per_actor = {}
    with open(os.path.join(args.output_dir, "output.geom.yml"), 'w') as of:
        # Write out non-geom records preserved from the original/input
        # geoms file
        for non_geom_rec in non_geom_records:
            print(f"- {kpf_yaml_dump(non_geom_rec)}", file=of)

        # Write out updated geoms; keep track of new actor time ranges
        for actor_id, geom_recs in cropped_geoms_by_actor.items():
            if len(geom_recs) == 0:
                # We have no remaining geom records surviving the crop for
                # the given actor, remove the actor from all activites
                for activity in actor_activity_lookup[actor_id]:
                    activity['actors'] = [a for a in activity.get('actors', [])
                                          if a.get('id1') != actor_id]
            else:
                min_ts0, max_ts0 = float('inf'), 0.0
                for geom_rec in geom_recs:
                    min_ts0 = min(geom_rec.get('ts0', min_ts0), min_ts0)
                    max_ts0 = max(geom_rec.get('ts0', max_ts0), max_ts0)
                    # Write out the geom record
                    print(f"- {kpf_yaml_dump({'geom': geom_rec})}", file=of)

                num_frames_per_actor[actor_id] = max_ts0 - min_ts0
                # Update timespans for the given actor
                for activity in actor_activity_lookup[actor_id]:
                    for actor_rec in activity.get('actors', []):
                        if actor_rec.get('id1') != actor_id:
                            continue

                        for timespan in actor_rec.get('timespan', []):
                            timespan['tsr0'] = [min_ts0, max_ts0]

    # Dump kw18 of geoms
    dump_geoms_as_kw18(itertools.chain(*cropped_geoms_by_actor.values()),
                       num_frames_per_actor,
                       args.output_dir)

    with open(os.path.join(args.output_dir, "output.act.yml"), 'w') as of:
        out_meta_records = []
        out_activity_records = []
        activity_counts = {}
        for activity in yaml_activities:
            if 'meta' in activity:
                meta_val = activity.get('meta')
                if(isinstance(meta_val, str) and
                   re.search(r'\w+ \d+ instances', meta_val)):
                    continue
                else:
                    out_meta_records.append(activity)
                continue

            # Only modify / process activiy records that are actually
            # activity records (e.g. not "meta" records)
            if 'act' in activity:
                # Adjust the timespans of each activity based on the
                # already adjusted actor timespans
                actors = activity.get('act').get('actors', [])
                if len(actors) == 0:
                    # Don't output activities which have no constituent
                    # actors after the crop
                    continue

                min_actor_ts0, max_actor_ts0 = float('inf'), 0.0
                for actor in actors:
                    for timespan in actor.get('timespan', []):
                        actor_ts0_start, actor_ts0_end = timespan.get('tsr0')
                        min_actor_ts0 = min(actor_ts0_start, min_actor_ts0)
                        max_actor_ts0 = max(actor_ts0_end, max_actor_ts0)

                for timespan in activity.get('act').get('timespan', []):
                    timespan['tsr0'] = [min_actor_ts0, max_actor_ts0]

                # Count the instances for out meta counts
                for activity_name, count in activity.get('act', {}).get('act2', {}).items():
                    activity_counts[activity_name] =\
                        activity_counts.get(activity_name, 0) + count

                out_activity_records.append(activity)

        for out_meta_rec in out_meta_records:
            print(f"- {kpf_yaml_dump(out_meta_rec)}", file=of)

        for activity_name, count in activity_counts.items():
            meta_rec = {"meta": f"{activity_name} {int(count)} instances"}
            print(f"- {kpf_yaml_dump(meta_rec)}", file=of)

        for out_activity_rec in out_activity_records:
            print(f"- {kpf_yaml_dump(out_activity_rec)}", file=of)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Given a homography, a time offset and a pair of geom and "
        "activity YAML files, crop the activities")
    parser.add_argument("-g", "--input-geom",
                        type=str,
                        required=True,
                        help="Path to input geometry KPF YAML to warp and "
                        "crop")
    parser.add_argument("-a", "--input-activities",
                        type=str,
                        required=True,
                        help="Path to input activity KPF YAML")
    parser.add_argument("-H", "--homography-file",
                        type=str,
                        help="Path to homography text file")
    parser.add_argument("-o", "--output-dir",
                        type=str,
                        help="Output directory for warped and cropped results")
    parser.add_argument("-b", "--crop-bounds",
                        type=str,
                        default="352x240",
                        help="Output frame bounds for cropping")
    parser.add_argument("-F", "--framerate",
                        type=float,
                        default=30.0,
                        help="Source video framerate for calculating "
                        "timestamp offset (default is 30)")
    parser.add_argument("-f", "--frame-offset",
                        type=int,
                        help="Number of frames to shift each geom record")

    main(parser.parse_args())
