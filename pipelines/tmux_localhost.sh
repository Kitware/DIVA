#!/bin/bash

#+
# RC3D starter script.  Designed to test 1 json writer and 2 instances of rc3d
# running on different videos.
# Usage:
#
#   ./tmux_starter_script.sh  <environment_setup_script> <rc3d_home>
#
# environment_setup_script: A script (possibly setup_DIVA.sh) that
# sets the enviroment up properly so that pipeline_runner will be found in
# PATH and will execute properly
# 
# rc3d_home: home directory for rc3d experiments ($RC3D_ROOT/experiments/virat)
#
#-

SESSION="rc3d_zeromq"

START_SCRIPT=$1
RC3D_HOME=$2

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#cd ${SCRIPT_DIR}

echo "$(date) Creating session ${SESSION}"
tmux new-session -d -s $SESSION

sleep 1
echo "$(date) Starting First RC3D Instance..."
tmux select-window -t $SESSION:0
tmux rename-window -t $SESSION:0 'Sender0'
tmux send-keys -t 0 "export PYTHONPATH=${RC3D_HOME}" C-m
tmux send-keys -t 0 "source ${START_SCRIPT}" C-m
tmux send-keys -t 0 "pipeline_runner --pipe ${SCRIPT_DIR}/rc3d_sender.pipe --set exp:experiment_file_name=etc/rc3d_experiment.yml --set rc3d:experiment_file_name=${RC3D_HOME}/experiment.yml --set rc3d:model_cfg=${RC3D_HOME}/td_cnn_end2end.yml" C-m

sleep 1
tmux split-window -t $SESSION:0
tmux select-pane -t 1 
tmux split-window -h -t $SESSION:0

sleep 1
echo "$(date) Starting NIST JSON writer..."
tmux send-keys -t 1 "export PYTHONPATH=${RC3D_HOME}" C-m
tmux send-keys -t 1 "source ${START_SCRIPT}" C-m
tmux send-keys -t 1 "pipeline_runner --pipe ${SCRIPT_DIR}/json_writer_receiver.pipe --set json_writer:experiment_file_name=${RC3D_HOME}/experiment.yml --set json_writer:model_cfg=${RC3D_HOME}/td_cnn_end2end.yml" C-m


sleep 1
echo "$(date) Preparing Swimlane Visualizer..."
tmux send-keys -t 2 "export PYTHONPATH=${RC3D_HOME}" C-m
tmux send-keys -t 2 "source ${START_SCRIPT}" C-m
tmux send-keys -t 2 "pipeline_runner --pipe ${SCRIPT_DIR}/swimlane_receiver.pipe --set visualize:experiment_file_name=${RC3D_HOME}/experiment.yml" C-m

echo "$(date) Starter script done!"
