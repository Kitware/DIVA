#!/bin/bash

#+
# Simple receiver that starts two pipelines, one to receive image and the other to 
# receiver detected object set
# Usage:
#
#   ./tmux_receiver_starter_script.sh <environment_setup_script> <host_ip>
#
# environment_setup_script: A script (possibly setup_DIVA.sh) that
# sets the enviroment up properly so that pipeline_runner will be found in
# PATH and will execute properly
# 
# host_ip: IP address of the host where the send is running
#
# TMUX session will create 2 panes with the two receivers
#-

SESSION="test_receiver_sprokit_zeromq"

START_SCRIPT=$1
HOST_IP=$2

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#cd ${SCRIPT_DIR}

echo "$(date) Creating session ${SESSION}"
tmux new-session -d -s $SESSION

sleep 1
echo "$(date) Starting image receiver..."
tmux select-pane -t 0
#tmux send-keys -t 1 "cd ${SCRIPT_DIR}" C-m
tmux send-keys -t 0 "source ${START_SCRIPT}" C-m
tmux send-keys -t 0 "pipeline_runner --pipe ${SCRIPT_DIR}/test_experiment_receive.pipe --set zmq:connect_host=${HOST_IP}" C-m

sleep 1
tmux split-window -t $SESSION:0
tmux select-pane -t 0
tmux split-window -h -t $SESSION:0

sleep 1
echo "$(date) Starting detected object set receiver ..."
#tmux send-keys -t 3 "cd ${SCRIPT_DIR}" C-m
tmux send-keys -t 2 "source ${START_SCRIPT}" C-m
tmux send-keys -t 2 "pipeline_runner --pipe ${SCRIPT_DIR}/test_experiment_receive2.pipe --set zmq:connect_host=${HOST_IP}" C-m

echo "$(date) Receiver script done!"
