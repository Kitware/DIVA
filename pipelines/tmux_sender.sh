#!/bin/bash

#+
# RC3D starter script. 
# 
# Usage:
#
#   ./tmux_starter_script.sh  <environment_setup_script> <rc3d_home>
#
# environment_setup_script: A script (possibly setup_DIVA.sh) that
# sets the enviroment up properly so that pipeline_runner will be found in
# PATH and will execute properly
#
# rc3d_home: path to the experiment directory of RC3D ($RC3D_ROOT/experiments/virat)
#-

SESSION="rc3d_zeromq_sender"

START_SCRIPT=$1
RC3D_HOME=$2

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#cd ${SCRIPT_DIR}

echo "$(date) Creating session ${SESSION}"
tmux new-session -d -s $SESSION

sleep 1
echo "$(date) Starting RC3D Instance..."
tmux select-window -t $SESSION:0
tmux rename-window -t $SESSION:0 'Sender0'
tmux send-keys -t $SESSION:0 "source ${START_SCRIPT}" C-m
tmux send-keys -t $SESSION:0 "export PYTHONPATH=${PYTHONPATH}:${RC3D_HOME}" C-m
tmux send-keys -t $SESSION:0 "pipeline_runner --pipe ${SCRIPT_DIR}/rc3d_sender.pipe --set exp:experiment_file_name=etc/rc3d_experiment.yml --set rc3d:experiment_file_name=${RC3D_HOME}/experiments/virat/experiment.yml" C-m

echo "$(date) Starter script done!"
