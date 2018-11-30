from __future__ import absolute_import

import argparse
import os

from DIVA.processes.dispatcher.tasks import detect

# kwiver/sprokit imports
from sprokit.pipeline import process
from kwiver.kwiver_process import KwiverProcess

import threading

class Dispatcher(KwiverProcess):
    """
    Dispatches experiment file to pipeline tasks
    """
    def __init__(self, conf):
        KwiverProcess.__init__(self, conf)
        #TODO: Accept list of gpu
        self.add_config_trait( "num_gpu", "num_gpu", "1", \
                                "Number of gpu's dispatcher can use" )
        self.declare_config_using_trait("num_gpu")
        self.add_config_trait( "tasks_per_gpu", "tasks_per_gpu", "2", \
                                "Number of tasks scheduled on a gpu" )
        self.declare_config_using_trait("tasks_per_gpu")
        self.add_config_trait( "experiment_file_root", "experiment_file_root",
                                ".", "root directory for experiment files" )
        self.declare_config_using_trait("experiment_file_root")
        
        self.add_config_trait("darknet_root", "darknet_root", ".",
                                "root directory for darknet")
        self.declare_config_using_trait("darknet_root")
        self.add_config_trait("csv_root", "csv_root", ".",
                                "root directory for csv file")
        self.declare_config_using_trait("csv_root")
        self.lock = threading.Lock()

    def _configure(self):
        self.partial_signatures = []
        for experiment_file in os.listdir(self.config_value("experiment_file_root")):
            if experiment_file.endswith(".yml"):
                csv_file_name = os.path.splitext(experiment_file)[0] + ".csv"
                self.partial_signatures.append( detect.s(
                                os.path.join( self.config_value( "experiment_file_root" ), 
                                experiment_file ), 
                                self.config_value("darknet_root"), 
                                os.path.join( self.config_value("csv_root"), csv_file_name ) ) )
        self.signature_index = 0

        self.task_queue = {}
        for gpu_index in range(int(self.config_value("num_gpu"))):
            self.task_queue[gpu_index] = {}
            for task_index in range(int(self.config_value("tasks_per_gpu"))):
                self.task_queue[gpu_index][task_index] = None
    
    def _find_free_workers(self):
        free_workers = []
        for gpu_index, gpu_dict in self.task_queue.iteritems():
            for task_index, task in gpu_dict.iteritems():
                if ( task is None or task.ready() ):
                    free_workers.append( (gpu_index, task_index) )
        return free_workers

    def _step(self):
        # Only one thread dispathces
        self.lock.acquire()
        if self.signature_index < len(self.partial_signatures):
            # Dispatching data
            free_workers = self._find_free_workers()
            for free_worker in free_workers:
                gpu_index, task_index = free_worker
                if self.signature_index <  len( self.partial_signatures ) :
                    self.task_queue[gpu_index][task_index] = \
                            self.partial_signatures[self.signature_index].delay( gpu=gpu_index )
                    self.signature_index += 1
                else:
                    break
        else:
            # Waiting for things to complete
            free_workers = self._find_free_workers()
            if len(free_workers) == int( self.config_value("num_gpu") ) * \
                        int( self.config_value("tasks_per_gpu") ):
                self.mark_process_as_complete()
        self.lock.release()


def __sprokit_register__():
    from sprokit.pipeline import process_factory

    module_name = 'python:kwiver.dispatcher'

    if process_factory.is_process_module_loaded(module_name):
        return

    process_factory.add_process('Dispatcher', 
                            'Dispatch experiment file across multiple instances of algorithm', 
                            Dispatcher)

    process_factory.mark_process_module_as_loaded(module_name)


    


