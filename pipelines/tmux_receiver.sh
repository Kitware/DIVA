#!/bin/bash

#+
# RC3D receiver starter script.  Designed to test 1 json writer and 1 instance of 
# swimlane visualization
# Usage:
#
#   ./tmux_starter_script.sh  <environment_setup_script> <rc3d_home> <host_ip>
#
# environment_setup_script: A script (possibly setup_DIVA.sh) that
# sets the enviroment up properly so that pipeline_runner will be found in
# PATH and will execute properly
# 
# rc3d_home: home directory for rc3d experiments directory ($RC3D_ROOT/experiments/virat)
#
# host_ip: ip address of the host system
#
#-

SESSION="rc3d_zeromq_receiver"

START_SCRIPT=$1
RC3D_HOME=$2
HOST_IP=$3

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#cd ${SCRIPT_DIR}

echo "$(date) Creating session ${SESSION}"
tmux new-session -d -s $SESSION

sleep 1
echo "$(date) Starting NIST JSON writer..."
tmux select-pane -t 0
tmux send-keys -t 0 "export PYTHONPATH=${RC3D_HOME}" C-m
tmux send-keys -t 0 "source ${START_SCRIPT}" C-m
tmux send-keys -t 0 "pipeline_runner --pipe ${SCRIPT_DIR}/json_writer_receiver.pipe --set zmq:connect_host=${HOST_IP} --set rc3d:exp_file=${RC3D_HOME}/experiment.yml" C-m

sleep 1
tmux split-window -t $SESSION:0

sleep 1
echo "$(date) Preparing Swimlane Visualizer..."
tmux send-keys -t 1 "export PYTHONPATH=${RC3D_HOME}" C-m
tmux send-keys -t 1 "source ${START_SCRIPT}" C-m
tmux send-keys -t 1 "pipeline_runner --pipe ${SCRIPT_DIR}/swimlane_receiver.pipe --set zmq:connect_host=${HOST_IP} --set rc3d:exp_file=${RC3D_HOME}/experiment.yml" C-m

echo "$(date) Receiver script done!"
