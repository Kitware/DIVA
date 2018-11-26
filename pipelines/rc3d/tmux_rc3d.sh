#!/bin/bash

#+
# RC3D starter script. Runs rc3d pipeline on a single terminal 
# Usage:
#
#   ./tmux_starter_script.sh  <environment_setup_script> <rc3d_home>
#
# environment_setup_script: A script (possibly setup_DIVA.sh) that
# sets the enviroment up properly so that pipeline_runner will be found in
# PATH and will execute properly
# 
# rc3d_home: home directory for rc3d
#
#-

SESSION="rc3d"

START_SCRIPT=$1
RC3D_HOME=$2

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "$(date) Creating session ${SESSION}"
tmux new-session -d -s $SESSION

sleep 1
echo "$(date) Starting RC3D pipeline..."
tmux select-window -t $SESSION:0
tmux rename-window -t $SESSION:0 'Sender0'
tmux send-keys -t 0 "export PYTHONPATH=${RC3D_HOME}/experiments/virat" C-m
tmux send-keys -t 0 "source ${START_SCRIPT}" C-m
tmux send-keys -t 0 "pipeline_runner --pipe ${SCRIPT_DIR}/rc3d.pipe --set rc3d:experiment_file_name=${RC3D_HOME}/experiments/virat/experiment.yml --set rc3d:model_cfg=${RC3D_HOME}/experiments/virat/td_cnn_end2end.yml" C-m


echo "$(date) Starter script done!"
