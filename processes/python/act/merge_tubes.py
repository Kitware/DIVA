# -*- coding: utf-8 -*-
"""
Kwiver process based on evaluating act

@author Ameya Shringi
"""

# Kwiver/Sprokit imports
from sprokit.pipeline import process
from kwiver.kwiver_process import KwiverProcess
from vital.types import ObjectTrackSet

# ACT Imports
from exp_config import experiment_config, expcfg_from_file
from ACT_utils import nms_tubelets
from virat_dataset import ViratDataset

import numpy as np


class MergeTubes(KwiverProcess):
    """
    Merge tubelets produced by ACT to create larger tubes.
    """
    def _nms_tracks(self, tracks, label_id, iou_thresh, top_k):
        label_tracks = []
        label_tracks_id = []
        for track_id, track in enumerate(tracks):
            if len(track) == 0:
                continue
            else:
                track_state  = track[track.first_frame]
                if int(track_state.detection.type().get_most_likely_class()) == label_id:
                    label_tracks.append(track)
                    label_tracks_id.append(track_id)
        dets = np.zeros((len(label_tracks), 4*experiment_config.data.num_frames+1))
        for track_id, track in enumerate(label_tracks):
            first_track_state = track[track.first_frame]
            first_frame_id = first_track_state.frame_id
            for track_state in track:
                frame_id = track_state.frame_id - first_frame_id
                dets[track_id, 4*frame_id] = track_state.detection.\
                                                    bounding_box().min_x()
                dets[track_id, 4*frame_id+1] = track_state.detection.\
                                                    bounding_box().min_y()
                dets[track_id, 4*frame_id+2] = track_state.detection.\
                                                    bounding_box().max_x()
                dets[track_id, 4*frame_id+3] = track_state.detection.\
                                                    bounding_box().max_y()
                dets[track_id, dets.shape[1]-1] = track_state.detection.confidence()
        nms_ids = nms_tubelets(dets, iou_thresh, top_k)
        nms_track_ids = [label_tracks_id[nms_id] for nms_id in nms_ids]
        return nms_track_ids


    def _iou2d(self, track, successive_track):
        """
        Compute iou2d between the last frame of a track and first frame of the
        next track
        """
        last_track_state = track[track.last_frame]
        first_track_state = successive_track[successive_track.first_frame]
        if first_track_state is not None and last_track_state is not None:
            first_detection = first_track_state.detection
            last_detection = last_track_state.detection
            if first_detection.type().get_most_likely_class() == \
                    last_detection.type().get_most_likely_class():
                first_bbox = first_detection.bounding_box()
                last_bbox = last_detection.bounding_box()
                xmin = max(first_bbox.min_x(), last_bbox.min_x())
                ymin = max(first_bbox.min_y(), last_bbox.min_y())
                xmax = min(first_bbox.max_x(), last_bbox.max_x())
                ymax = max(first_bbox.max_y(), last_bbox.max_y())
                if xmin > xmax or ymin > ymax:
                    return 0.0
                else:
                    intersection = (ymax-ymin)*(xmax-xmin)
                    union = first_bbox.area() + last_bbox.area() - intersection
                    return float(intersection)/union
            else:
                return 0.0
        else:
            return 0.0

    def _merge_tracks(self, track, other_track):
        # Simplest merge TODO: verify the merge
        all_frames = track.all_frame_ids()
        for track_state in other_track:
            if track_state.frame_id not in all_frames:
                track.append(track_state)
        return track

    def __init__(self, conf):
        KwiverProcess.__init__(self, conf)
        self.add_config_trait("exp", "exp",
                            '.', 'experiment configuration for ACT')
        self.declare_config_using_trait('exp')
        expcfg_from_file(self.config_value("exp"))
        required = process.PortFlags()
        required.add(self.flag_required)
        #  declare our ports ( port-name, flags)
        self.declare_input_port_using_trait('object_track_set', required )
        self.declare_input_port_using_trait('timestamp', required)
        self.declare_output_port_using_trait('object_track_set', process.PortFlags() )


    def _configure(self):
        self.finished_tracks = []
        self.current_tracks = [] 
        self.virat_dataset = ViratDataset(experiment_config.data.data_root,
                                        experiment_config.data.frames_root,
                                        experiment_config.data.flow_root,
                                        experiment_config.data.train_annotation_dirs,
                                        experiment_config.data.test_annotation_dirs,
                                        experiment_config.data.class_index,
                                        experiment_config.data.save_directory,
                                        experiment_config.train.kpf_mode,
                                        experiment_config.train.json_mode,
                                        experiment_config.data.save_prefix)
        self.video_index = 0

    def _step(self):
        object_track_set = self.grab_input_using_trait("object_track_set")
        timestamp = self.grab_input_using_trait("timestamp")

        # End of video processing
        if timestamp.get_frame() == self.virat_dataset.test_num_frames(
                                            self.virat_dataset.test_video_list[
                                                self.video_index]):
            self.video_index += 1
            self.finished_tracks = self.current_tracks
            self.current_tracks = []

        if len(object_track_set) > 0:
            # Non maximum supression for tracks
            pruned_tracks =  []
            nms_ids = []
            for label_id in range(self.virat_dataset.nlabels):
                # skip background (might be redundant)
                if label_id == 0:
                    continue
                nms_ids.extend(self._nms_tracks(object_track_set.tracks(), label_id, \
                                                0.3, top_k=10))

            #TODO: Switch to track id rather than track index 
            new_tracks = []
            for nms_id in nms_ids:
                pruned_tracks.append(object_track_set.tracks()[nms_id])

            # Create new tubes for first frame
            if len(self.current_tracks) == 0:
                self.current_tracks = pruned_tracks
                self.push_to_port_using_trait("object_track_set", 
                        ObjectTrackSet(self.finished_tracks))
            else:
                merged_ids = []
                for track_id, track in enumerate(self.current_tracks):
                    is_continued = False
                    for nms_track_id, nms_track in enumerate(pruned_tracks):
                        # Check iou and don't merge tracks more than once
                        if self._iou2d(track, nms_track) > 0.2 and \
                                nms_track_id not in merged_ids:
                            # Merge tubes
                            is_continued = True
                            merged_ids.append(nms_track_id)
                            track = self._merge_tracks(track, nms_track)
                            break

                    if not is_continued:
                        self.finished_tracks.append(track)
                    else:
                        new_tracks.append(track)

                for track_id, nms_track in enumerate(pruned_tracks):
                    if track_id not in merged_ids:
                        new_tracks.append(nms_track)
                self.current_tracks = new_tracks
                self.push_to_port_using_trait("object_track_set", 
                                            ObjectTrackSet(self.finished_tracks))
                self.finished_tracks = []
        else:   
            self.push_to_port_using_trait("object_track_set", ObjectTrackSet())

# ==================================================================
def __sprokit_register__():
    from sprokit.pipeline import process_factory

    module_name = 'python:kwiver.MergeTubes'

    if process_factory.is_process_module_loaded(module_name):
        return

    process_factory.add_process('MergeTubes', 'Merge Tubelets from earlier iteration', MergeTubes)

    process_factory.mark_process_module_as_loaded(module_name)
