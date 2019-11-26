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
	   -p "test_1" \
	   -o "$1"
}

test_2_0() {
    python ../eo_to_ir.py \
	   -g "test_2.geom.yml" \
	   -a "test_2.act.yml" \
	   -t "test_2.types.yml" \
	   -b "8x8" \
	   -p "test_2" \
	   -o "$1"
}

test_3_0() {
    python ../eo_to_ir.py \
	   -g "test_3.geom.yml" \
	   -a "test_3.act.yml" \
	   -t "test_3.types.yml" \
	   -b "8x8" \
	   -p "test_3" \
	   -o "$1"
}

test_4_0() {
    python ../eo_to_ir.py \
	   -g "test_1.geom.yml" \
	   -a "test_1.act.yml" \
	   -t "test_1.types.yml" \
	   -b "352x240" \
	   -p "test_4" \
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
	   -p "test_5" \
	   -o "$1"
}

test_6_0() {
    python ../eo_to_ir.py \
	   -g "test_2.geom.yml" \
	   -a "test_2.act.yml" \
	   -t "test_2.types.yml" \
	   -b "16x16" \
	   -H "test_homography_2.txt" \
	   -p "test_6" \
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
	   -p "test_7" \
	   -o "$1"
}

test_8_0() {
    python ../eo_to_ir.py \
	   -g "test_4.geom.yml" \
	   -a "test_2.act.yml" \
	   -t "test_2.types.yml" \
	   -b "16x16" \
	   -H "test_homography_1.txt" \
	   -p "test_8" \
	   --min-spatial-overlap 0.5 \
	   -o "$1"
}

test_9_0() {
    python ../eo_to_ir.py \
	   -g "test_5.geom.yml" \
	   -a "test_5.act.yml" \
	   -t "test_2.types.yml" \
	   -b "8x8" \
	   -p "test_9" \
	   -o "$1"
}


test_10_0() {
    # Test negative frame number filtering
    python ../eo_to_ir.py \
	   -g "test_2.geom.yml" \
	   -a "test_2.act.yml" \
	   -t "test_2.types.yml" \
	   -p "test_10" \
	   -b "8x8" \
	   -f "-2099" \
	   -o "$1"
}

test_11_0() {
    # Test multi-actor activities
    python ../eo_to_ir.py \
	   -g "test_2.geom.yml" \
	   -a "test_11.act.yml" \
	   -t "test_2.types.yml" \
	   -b "352x240" \
	   -p "test_11_0" \
	   -o "$1"
}

test_11_1() {
    # Test multi-actor activities, drop activity if any constituent
    # actor is filtered out
    python ../eo_to_ir.py \
	   -g "test_2.geom.yml" \
	   -a "test_11.act.yml" \
	   -t "test_2.types.yml" \
	   -b "8x8" \
	   -p "test_11_1" \
	   -o "$1"
}

test_11_2() {
    # Test multi-actor activities, drop activity if any constituent
    # actor is filtered out; With --include-orphans don't remove geom
    # or type records for actors no longer belonging to an activty
    python ../eo_to_ir.py \
	   -g "test_2.geom.yml" \
	   -a "test_11.act.yml" \
	   -t "test_2.types.yml" \
	   -b "8x8" \
	   -p "test_11_2" \
	   -o "$1" \
       --include-orphans
}
