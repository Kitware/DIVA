#!/bin/bash
# Test script that sends images and simulated detected object set across the wire
#   ./tmux_starter_script.sh  <environment_setup_script> 
# the enviornment setup script would be setup_DIVA.sh

SESSION="test_sender_sprokit_zeromq"

START_SCRIPT=$1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#cd ${SCRIPT_DIR}

echo "$(date) Creating session ${SESSION}"
tmux new-session -d -s $SESSION

sleep 1
echo "$(date) Starting Sender..."
tmux select-window -t $SESSION:0
tmux rename-window -t $SESSION:0 'Sender0'
tmux send-keys -t $SESSION:0 "source ${START_SCRIPT}" C-m
tmux send-keys -t $SESSION:0 "pipeline_runner --pipe ${SCRIPT_DIR}/test_experiment.pipe" C-m

echo "$(date) Starter script done!"
