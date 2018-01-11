import diva_python_utils

meta = diva_python_utils.meta() # We will reuse this

# Example of Detection/Track Logic creating a geometry file
print 'Geometry Content'
meta.set_msg("Example geometry");
print meta.to_string(),
meta.set_msg("1 tracks; 50 detection");
print meta.to_string(),
meta.set_msg("min / max frame: 0 942 min / max timestamp: 0 471 ");
print meta.to_string(),
meta.set_msg("min / max geometry: 0,289 - 1278 719 ( 1279x431+0+289 )");
print meta.to_string(),

time_s = 0.0
geom = diva_python_utils.geometry()
for x in range(0,50):
  geom.clear()
  geom.set_track_id(66);
  geom.set_detection_id(0);
  geom.set_frame_id(x);
  geom.set_frame_time(time_s);
  geom.set_evaluation(diva_python_utils.geometry_evaluation.true_positive);
  geom.set_occlusion(diva_python_utils.geometry_occlusion.heavy);
  geom.set_source(diva_python_utils.geometry_source.truth);
  geom.set_bounding_box_pixels(104, 349, 210, 385);
  geom.add_polygon_point( (100,399) )
  geom.add_polygon_point( (200,398) )
  geom.add_polygon_point( (300,397) )
  print geom.to_string(),
  time_s += 0.1

print 'Label Content'
# Example of writing a label/classification file

meta.set_msg("Example type labels");
print meta.to_string(),
meta.set_msg("Dumpsters 1");
print meta.to_string(),
meta.set_msg("Vehicle 1 ");
print meta.to_string(),

label = diva_python_utils.label()
label.set_track_id(66),
label.set_type('Dumpster')
print label.to_string(),
label.set_track_id(67),
label.set_type('Vehicle')
print label.to_string(),

# Example of writing an activity file
print 'Activity Content'

meta.set_msg('Example activity');
print meta.to_string(),
meta.set_msg('vehicle_moving 2 instances');
print meta.to_string(),
meta.set_msg('activity_gesturing 0 instances');
print meta.to_string(),

actv = diva_python_utils.activity()
actv.set_activity_name("vehicle_moving");
actv.set_activity_id(1);
actv.set_source(diva_python_utils.activity_source.truth);
# Overall timeframe of the activity
actv.add_frame_id_span((2135, 2456));
actv.add_frame_id_span((2479, 2503));
# Specific actors in this activity, and their associated frames
actv.add_actor_frame_id_span(55,(2135, 2344));
actv.add_actor_frame_id_span(55,(2479, 2496));
actv.add_actor_frame_id_span(44,(2267, 2456));
actv.add_actor_frame_id_span(44,(2488, 2503));
print actv.to_string(),

