#!/bin/bash

#+
# RC3D starter script. 
# 
# Usage:
#
#   ./tmux_rc3d.sh  <environment_setup_script> <rc3d_home> <vis_directory> <algorithm_time>
#
# environment_setup_script: A script (possibly setup_DIVA.sh) that
# sets the enviroment up properly so that pipeline_runner will be found in
# PATH and will execute properly
#
# rc3d_home: path to the home directory of RC3D 
#
# vis_directory: directory where visualizations are dumped
#
# algorithm_time: approx time taken by the pipeline to output visualization
#-

SESSION="rc3d_demo"


START_SCRIPT=$1
RC3D_HOME=$2
VIS_DIRECTORY=$3
ALGORITH_TIME=$4

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#cd ${SCRIPT_DIR}

echo "$(date) Creating session ${SESSION}"
tmux new-session -d -s $SESSION

sleep 1
echo "$(date) Starting Image Sender..."
tmux select-window -t $SESSION:0
tmux rename-window -t $SESSION:0 'Sender0'
tmux send-keys -t $SESSION:0 "source ${START_SCRIPT}" C-m
tmux send-keys -t $SESSION:0 "pipeline_runner --pipe ${SCRIPT_DIR}/image_sender.pipe --set exp:experiment_file_name=etc/input_stream.yml --set zmq_timg:port 5560" C-m

sleep 1
tmux split-window -h -t $SESSION:0
tmux select-pane -t 0
tmux split-window -t $SESSION:0

sleep 1
echo "$(date) Starting RC3D Instance..."
tmux send-keys -t 1 "export PYTHONPATH=${RC3D_HOME}/experiments/virat" C-m
tmux send-keys -t 1 "source ${START_SCRIPT}" C-m
tmux send-keys -t 1 "pipeline_runner --pipe ${SCRIPT_DIR}/rc3d.pipe --set rc3d:experiment_file_name=${RC3D_HOME}/experiments/virat/experiment.yml --set rc3d:model_cfg=${RC3D_HOME}/experiments/virat/td_cnn_end2end.yml --set zmq::port=5560" C-m


echo "$(date) Starter script done!"
