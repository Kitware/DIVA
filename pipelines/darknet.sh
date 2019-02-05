#!/bin/bash

# RUN ACT on multiple experiment files. For every experiment file, an output
# json file containing ACT predictions would be generated
#
# START_SCRIPT: Installation script for DIVA (setup_DIVA.sh)
#
# DARKNET_ROOT: ROOT Directory of YOLO
#
# VIDEO_EXPERIMENT_ROOT: ROOT Directory where all experiment.yml files are stored
#
# CSV_ROOT: Root Directory where all csv files would be stored
#
# GPU_INDEX: GPU Index on which darknet runs

START_SCRIPT=$1
DARKNET_ROOT=$2
VIDEO_EXPERIMENT_ROOT=$3
CSV_ROOT=$4
GPU_INDEX=$5

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Setup DIVA
source ${START_SCRIPT}

for video_file in $VIDEO_EXPERIMENT_ROOT/*
do
  output_file="${CSV_ROOT}/"$(basename $video_file .yml)".csv"
  if [ ! -e "${output_file}" ]; then
    echo "${output_file} does not exist"
    pipeline_runner -p ${SCRIPT_DIR}/darknet.pipe \
      --set exp:experiment_file_name=${video_file} \
      --set yolo_v2:detector:darknet:net_config=${DARKNET_ROOT}/models/virat_auto.inference.cfg \
      --set yolo_v2:detector:darknet:weight_file=${DARKNET_ROOT}/models/virat_auto_final.weights \
      --set yolo_v2:detector:darknet:class_names=${DARKNET_ROOT}/models/virat.names \
      --set yolo_v2:detector:darknet:gpu_index=${GPU_INDEX} \
      --set sink:file_name=${output_file} 
    sleep 1 
  else
    echo "${output_file} exists"
    sleep 1
  fi
done
