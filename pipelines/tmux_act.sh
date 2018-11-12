#!/bin/bash

#+
# RC3D starter script. 
# 
# Usage:
#
#   ./tmux_act.sh  <environment_setup_script> <act_home> <vis_directory> <algorithm_time>
#
# environment_setup_script: A script (possibly setup_DIVA.sh) that
# sets the enviroment up properly so that pipeline_runner will be found in
# PATH and will execute properly
#
# act_home: path to the home directory of act 
#
# vis_directory: directory where visualizations are dumped
#
# algorithm_time: approx time taken by the pipeline to output visualization
#-

SESSION="act_demo"

START_SCRIPT=$1
ACT_HOME=$2
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
tmux send-keys -t $SESSION:0 "pipeline_runner --pipe ${SCRIPT_DIR}/image_sender.pipe --set exp:experiment_file_name=etc/input_stream.yml --set zmq_timg:port 5660" C-m

sleep 1
tmux split-window -h -t $SESSION:0
tmux select-pane -t 0
tmux split-window -t $SESSION:0

sleep 1
echo "$(date) Starting ACT Instance..."
tmux send-keys -t 1 "export PYTHONPATH=${ACT_HOME}/act-detector-scripts:${ACT_HOME}/virat-act-detector-scripts:${ACT_HOME}/python:${PYTHONPATH}" C-m
tmux send-keys -t 1 "source ${START_SCRIPT}" C-m
tmux send-keys -t 1 "source ${ACT_HOME}/act-detector/bin/activate" C-m
tmux send-keys -t 1 "mkdir -p ${VIS_DIRECTORY}" C-m
tmux send-keys -t 1 "pipeline_runner --pipe ${SCRIPT_DIR}/act_receiver.pipe --set act_process:exp=${ACT_HOME}/virat-act-detectory-scripts/rgb_eval_1b.yml --set --set zmq::port=5660 --set img_writer::file_name_template=${VIS_DIRECTORY}/image%06d.jpg" C-m

sleep 1
echo "$(date) Starting display..."
tmux send-keys -t 2 "dsplay.sh ${VIS_DIRECTORY} ${ALGORITHM_TIME}" C-m

echo "$(date) Starter script done!"
