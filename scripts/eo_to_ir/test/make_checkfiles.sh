#!/bin/bash

source integration_tests.sh

test_1_0 "$checkfiles_dir/test_1_0" >"$checkfiles_dir/test_1_0/test_1_0.log"
test_2_0 "$checkfiles_dir/test_2_0" >"$checkfiles_dir/test_2_0/test_2_0.log"
test_3_0 "$checkfiles_dir/test_3_0" >"$checkfiles_dir/test_3_0/test_3_0.log"
test_4_0 "$checkfiles_dir/test_4_0" >"$checkfiles_dir/test_4_0/test_4_0.log"
test_5_0 "$checkfiles_dir/test_5_0" >"$checkfiles_dir/test_5_0/test_5_0.log"
test_6_0 "$checkfiles_dir/test_6_0" >"$checkfiles_dir/test_6_0/test_6_0.log"
test_7_0 "$checkfiles_dir/test_7_0" >"$checkfiles_dir/test_7_0/test_7_0.log"
