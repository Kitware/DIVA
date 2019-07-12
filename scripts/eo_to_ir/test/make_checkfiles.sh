#!/bin/bash

source integration_tests.sh

for tst in test_{1..9}_0; do
    rm "${checkfiles_dir}/${tst}/"*

    $tst "$checkfiles_dir/$tst" >"$checkfiles_dir/$tst/$tst.log"
done
