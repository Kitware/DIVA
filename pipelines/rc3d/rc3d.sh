#!/bin/bash

# RUN RC3D on multiple experiment files. For every experiment file, an output
# json file containing RC3D predictions would be generated
#
# START_SCRIPT: Installation script for DIVA (setup_DIVA.sh)
#
# RC3D_ROOT: ROOT Directory of RC3D
#
# VIDEO_EXPERIMENT_ROOT: ROOT Directory where all experiment.yml files are stored
#
# JSON_ROOT: Root Directory where all output json files would be stored


START_SCRIPT=$1
RC3D_ROOT=$2
VIDEO_EXPERIMENT_ROOT=$3
JSON_ROOT=$4

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH=${RC3D_ROOT}/experiments/virat
source ${START_SCRIPT}

echo ${PYTHONPATH}
for video_file in $VIDEO_EXPERIMENT_ROOT/*
do
  output_file="${JSON_ROOT}/sysfile_"$(basename $video_file .yml)".json"
  pipeline_runner -p ${SCRIPT_DIR}/rc3d.pipe --set exp:experiment_file_name=${video_file} \
                                                  --set json_writer:json_path=${output_file}
  sleep 5
  #  echo $output_file 
done
