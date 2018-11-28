#!/bin/bash

#+
# ACT starter script. 
# 
# Usage:
#
#   ./tmux_act_zmq.sh  <environment_setup_script> <act_home> 
#
# environment_setup_script: A script (possibly setup_DIVA.sh) that
# sets the enviroment up properly so that pipeline_runner will be found in
# PATH and will execute properly
#
# act_home: path to the home directory of act 
#-

SESSION="act_zmq"

START_SCRIPT=$1
ACT_HOME=$2
ACT_CONFIG="${ACT_HOME}/virat-act-detector-scripts/rgb_eval_1b.yml"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "$(date) Creating session ${SESSION}"
tmux new-session -d -s $SESSION

sleep 1
echo "$(date) Starting ACT Instance..."
tmux send-keys -t 0 "export PYTHONPATH=${ACT_HOME}/act-detector-scripts:${ACT_HOME}/virat-act-detector-scripts:${ACT_HOME}/python:${PYTHONPATH}" C-m
tmux send-keys -t 0 "source ${START_SCRIPT}" C-m
tmux send-keys -t 0 "source ${ACT_HOME}/act-detector/bin/activate" C-m
tmux send-keys -t 0 "pipeline_runner --pipe ${SCRIPT_DIR}/act_zmq.pipe --set act_process:exp=${ACT_CONFIG} --set json_writer:exp=${ACT_CONFIG} --set merge_tubes:exp=${ACT_CONFIG} --set visualize:exp=${ACT_CONFIG}" C-m

echo "$(date) Starter script done!"
