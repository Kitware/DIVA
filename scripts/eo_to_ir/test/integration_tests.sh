#!/bin/bash

export checkfiles_dir=checkfiles

check_status() {
    status=$?
    if [ $status -ne 0 ]; then
	echo "*** FAILED ***"
	exit $status
    fi
}

run_test() {
    test=$1
    checkfile_outdir=$2
    checkfile_outdir_basename=`basename $checkfile_outdir`
    compcheck_outdir=${3-compcheckfiles}
    compcheckfile_outdir="$compcheck_outdir/$checkfile_outdir_basename"
    if [ -d "$compcheckfile_outdir" ]; then
	rm "${compcheckfile_outdir}/"*
    else
	mkdir -p "$compcheckfile_outdir"
    fi

    echo "** Running integration test '$test' **"
    log_fn="$compcheckfile_outdir/$test.log"
    $test "$compcheckfile_outdir" >"$log_fn"
    check_status

    # Replace paths in logfile
    for f in "$log_fn" "${compcheckfile_outdir}/config.csv"; do
	if [ -f "$f" ]; then
	    sed -e "s:${compcheckfile_outdir}:${checkfile_outdir}:g" "$f" >"$f.new"
	    mv "$f.new" "$f"
	fi
    done
    diff --exclude \*png -r "$checkfile_outdir" "$compcheckfile_outdir"
    check_status
    
    echo "*** OK ***"
}

test_1_0() {
    python ../eo_to_ir.py \
	   -g "test_1.geom.yml" \
	   -a "test_1.act.yml" \
	   -t "test_1.types.yml" \
	   -b "352x240" \
	   -o "$1"
}

test_2_0() {
    python ../eo_to_ir.py \
	   -g "test_2.geom.yml" \
	   -a "test_2.act.yml" \
	   -t "test_2.types.yml" \
	   -b "8x8" \
	   -o "$1"
}

test_3_0() {
    python ../eo_to_ir.py \
	   -g "test_3.geom.yml" \
	   -a "test_3.act.yml" \
	   -t "test_3.types.yml" \
	   -b "8x8" \
	   -o "$1"
}

test_4_0() {
    python ../eo_to_ir.py \
	   -g "test_1.geom.yml" \
	   -a "test_1.act.yml" \
	   -t "test_1.types.yml" \
	   -b "352x240" \
	   -o "$1" \
	   -f "10"
}

test_5_0() {
    python ../eo_to_ir.py \
	   -g "test_2.geom.yml" \
	   -a "test_2.act.yml" \
	   -t "test_2.types.yml" \
	   -b "16x16" \
	   -H "test_homography_1.txt" \
	   -o "$1"
}

test_6_0() {
    python ../eo_to_ir.py \
	   -g "test_2.geom.yml" \
	   -a "test_2.act.yml" \
	   -t "test_2.types.yml" \
	   -b "16x16" \
	   -H "test_homography_2.txt" \
	   -o "$1"
}

test_7_0() {
    python ../eo_to_ir.py \
	   -g "test_2.geom.yml" \
	   -a "test_2.act.yml" \
	   -t "test_2.types.yml" \
	   -b "16x16" \
	   -H "test_homography_2.txt" \
	   -f "12" \
	   -o "$1"
}

test_8_0() {
    python ../eo_to_ir.py \
	   -g "test_4.geom.yml" \
	   -a "test_2.act.yml" \
	   -t "test_2.types.yml" \
	   -b "16x16" \
	   -H "test_homography_1.txt" \
	   --min-spatial-overlap 0.5 \
	   -o "$1"
}
