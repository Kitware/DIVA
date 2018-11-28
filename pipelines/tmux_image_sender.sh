#!/bin/bash

#+
# Run image sender inside tmux 
# 
# Usage:
#
#   ./tmux_image_sender.sh  <environment_setup_script> <experiment_file>
#
# environment_setup_script: A script (possibly setup_DIVA.sh) that
# sets the enviroment up properly so that pipeline_runner will be found in
# PATH and will execute properly
#
# experiment_file: path to a diva_experiment file (check etc/video_experiment.yml for example)
#-

SESSION="image_sender"

START_SCRIPT=$1
EXPERIMENT_FILE=$2

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#cd ${SCRIPT_DIR}

echo "$(date) Creating session ${SESSION}"
tmux new-session -d -s $SESSION

sleep 1
echo "$(date) Starting Image Sender Instance..."
tmux select-window -t $SESSION:0
tmux rename-window -t $SESSION:0 'Sender0'
tmux send-keys -t $SESSION:0 "source ${START_SCRIPT}" C-m
tmux send-keys -t $SESSION:0 "pipeline_runner --pipe ${SCRIPT_DIR}/image_sender.pipe --set exp:experiment_file_name=${EXPERIMENT_FILE}" C-m

echo "$(date) Starter script done!"
