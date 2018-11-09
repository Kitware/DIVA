#!/bin/bash

VIDEO_EXPERIMENT_ROOT=$1
JSON_ROOT=$2

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for video_file in $VIDEO_EXPERIMENT_ROOT/*
do
  output_file="${JSON_ROOT}/sysfile_"$(basename $video_file .yml)".json"
  pipeline_runner -p ${SCRIPT_DIR}/rc3d.pipe --set exp:experiment_file_name=${video_file} \
                                             --set json_writer:json_path=${output_file}
  echo $output_file 
done
