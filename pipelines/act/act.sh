#!/bin/bash

# RUN ACT on multiple experiment files. For every experiment file, an output
# json file containing ACT predictions would be generated
#
# START_SCRIPT: Installation script for DIVA (setup_DIVA.sh)
#
# ACT_ROOT: ROOT Directory of ACT
#
# VIDEO_EXPERIMENT_ROOT: ROOT Directory where all experiment.yml files are stored
#
# JSON_ROOT: Root Directory where all output json files would be stored


START_SCRIPT=$1
ACT_ROOT=$2
VIDEO_EXPERIMENT_ROOT=$3
JSON_ROOT=$4

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Setup ACT
export PYTHONPATH=${ACT_ROOT}/act-detector-scripts:${ACT_ROOT}/virat-act-detector-scripts:${ACT_ROOT}/python:${PYTHONPATH}
source ${ACT_ROOT}/act-detector/bin/activate

# Setup DIVA
source ${START_SCRIPT}

for video_file in $VIDEO_EXPERIMENT_ROOT/*
do
  output_file="${JSON_ROOT}/sysfile_"$(basename $video_file .yml)".json"
  if [ ! -e "${output_file}" ]; then
    echo "${output_file} does not exist"
    pipeline_runner -p ${SCRIPT_DIR}/act.pipe --set exp:experiment_file_name=${video_file} \
                                            --set json_writer:json_path=${output_file} \
                  --set act_process:exp=${ACT_ROOT}/virat-act-detector-scripts/rgb_eval_1b.yml \
                  --set merge_tubes:exp=${ACT_ROOT}/virat-act-detector-scripts/rgb_eval_1b.yml \
                  --set json_writer:exp=${ACT_ROOT}/virat-act-detector-scripts/rgb_eval_1b.yml 
    sleep 1 
  else
    echo "${output_file} exists"
    sleep 1
  fi
done
