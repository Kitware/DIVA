#!/bin/bash

VIS_ROOT=$1
SLEEP_TIME=$2
while true
do
for image_file in $VIS_ROOT/image*
do
  eog --single-window $image_file &
  sleep $2
done
done
