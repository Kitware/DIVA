#!/bin/bash

source integration_tests.sh

for tst in test_{1..10}_0; do
    run_test "$tst" "$checkfiles_dir/$tst"
done
