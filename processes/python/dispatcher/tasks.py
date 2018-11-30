from __future__ import absolute_import, unicode_literals

from DIVA.processes.dispatcher.celery_config import app

import argparse
import os

from sprokit.pipeline import pipeline
from sprokit.pipeline import process_factory
from sprokit.pipeline import modules
from sprokit.pipeline import config
from sprokit.pipeline import scheduler_factory


def create_diva_experiment_config( experiment_root ):
    exp_config = config.empty_config()
    exp_config.set_value( "experiment_file_name", experiment_root )
    return exp_config

def create_darknet_config( darknet_root, gpu ):
    darknet_config = config.empty_config()  
    darknet_config.set_value( "detector:type", "darknet")
    darknet_config.set_value( "detector:darknet:net_config", os.path.join( darknet_root, 
                                        "models", "virat_auto.inference.cfg" ) ) 
    darknet_config.set_value( "detector:darknet:weight_file", os.path.join( darknet_root, 
                                        "models", "virat_auto_final.weights" ) ) 
    darknet_config.set_value( "detector:darknet:class_names", os.path.join( darknet_root, 
                                        "models", "virat.names" ) )
    darknet_config.set_value( "detector:darknet:thresh", "0.50" )
    darknet_config.set_value( "detector:darknet:hier_thresh", "0.50" )
    darknet_config.set_value( "detector:darknet:gpu_index", str( gpu ) )
    darknet_config.set_value( "detector:darknet:resize_ni", "1024" )
    darknet_config.set_value( "detector:darknet:resize_nj", "1024" )
    return darknet_config

@app.task( name='dispatcher.task.darknet.detect' )
def detect( exp_file, darknet_root, csv_path, gpu ):
    # Load all modules
    modules.load_known_modules()
    
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
    darknet_pipeline.setup_pipeline()
    if darknet_pipeline.setup_successful():
        # Create scheduler and run the pipeline
        scheduler = scheduler_factory.create_scheduler( "pythread_per_process",
                                                        darknet_pipeline )
        scheduler.start()
        scheduler.wait()
        return True
    else:
        raise Exception("Failed to create pipeline")
        return False
    

