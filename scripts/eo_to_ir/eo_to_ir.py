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


def _build_activity_time_shifter(frame_offset):
    def _apply_offset(activity_rec):
        for timespan_rec in itertools.chain(
                activity_rec.get('timespan', []),
                *[a.get('timespan', []) for a in
                  activity_rec.get('actors')]):
            timespan_rec['tsr0'] =\
                [t + frame_offset for t in timespan_rec.get('tsr0', [])]

        return activity_rec

    return _apply_offset


def _build_activity_timespan_adjuster(geoms_by_actor_by_ts0,
                                      geom_qualifier=lambda g: True,
                                      minimum_frames=0):
    # Correct our activity timespans against mapped/filtered (cropped)
    # geom records.  The 'geom_qualifier' function determines whether
    # a given geom should be taken into account when considering the
    # bounds (e.g. if a geom record is "off-screen"); 'minimum_frames'
    # is the number of geoms that pass the 'geom_qualifier' for the
    # actor to be kept in the event
    # ** NOTE ** This function assumes that there's only a single
    # ** record for a given "timespan" value

    def _adjust_timespans_reducer(out_activities, activity_rec):
        min_ts0, max_ts0 = float('inf'), -float('inf')
        adjusted_actors = []
        for actor_rec in activity_rec.get('actors', []):
            actor_id = actor_rec['id1']

            min_a_ts0, max_a_ts0 = float('inf'), -float('inf')
            ts0_s, ts0_e = actor_rec['timespan'][0]['tsr0']
            qualifying_frames = 0
            for ts0 in range(ts0_s, ts0_e + 1):
                geom = geoms_by_actor_by_ts0.get(actor_id, {}).get(ts0)
                if geom is not None and geom_qualifier(geom):
                    qualifying_frames += 1
                    min_a_ts0 = min(ts0, min_a_ts0)
                    max_a_ts0 = max(ts0, max_a_ts0)

            # Don't output the actor if there are no qualifying geoms,
            # or if the number of qualifying geoms < minimum_frames
            if max_a_ts0 - min_a_ts0 < 0 or qualifying_frames < minimum_frames:
                continue
            else:
                # Adjust the actor timespan
                actor_rec['timespan'][0]['tsr0'] = [min_a_ts0, max_a_ts0]
                adjusted_actors.append(actor_rec)

                min_ts0 = min(min_a_ts0, min_ts0)
                max_ts0 = max(max_a_ts0, max_ts0)

        if max_ts0 - min_ts0 >= 0:
            # Adjust the activity timespan
            activity_rec['timespan'][0]['tsr0'] = [min_ts0, max_ts0]
            out_activities.append(activity_rec)

        return out_activities

    return _adjust_timespans_reducer


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
    yaml_activities, activity_records, non_activity_records =\
        parse_activities_yaml(args.input_activities)

    yaml_geoms, non_geom_records, geoms_by_actor =\
        parse_geom_yaml(args.input_geom)

    yaml_types, yaml_type_by_actor =\
        parse_type_yaml(args.input_types)

    geom_mapper_fns = []
    activity_mapper_fns = []

    # Pre-crop mapping
    if args.homography_file is not None:
        geom_mapper_fns.append(
            xd_map(_build_homography_mapper(args.homography_file)))

    if args.frame_offset is not None:
        geom_mapper_fns.append(
            xd_map(_build_time_shifter(args.frame_offset,
                                       args.framerate)))
        activity_mapper_fns.append(
            xd_map(_build_activity_time_shifter(args.frame_offset)))

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

    cropped_geoms_by_actor_by_ts0 = {}
    for actor, actor_geoms in geoms_by_actor.items():
        cropped_geoms_by_actor_by_ts0[actor] =\
            {g.get('ts0'): g for g in
             reduce(geom_pipeline(appender), actor_geoms, [])}

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

        for actor_id, geom_recs_by_ts0 in cropped_geoms_by_actor_by_ts0.items():
            geom_recs = geom_recs_by_ts0.values()
            if len(geom_recs) > 0:
                surviving_actors.add(actor_id)
                min_ts0, max_ts0 = float('inf'), 0.0
                for geom_rec in geom_recs:
                    min_ts0 = min(geom_rec.get('ts0', min_ts0), min_ts0)
                    max_ts0 = max(geom_rec.get('ts0', max_ts0), max_ts0)
                    # Write out the geom record
                    print(f"- {kpf_yaml_dump({'geom': geom_rec})}", file=of)

                num_frames_per_actor[actor_id] = max_ts0 - min_ts0

    # Dump kw18 of geoms
    kw18_base, _ = os.path.splitext(args.input_geom)
    kw18_outpath = os.path.join(args.output_dir, f"{kw18_base}.kw18")
    abort_if_file_exists(kw18_outpath)
    dump_geoms_as_kw18(itertools.chain(
        *[v.values() for v in cropped_geoms_by_actor_by_ts0.values()]),
                       num_frames_per_actor,
                       kw18_outpath)

    activity_pipeline = xd(*activity_mapper_fns)
    out_act_path = os.path.join(
        args.output_dir, os.path.basename(args.input_activities))
    abort_if_file_exists(out_act_path)
    with open(out_act_path, 'w') as of:
        out_meta_records = []
        activity_counts = {}
        activity_timespan_adjuster =\
            _build_activity_timespan_adjuster(cropped_geoms_by_actor_by_ts0)
        for rec in non_activity_records:
            meta_val = rec.get('meta')
            # Don't include original activity count meta records as we
            # have to recompute after the crop
            if(isinstance(meta_val, str) and
               re.search(r'\w+ \d+ instances', meta_val)):
                continue
            else:
                out_meta_records.append(rec)

        out_activity_records = reduce(
            activity_pipeline(activity_timespan_adjuster),
            activity_records,
            [])

        for activity in out_activity_records:
            # Count the instances for out meta counts
            for activity_name, count in activity.get('act2', {}).items():
                activity_counts[activity_name] =\
                    activity_counts.get(activity_name, 0) + count

        for out_meta_rec in out_meta_records:
            print(f"- {kpf_yaml_dump(out_meta_rec)}", file=of)

        for activity_name, count in activity_counts.items():
            meta_rec = {"meta": f"{activity_name} {int(count)} instances"}
            print(f"- {kpf_yaml_dump(meta_rec)}", file=of)

        for out_activity_rec in out_activity_records:
            print(f"- {kpf_yaml_dump({'act': out_activity_rec})}", file=of)

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
