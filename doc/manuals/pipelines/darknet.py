exp_config = create_diva_experiment_config( exp_file )
exp_process = process_factory.create_process( "diva_experiment", "exp", exp_config ) 

# Create Image Object Detector Process
darknet_config = create_darknet_config( darknet_root, gpu ) 
yolo_process = process_factory.create_process( "image_object_detector", "yolo_v2", \
                                                                    darknet_config )

# Create Detected object set output
detected_output_config = config.empty_config()
detected_output_config.set_value( "writer:type", "csv" )
detected_output_config.set_value( "file_name", csv_path )
detected_output_process = process_factory.create_process( "detected_object_output", "sink",
                                                            detected_output_config )
# Create pipeline out of these
darknet_pipeline = pipeline.Pipeline()
darknet_pipeline.add_process( exp_process )
darknet_pipeline.add_process( yolo_process )
darknet_pipeline.add_process( detected_output_process )

# Create connections
darknet_pipeline.connect( "exp", "image", \
                             "yolo_v2", "image" )
darknet_pipeline.connect( "yolo_v2", "detected_object_set", \
                                  "sink", "detected_object_set" )

