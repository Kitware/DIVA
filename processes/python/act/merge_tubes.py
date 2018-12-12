# -*- coding: utf-8 -*-
"""
Kwiver process to merge intermediate tubelets produces by ACT into tubes 

@author Ameya Shringi
"""

# Kwiver/Sprokit imports
from sprokit.pipeline import process
from kwiver.kwiver_process import KwiverProcess
from vital.types import ObjectTrackSet
from sprokit.pipeline import datum
# ACT Imports
from exp_config import experiment_config, expcfg_from_file
from ACT_utils import nms_tubelets

import numpy as np


class MergeTubes(KwiverProcess):
    """
    Merge tubelets produced by ACT to create larger tubes.

    * Input Ports:
        * ``object_track_set`` Intermediate detections from ACT forward pass (Required)
        * ``file_name`` Input source (Required)
        * ``timestamp`` Timestamp assocaited with the input from which intermediated tracks were computed (Required)
      
    * Output Ports:
        * ``object_track_set`` Finished tubes
        * ``current_object_track_set`` Incomplete tubes

    * Configuration
        * ``exp`` Experiment configuration for ACT (Eg. `exp.yml`_)
        * ``num_classes`` Number of classes that ACT was trained on (default=20)
    
    .. Repo Links

    .. _exp.yml: https://gitlab.kitware.com/kwiver/act_detector/blob/act-detector/virat-act-detector-scripts/rgb_actev.yml
    """
    def __init__(self, conf):
        """
        Constructor for MergeTubes
        :param conf: configuration for the process
        :return None
        """
        KwiverProcess.__init__(self, conf)
        self.add_config_trait("exp", "exp",
                            '.', 'experiment configuration for ACT')
        self.declare_config_using_trait('exp')
        self.add_config_trait("num_classes", "num_classes",
                            '20', 'Total number of classes ACT was trained on')
        self.declare_config_using_trait('num_classes')

        required = process.PortFlags()
        required.add(self.flag_required)
    
        optional = process.PortFlags()

        self.add_port_trait("current_object_track_set", "object_track_set", 
                            "Set of incomplete action tubes")
        #  declare our ports ( port-name, flags)
        self.declare_input_port_using_trait('object_track_set', required )
        self.declare_input_port_using_trait('file_name', required )
        self.declare_input_port_using_trait('timestamp', required)
        self.declare_output_port_using_trait('object_track_set', 
                                            required )
        self.declare_output_port_using_trait('current_object_track_set', 
                                            optional )
        self.video_name = None

    def _configure(self):
        """
        Configure the process
        """
        self.finished_tracks = []
        self.current_tracks = [] 
        # Global configuration
        expcfg_from_file(self.config_value("exp"))

    def _nms_tracks(self, tracks, label_id, iou_thresh, top_k):
        """
        Non maximum suppression for the tracks of a class
        :param tracks: Set of all intermediate tracks produces by ACT
        :param label_id: class index for which nms is being performed
        :param iou_thresh: lower bound of iou used to suppress tracks
        :param top_k: uppperbound on number of tracks obtained after suppression
        :return list of track ids representing the top k tracks
        """
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
        :param track: Current track
        :param successive_track: Track that follows current track
        :return IOU between current and successive track
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
                    try:
                        iou =  float(intersection)/union
                        return iou
                    except ZeroDivisionError:
                        return 0.0
            else:
                return 0.0
        else:
            return 0.0

    def _merge_tracks(self, track, other_track):
        """
        Helper function to merge two tracks
        :param track: First track
        :param other_track: Second track
        :return track obtained from merding two tracks
        """
        # Simplest merge TODO: verify the merge
        all_frames = track.all_frame_ids()
        for track_state in other_track:
            if track_state.frame_id not in all_frames:
                track.append(track_state)
        return track

    def _step(self):
        """
        Step function for the process
        """
        object_track_set = self.grab_input_using_trait("object_track_set")
        timestamp = self.grab_input_using_trait("timestamp")
        file_name = self.grab_input_using_trait("file_name")

        if len(object_track_set) > 0:
            # Non maximum supression for tracks
            pruned_tracks =  []
            nms_ids = []
            for label_id in range(int(self.config_value("num_classes"))):
                # skip background (might be redundant)
                if label_id == 0:
                    continue
                nms_ids.extend(self._nms_tracks(object_track_set.tracks(), label_id, \
                                                0.3, top_k=2))

            #TODO: Switch to track id rather than track index 
            new_tracks = []
            for nms_id in nms_ids:
                pruned_tracks.append(object_track_set.tracks()[nms_id])
            # Create new tubes for first frame
            if len(self.current_tracks) == 0:
                self.current_tracks = pruned_tracks
                self.push_to_port_using_trait("object_track_set", 
                        ObjectTrackSet(self.finished_tracks))
                self.push_to_port_using_trait("current_object_track_set", 
                                            ObjectTrackSet(self.current_tracks))
            else:
                merged_ids = []
                for track_id, track in enumerate(self.current_tracks):
                    is_continued = False
                    for nms_track_id, nms_track in enumerate(pruned_tracks):
                        # Check iou and don't merge tracks more than once
                        if self._iou2d(track, nms_track) > 0.5 and \
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
                self.push_to_port_using_trait("current_object_track_set", 
                                            ObjectTrackSet(self.current_tracks))
                self.finished_tracks = []
        else:   
            self.push_to_port_using_trait("object_track_set", 
                                            ObjectTrackSet(self.finished_tracks))
            self.push_to_port_using_trait("current_object_track_set", ObjectTrackSet())
        print ("merge_tube: Done with " + str(timestamp.get_frame()) + " frame")

# ==================================================================
def __sprokit_register__():
    """
    Sprokit registraction for the process
    """
    from sprokit.pipeline import process_factory

    module_name = 'python:kwiver.MergeTubes'

    if process_factory.is_process_module_loaded(module_name):
        return

    process_factory.add_process('MergeTubes', 'Merge Tubelets from earlier iteration', MergeTubes)

    process_factory.mark_process_module_as_loaded(module_name)
