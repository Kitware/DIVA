# -*- coding: utf-8 -*-
"""
Kwiver process based on evaluating act

@author Ameya Shringi
"""

# Kwiver/Sprokit imports
from sprokit.pipeline import process
from kwiver.kwiver_process import KwiverProcess

# ACT Imports
from exp_config import experiment_config, expcfg_from_file
from act_utils import nms_tubelets

class ACTProcess(KwiverProcess):
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
                track_state  = track[0]
                if track_state.detection().type() == label_id:
                    label_tracks.append(track)
                    label_track_id.append(track_id)
        dets = np.zeros((len(label_tracks), 4*experiemnt_config.data.num_frames+1))
        for track_id, track in enumerate(label_tracks):
            first_track_state = self._find_first_track_state(track)
            last_track_state = self._find_last_track_state(track)
            first_frame_id = first_track_state.frame_id()
            last_frame_id = last_track_state.frame_id()
            if last_frame_id - first_frame_id != experiment_config.data.num_frames:
                import pdb
                pdb.set_trace()
            for track_state in track:
                frame_id = track_state.frame_id() - first_frame_id
                dets[track_id, 4*frame_id] = track_state.detection.\
                                                    bounding_box.get_xmin()
                dets[track_id, 4*frame_id+1] = track_state.detection.\
                                                    bounding_box.get_ymin()
                dets[track_id, 4*frame_id+2] = track_state.detection.\
                                                    bounding_box.get_xmax()
                dets[track_id, 4*frame_id+3] = track_state.detection.\
                                                    bounding_box.get_ymax()
                dets[track_id, dets.shape[1]-1] = track_state.detection.confidence()
        nms_ids = nms_tubelets(dets, iou_thresh, top_k)
        nms_track_ids = [label_track_id[nms_id] for nms_id in nms_ids]
        return nms_track_ids

    def _find_last_track_state(self, track):
        if len(track) == 0:
            return None
        else:
            last_track_state = track[0]
            for track_state in track:
                if track_state.frame_id > last_track_state.frame_id:
                    last_track_state = track_state
            return last_track_state
    
    def _find_first_track_state(self, track):
        if len(track) == 0:
            return None
        else:
            first_track_state = track[0]
            for track_state in track:
                if track_state.frame_id < first_track_state.frame_id:
                    first_track_state = track_state
            return first_track_state

    def _iou2d(self, track, successive_track):
        """
        Compute iou2d between the last frame of a track and first frame of the
        next track
        """
        last_track_state = self._find_last_track_state(track)
        first_track_state = self._find_first_track_state(succesive_track)
        if first_track_state is not None and last_track_state is not None:
            first_detection = first_track_state.detection()
            last_detection = last_track_state.detection()
            if first_detection.type() == last_detection.type():
                first_bbox = first_detection.bounding_box()
                last_bbox = last_detection.bouding_box()
                xmin = max(first_bbox.xmin(), last_bbox.xmin())
                ymin = max(first_bbox.ymin(), last_bbox.ymin())
                xmax = min(first_bbox.xmax(), last_bbox.xmax())
                ymax = max(first_bbox.ymax(), last_bbox.ymax())
                if xmin > xmax or ymin > ymax:
                    return 0.0
                else:
                    intersection = (ymax-ymin)*(xmax-xmin)
                    union = first_bbox.area() + second_bbox.area() - intersection
                    return float(intersection)/union
            else:
                return 0.0
        else:
            return 0.0

    def _merge_tracks(self, track, other_track):
        # Simplest merge TODO: verify the merge
        for track_state in other_track:
            track.append(track_state)
        return track

    def __init__(self, conf):
        KwiverProcess.__init__(self, conf)
        self.add_config_trait("exp", "exp",
                            '.', 'experiment configuration for ACT')
        self.declare_config_using_trait('exp')
        expcfg_from_file(self.config_valud("exp"))
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

    def _step(self):
        object_track_set = self.grab_input_using_trait("object_track_set")
        timestamp = self.grab_input_using_trait("timestamp")
        if len(object_track_set) > 0:
            # Non maximum supression for tracks
            pruned_tracks =  []
            for label_id in self.virat_dataset.n_labels:
                # skip background (might be redundant)
                if label_id == 0:
                    continue
                nms_ids.append(self._nms_tracks(object_track_set.tracks(), label_id, 0
                                            .3, top_k=10))
            new_tracks = []
            for nms_id in nms_ids:
                pruned_tracks.append(object_track_set.get_track(nms_id))
            
            # Create new tubes for first frame
            if timestamp.get_frame() == 1:
                self.current_tubes = pruned_tracks
                self.push_to_port_using_trait("object_track_set", ObjectTrackSet())
            else:
                merged_ids = []
                for track_id, track in enumerate(self.current_tubes):
                    is_continued = False
                    for nms_track_id, nms_track in enumerate(pruned_tracks):
                        # Check iou and don't merge tracks more than once
                        if self._iou2d(track, nms_track) > 0.2 and \
                                nms_track_id not in merged_ids:
                            # Merge tubes                               
                            is_continued = True
                            merged_ids.append(nms_track_id)
                            track = self._merge_track(track, nms_track)
                            break

                    if not is_continued:
                        self.finished_tubes.append(track)
                    else:
                        new_tracks.append(track)

                    for track_id, nms_track in pruned_tracks:
                        if track_id not in merged_ids:
                            new_tracks.append(nms_track)
                            
                self.current_tubes = new_tracks
                self.push_to_port_using_trait("object_track_set", 
                                            ObjectTrackSet(self.finished_tubes))
                self.finished_tubes = []
        else:   
            self.push_to_port_using_trait("object_track_set", ObjectTrackSet())

# ==================================================================
def __sprokit_register__():
    from sprokit.pipeline import process_factory

    module_name = 'python:kwiver.MergeTubesProcess'

    if process_factory.is_process_module_loaded(module_name):
        return

    process_factory.add_process('MergeTubesProcess', 'Merge Tubelets from earlier iteration', ACTProcess)

    process_factory.mark_process_module_as_loaded(module_name)
