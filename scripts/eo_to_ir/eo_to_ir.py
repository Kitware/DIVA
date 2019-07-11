#!/usr/bin/env python3

import argparse
import os
import re
import itertools
from functools import reduce

from lib.homography import load_homography_file, apply_homography
from lib.camera_io import load_camera_krtd_file
from lib.view import view_to_view
from lib.utils import (parse_activities_yaml,
                       parse_geom_yaml,
                       parse_type_yaml,
                       abort_if_file_exists,
                       kpf_yaml_dump,
                       dump_geoms_as_kw18,
                       area_of_bounds)
from lib.transduce import (xd_map,
                           xd_filter,
                           appender,
                           xd)


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


def _build_geom_cropper(crop_bounds):
    cropper_fn = _build_cropper(crop_bounds)

    def _geom_cropper(geom):
        orig_bounds = tuple(map(float, geom.get('g0').split(' ')))
        cropped_bounds = cropper_fn(orig_bounds)
        x0, y0, x1, y1 = cropped_bounds

        geom['g0'] = ' '.join(map(str, cropped_bounds))
        # Keep track of how much of the bounding box remains after
        # cropping
        geom['_ov0'] = (area_of_bounds(cropped_bounds) /
                        area_of_bounds(orig_bounds))

        return geom

    return _geom_cropper


def geom_0area_filter(geom):
    x0, y0, x1, y1 = tuple(map(float, geom.get('g0').split(' ')))

    return x0 != x1 and y0 != y1


def strip_geom_internal_fields(geom):
    # Any field with a leading underscore should be stripped off prior
    # to dumping
    to_remove = []
    for k in geom.keys():
        if k.startswith('_'):
            to_remove.append(k)

    for k in to_remove:
        del geom[k]

    return geom


def _build_offscreen_flagger(min_overlap):
    def _offscreen_flagger(geom):
        if geom.get('_ov0', float('Inf')) < min_overlap:
            geom["occlusion"] = "off-screen"

        return geom

    return _offscreen_flagger


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


def _build_cam_to_cam_mapper(src_cam_file, dest_cam_file):
    src_cam = load_camera_krtd_file(src_cam_file)
    dest_cam = load_camera_krtd_file(dest_cam_file)

    def _apply_cam_to_cam_map(geom_rec):
        new_bounds = view_to_view(
            src_cam,
            dest_cam,
            [float(b) for b in geom_rec.get('g0').split(' ')])

        if new_bounds is None:
            new_bounds = (-1, -1, -1, -1)

        geom_rec['g0'] = ' '.join(map(str, new_bounds))

        # geom_rect is modified in place, so returning here is just a
        # convenience
        return geom_rec

    return _apply_cam_to_cam_map


def main(args):
    yaml_activities, actor_activity_lookup =\
        parse_activities_yaml(args.input_activities)

    yaml_geoms, non_geom_records, geoms_by_actor =\
        parse_geom_yaml(args.input_geom)

    yaml_types, yaml_type_by_actor =\
        parse_type_yaml(args.input_types)

    geom_mapper_fns = []

    # Pre-crop mapping
    if args.homography_file is not None:
        geom_mapper_fns.append(
            xd_map(_build_homography_mapper(args.homography_file)))

    if args.frame_offset is not None:
        geom_mapper_fns.append(
            xd_map(_build_time_shifter(args.frame_offset,
                                       args.framerate)))

    if args.camera_to_camera is not None:
        src_cam_file, dest_cam_file =\
            map(str.strip, args.camera_to_camera.split(':'))

        geom_mapper_fns.append(
            xd_map(_build_cam_to_cam_mapper(src_cam_file,
                                            dest_cam_file)))

    crop_bounds = map(float, args.crop_bounds.split('x'))
    geom_mapper_fns.append(
        xd_map(_build_geom_cropper(crop_bounds)))

    # Post-crop mapping
    if args.min_spatial_overlap is not None:
        geom_mapper_fns.append(
            xd_map(_build_offscreen_flagger(args.min_spatial_overlap)))

    geom_pipeline = xd(*geom_mapper_fns,
                       xd_filter(geom_0area_filter),
                       xd_map(strip_geom_internal_fields))

    cropped_geoms_by_actor = {}
    for actor, actor_geoms in geoms_by_actor.items():
        cropped_geoms_by_actor[actor] =\
            reduce(geom_pipeline(appender), actor_geoms, [])

    os.makedirs(args.output_dir, exist_ok=True)

    # This is needed for when we dump out the kw18
    num_frames_per_actor = {}

    # Useful for generating our output "types" file
    surviving_actors = set()

    # Since we're using the input basename for our output filename,
    # want to prevent ourselves from accidently overwriting the input
    # file if we're not careful when specifying our output directory
    out_geom_path = os.path.join(
        args.output_dir, os.path.basename(args.input_geom))
    abort_if_file_exists(out_geom_path)
    with open(out_geom_path, 'w') as of:
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
                surviving_actors.add(actor_id)
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
    kw18_base, _ = os.path.splitext(args.input_geom)
    kw18_outpath = os.path.join(args.output_dir, f"{kw18_base}.kw18")
    abort_if_file_exists(kw18_outpath)
    dump_geoms_as_kw18(itertools.chain(*cropped_geoms_by_actor.values()),
                       num_frames_per_actor,
                       kw18_outpath)

    out_act_path = os.path.join(
        args.output_dir, os.path.basename(args.input_activities))
    abort_if_file_exists(out_act_path)
    with open(out_act_path, 'w') as of:
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

    out_types_path = os.path.join(
        args.output_dir, os.path.basename(args.input_types))
    abort_if_file_exists(out_types_path)
    with open(out_types_path, 'w') as of:
        for type_rec in yaml_types:
            # Preserving "meta" records
            if 'meta' in type_rec:
                print(f"- {kpf_yaml_dump(type_rec)}", file=of)

        for actor_id in sorted(surviving_actors):
            type_rec = yaml_type_by_actor[actor_id]
            print(f"- {kpf_yaml_dump(type_rec)}", file=of)


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
    parser.add_argument("-t", "--input-types",
                        type=str,
                        required=True,
                        help="Path to input types KPF YAML")
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
    parser.add_argument("-C", "--camera-to-camera",
                        type=str,
                        help="Two KRTD camera file paths (colon-separated)"
                        "being the source:destination cameras")
    parser.add_argument("--min-spatial-overlap",
                        type=float,
                        help='Minimum spatial overlap (as a ratio of post to '
                        'pre-crop area) required to not be considered '
                        'occluded ("off-screen")')

    main(parser.parse_args())
