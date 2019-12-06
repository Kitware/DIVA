import diva_python_utils

meta = diva_python_utils.meta() # We will reuse this

# Example of Detection/Track Logic creating a geometry file
print('Geometry Content')
meta.set_msg("Example geometry")
print(meta.to_string())
meta.set_msg("1 tracks; 50 detection")
print(meta.to_string())
meta.set_msg("min / max frame: 0 942 min / max timestamp: 0 471 ")
print(meta.to_string())
meta.set_msg("min / max geometry: 0,289 - 1278 719 ( 1279x431+0+289 )")
print(meta.to_string())

time_s = 0.0
geom = diva_python_utils.geometry()
for x in range(0,50):
  geom.clear()
  geom.set_track_id(66)
  geom.set_detection_id(0)
  geom.set_frame_id(x)
  geom.set_frame_time(time_s)
  geom.set_evaluation(diva_python_utils.geometry_evaluation.true_positive)
  geom.set_occlusion(diva_python_utils.geometry_occlusion.mostly)
  geom.set_source(diva_python_utils.geometry_source.truth)
  geom.set_bounding_box_pixels(104, 349, 210, 385)
  geom.add_polygon_point( (100,399) )
  geom.add_polygon_point( (200,398) )
  geom.add_polygon_point( (300,397) )
  print(geom.to_string())
  time_s += 0.1

print('Label Content')
# Example of writing a label/classification file

meta.set_msg("Example type labels")
print(meta.to_string())
meta.set_msg("Dumpsters 1")
print(meta.to_string())
meta.set_msg("Vehicle 1 ")
print(meta.to_string())

label = diva_python_utils.label()
label.set_track_id(66),
label.add_classification('Dumpster',1.0)
print(label.to_string())
label.clear()
label.set_track_id(67),
label.add_classification('Vehicle',1.0)
print(label.to_string())

# Example of writing an activity file
print('Activity Content')

meta.set_msg('Example activity')
print(meta.to_string())
meta.set_msg('vehicle_moving 2 instances')
print(meta.to_string())
meta.set_msg('activity_gesturing 0 instances')
print(meta.to_string())

actv = diva_python_utils.activity()
#actv.set_activity_name("vehicle_moving");
actv.set_activity_id(1)
actv.set_source(diva_python_utils.activity_source.truth)
# Overall timeframe of the activity
actv.add_frame_id_span((2135, 2456))
actv.add_frame_id_span((2479, 2503))
# Specific actors in this activity, and their associated frames
actv.add_actor_frame_id_span(55,(2135, 2344))
actv.add_actor_frame_id_span(55,(2479, 2496))
actv.add_actor_frame_id_span(44,(2267, 2456))
actv.add_actor_frame_id_span(44,(2488, 2503))
print(actv.to_string())

# Example of writing an experiment file
print('Experiment Content')
exp = diva_python_utils.experiment()
# This is a sample experiment file for the DIVA system.
# This file can be used for
#    1) Running and experiment
#    2) Scoring the results of the experiment

# What is the purpose of this experiment?
exp.set_type(diva_python_utils.experiment_type.object_detection)
input = exp.get_input()

# Describe the inputs :
# the dataset ID is used as the prefix for output files
input.set_dataset_id('VIRAT_S_000206_04_000710_000779')
# frame_rate_Hz metadata; available via the API if you want it
input.set_frame_rate_Hz(30)
# the instance of the input source, in this case, a file referencing image files,
# located in ${root_dir}/${source}, with filepaths of images to be processed.
input.set_image_list_source('./etc/','image_list.txt')

# Describe the outputs :
# How will your algorithm's output be transported?
exp.set_output_type(diva_python_utils.experiment_output_type.file)
# Where will the output be written?
exp.set_output_root_dir('./etc/algo-out')

# Scoring Configuration
# Where is the scoring executable
exp.set_score_events_executable('./bin/score_events')
# What file do we score against
exp.set_scoring_reference_geometry('./etc/ref-geom/VIRAT_S_000206_04_000710_000779.reduced.geom.yml')
# Where does the scoring evaluation go?
exp.set_scoring_evaluation_output_dir('./etc/eval-out')
# For scoring object detections :
# The reference labels file
exp.set_scoring_object_detection_reference_types('./etc/ref-geom/VIRAT_S_000206_04_000710_000779.types.yml')
# The target label to score
exp.set_scoring_object_detection_target('Person')
# Set the IOU
exp.set_scoring_object_detection_iou('0.5')
# Set the time window
exp.set_scoring_object_detection_time_window('25:75')

print(exp.to_string())
