#!/bin/bash

source integration_tests.sh

for tst in test_{1..10}_0 test_11_{0,1}; do
    rm "${checkfiles_dir}/${tst}/"*

    $tst "$checkfiles_dir/$tst" >"$checkfiles_dir/$tst/$tst.log"
done
