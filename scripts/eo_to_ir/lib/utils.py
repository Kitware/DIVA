import os

import yaml


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


def parse_type_yaml(path):
    yaml_types = load_yaml(path)
    record_by_actor = {}
    for item in yaml_types:
        if 'types' in item:
            actor_id = item.get('types', {}).get('id1')
            if actor_id is not None:
                record_by_actor[actor_id] = item

    return yaml_types, record_by_actor


def abort_if_file_exists(path):
    if os.path.isfile(path):
        print(f"File '{path}' already exists, aborting!")
        exit(1)


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


def dump_geoms_as_kw18(geoms, num_track_frames_lookup, outpath):
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


def area_of_bounds(bounds):
    x0, y0, x1, y1 = bounds

    return abs(x1 - x0) * abs(y1 - y0)
