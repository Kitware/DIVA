#!/bin/bash

# RUN optical flow on the dataset. 
#
# START_SCRIPT: Installation script for DIVA (setup_DIVA.sh)
#
# VIDEO_EXPERIMENT_ROOT: ROOT Directory where all experiment.yml files are stored
#
# OUTPUT_ROOT: Root Directory where all images would be stored

START_SCRIPT=$1
VIDEO_EXPERIMENT_ROOT=$2
OUTPUT_ROOT=$3

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Setup DIVA
source ${START_SCRIPT}

for video_file in $VIDEO_EXPERIMENT_ROOT/*
do
  video_prefix="$(basename $video_file .yml)"
  year=${video_prefix:0:10}
  date=${video_prefix:11:2}
  image_path=${OUTPUT_ROOT}/${year}/${date}/${video_prefix}
  mkdir -p -v ${image_path}
  pipeline_runner -p ${SCRIPT_DIR}/optical_flow.pipe \
    --set exp:experiment_file_name=${video_file} \
    --set writer:file_name_template=${image_path}/%05d.png
  sleep 1
done
