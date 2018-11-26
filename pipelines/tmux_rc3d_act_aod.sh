#!/bin/bash

#+
# starter script with rc3d and act. 
# 
# Usage:
#
#   ./tmux_rc3d_act_aod.sh  <environment_setup_script> <rc3d_home> <act_home> <darknet_root> <vis_directory> <algorithm_time>
#
# environment_setup_script: A script (possibly setup_DIVA.sh) that
# sets the enviroment up properly so that pipeline_runner will be found in
# PATH and will execute properly
#
# rc3d_home: path to the home directory of rc3d
#
# act_home: path to the home directory of act 
#
# darknet_home: path to the home directory of darknet
#
# rc3d_vis_directory: directory where visualizations for rc3d are dumped
#
# act_vis_directory: directory where visualizations for act are dumped
#
# algorithm_time: approx time taken by the pipeline to output visualization
#-

SESSION="rc3d_act_aod_demo"

START_SCRIPT=$1
RC3D_HOME=$2
ACT_HOME=$3
DARKNET_HOME=$4
RC3D_VIS_DIRECTORY=$5
ACT_VIS_DIRECTORY=$5
ALGORITH_TIME=$6

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#cd ${SCRIPT_DIR}

echo "$(date) Creating session ${SESSION}"
tmux new-session -d -s $SESSION

sleep 1
echo "$(date) Starting Image Sender..."
tmux select-window -t $SESSION:0
tmux rename-window -t $SESSION:0 'Sender0'
tmux send-keys -t $SESSION:0 "source ${START_SCRIPT}" C-m
tmux send-keys -t $SESSION:0 "pipeline_runner --pipe ${SCRIPT_DIR}/image_sender.pipe --set exp:experiment_file_name=etc/input_stream.yml --set zmq_timg:port 5860 --set zmq_timg:expected_subscribers=2" C-m

sleep 1
tmux split-window -h -t $SESSION:0
tmux select-pane -t 0
tmux split-window -t $SESSION:0
tmux select-pane -t 1
tmux split-window -t 1 

sleep 1
echo "$(date) Starting RC3D Instance..."
tmux send-keys -t 1 "export PYTHONPATH=${RC3D_HOME}/experiments/virat" C-m
tmux send-keys -t 1 "source ${START_SCRIPT}" C-m
tmux send-keys -t 1 "mkdir -p ${RC3D_VIS_DIRECTORY}" C-m
tmux send-keys -t 1 "pipeline_runner --pipe ${SCRIPT_DIR}/rc3d.pipe --set rc3d:experiment_file_name=${RC3D_HOME}/experiments/virat/experiment.yml --set rc3d:model_cfg=${RC3D_HOME}/experiments/virat/td_cnn_end2end.yml --set zmq::port=5860 --set img_writer::file_name_template=${RC3D_VIS_DIRECTORY}/image%06d.jpg" C-m

sleep 1
echo "$(date) Starting ACT Instance..."
tmux send-keys -t 2 "export PYTHONPATH=${ACT_HOME}/act-detector-scripts:${ACT_HOME}/virat-act-detector-scripts:${ACT_HOME}/python:${PYTHONPATH}" C-m
tmux send-keys -t 2 "source ${START_SCRIPT}" C-m
tmux send-keys -t 2 "source ${ACT_HOME}/act-detector/bin/activate" C-m
tmux send-keys -t 2 "mkdir -p ${ACT_VIS_DIRECTORY}" C-m
tmux send-keys -t 2 "pipeline_runner --pipe ${SCRIPT_DIR}/act_aod_receiver.pipe --set act_process:exp=${ACT_HOME}/virat-act-detectory-scripts/rgb_eval_1b.yml --set --set zmq::port=5860 --set img_writer::file_name_template=${ACT_VIS_DIRECTORY}/image%06d.jpg" C-m

tmux select-pane -t 3
tmux split window -t 3

sleep 1
echo "$(date) Starting display..."
tmux send-keys -t 3 "dsplay.sh ${RC3D_VIS_DIRECTORY} ${ALGORITHM_TIME}" C-m

sleep 1
echo "$(date) Starting display..."
tmux send-keys -t 4 "dsplay.sh ${ACT_VIS_DIRECTORY} ${ALGORITHM_TIME}" C-m

echo "$(date) Starter script done!"
