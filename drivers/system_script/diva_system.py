#
# DIVA driver script
#

import os
import sys
import subprocess
import re
import argparse
import csv

can_plot = 0
try:
    import matplotlib.pyplot as plt
    import numpy as np
    can_plot = 1
except ImportError:
    sys.stderr.write( 'matlplotlib / numpy not available; cannot generate plots\n' )

def read_cfg( fn ):
    cfg = dict()
    block_stack = list()
    with open(fn) as f:
        while 1:
            raw_line = f.readline()
            if not raw_line:
                break
            if re.search( '^\s*#', raw_line ):
                continue
            fields = raw_line.strip().split()
            m = re.search( '^\s*([^\s]+)\s*\=\s*(.+)\s*$', raw_line )
            if len(fields) == 0:
                continue
            if fields[0] == 'block':
                block_stack.append( fields[1] )
            elif fields[0] == 'endblock':
                block_stack.pop()
            elif m:
                (local_key, val) = (m.group(1), m.group(2))
                full_key = ':'.join(block_stack) + ':'+local_key
                cfg[ full_key ] = val
            else:
                sys.stderr.write( 'Failed to parse config file line "%s"\n"' % raw_line )
    return cfg

def cfg_get( cfg, key ):
    if not key in cfg:
        sys.stderr.write( 'Key "%s" not defined in config\n' % key )
        return None
    return cfg[ key ]

def write_sample_experiment():
    sample="""#

    # This is a sample experiment file for the DIVA system.
    #
    # This file can be passed as the argument to diva_system.py for
    #
    #   1) Running the experiment
    #
    #   2) Scoring the results of the experiment
    #

    #-----------------------------------------
    # What is the purpose of this experiment?
    #-----------------------------------------

    type = object_detection

    #-----------------------------------------
    #
    # These parameters are specific to your algorithm and available
    # via the API
    #
    #-----------------------------------------

    block algo

      # what command should we run? '$expfn' will be expanded to the path
      # to this file

      command = /path/to/darknet_detections -r $expfn

      darknet_config_path = /path/to/darknet.config

    endblock

    #-----------------------------------------
    #
    # Tell the system about the input
    #
    #-----------------------------------------

    block input

      # the dataset ID is used as the prefix for output files
      dataset_id = VIRAT_S_000000

      # frame_rate_Hz metadata; available via the API if you want it
      frame_rate_Hz = 30.0

      # transport_type: how the input type is made available
      # currently only 'disk' is supported
      transport_type = disk

      # local path to the input data
      root_dir = /path/to/your/input

      # input source type; currently either 'file_list' or 'video'
      type = file_list

      # the instance of the input source, in this case, a file,
      # located in ${root_dir}/${source}, with filepaths of images to be
      # processed.
      source = frames.txt

    endblock


    #-----------------------------------------
    #
    # Tell the system about your output
    #
    #-----------------------------------------

    block output

      # How will your algorithm's output be transported?
      type = file

      # Where will the output be written?
      root_dir = /path/to/your/ouput

    endblock

    #-----------------------------------------
    #
    # scoring
    #
    #-----------------------------------------

    block scoring

       # path to score_events binary
       score_events = /path/to/your/score_events

       # reference geometry
       ref_geom = /path/to/ref_geom.kpf.yml

       # computed geometry
       # defaults to output:root_dir:dataset_id.geom.kpf
       # computed_geom = /path/to/computed/geometry

       # evaluation results destination
       eval_output_dir = /path/to/evaluation/output

       # parameters to plot ROC curves
       # roc_opts = TBD

       # parameters used when type == object_detection

       block object_detection

           # path to reference object types file
           ref_types = /path/to/ref_types.kpf.yml

           # What diva object type are we scoring? 'Person' or 'Vehicle'
           target = Person

           # intersection-over-union to claim an object intersection
           iou = 0.5

           # what time window do you want to score?
           # format: start-frame:end-frame, e.g. 15:29
           # or use 'M' to auto-compute
           time_window 0:10


    endblock
    """
    print sample

def run_experiment( expfn, dry_run_flag ):
    cfg  = read_cfg( expfn )
    cmd = cfg_get( cfg, 'algo:command' )
    if not cmd:
        return
    cmd = cmd.replace( '$expfn', expfn )
    if dry_run_flag:
        sys.stdout.write( 'Command: "%s"\n' % cmd )
    else:
        subprocess.call( cmd, shell=True )


def score_experiment (expfn, dry_run_flag ):
    cfg = read_cfg( expfn )
    score_exe = cfg_get( cfg, 'scoring:score_events' )
    ref_geom = cfg_get( cfg, 'scoring:ref_geom' )
    out_dir = cfg_get( cfg, 'scoring:eval_output_dir' )
    dataset_id = cfg_get( cfg, 'input:dataset_id' )

    if not dataset_id:
        return

    comp_geom_key = 'scoring:computed_geom'
    comp_geom = None
    if not comp_geom_key in cfg:
        k1 = cfg_get( cfg, 'output:root_dir' )
        if not k1:
            return
        comp_geom = '%s/%s.geom.yml' % (k1, dataset_id )
        sys.stderr.write( 'Assuming computed geometry %s\n' % comp_geom )
    else:
        comp_geom = cfg[ comp_geom_key ]

    for i in [ score_exe, ref_geom, comp_geom ]:
        if not i:
            return
        if not os.path.exists( i ):
            sys.stderr.write( 'File %s does not exist\n' % i )
            return

    if not out_dir:
        return
    if not os.path.isdir( out_dir ):
        sys.stderr.write( 'Output directory %s is not a directory' % out_dir )
        return

    exp_type = cfg_get( cfg, ':type' )
    if not exp_type:
        return

    cmd = None
    title = None

    if exp_type == 'object_detection':
        ref_types = cfg_get( cfg, 'scoring:object_detection:ref_types' )
        obj_type = cfg_get( cfg, 'scoring:object_detection:target' )
        iou = cfg_get( cfg, 'scoring:object_detection:iou' )
        time_window = cfg_get( cfg, 'scoring:object_detection:time_window' )
        for i in [ ref_types, obj_type, iou, time_window ]:
            if not i:
                return

        title = '%s\n%s det' % (dataset_id, obj_type )
        if time_window != 'M':
            time_window = 'if' + time_window

        if not os.path.exists( ref_types ):
            sys.stderr.write( 'File %s does not exist\n' % ref_types )
            return

        roc_fn = '%s/%s.%s.roc' % (out_dir, dataset_id, obj_type )
        roc_csv_fn = '%s/%s.%s.roc.csv' % (out_dir, dataset_id, obj_type )

        cmd = list()
        cmd.append( '%s' % score_exe )
        cmd.append( '--kpf-target object:%s:3' % obj_type )
        cmd.append( '--kpf-conf-src cset:3' )
        cmd.append( '--kpf-types-gt %s' % ref_types )
        cmd.append( '--computed-tracks %s' % comp_geom )
        cmd.append( '--truth-tracks %s' % ref_geom )
        cmd.append( '--detection-mode' )
        cmd.append( '--fn2ts' )
        cmd.append( '--time-window %s' % time_window )
        cmd.append( '--iou %s' % iou )
        cmd.append( '--roc-csv-dump %s' % roc_csv_fn )

    else:
        sys.stderr.write( 'Scoring requested for unhandled experiment type "%s"\n' % exp_type )
        return

    if dry_run_flag:
        sys.stdout.write( 'Command: %s\n' % ' '.join(cmd) )
        return
    else:
        subprocess.call( ' '.join(cmd), shell=True )

        if can_plot:
            pd = list()
            fa = list()
            with open( roc_csv_fn ) as csvfile:
                csvreader = csv.DictReader( csvfile, delimiter=',', skipinitialspace=True)
                for row in csvreader:
                    pd.append( float( row['PD'] ))
                    fa.append( float( row['FA'] ))
            fig = plt.figure()
            rocplot = plt.subplot( 1, 1, 1 )
            rocplot.set_title( title, fontsize=10 )
            rocplot.set_ylim( 0.0, 1.0 )
            rocplot.plot( fa, pd )
            plt.xlabel( "FA count", fontsize=10 )
            plt.ylabel( "PD", fontsize=10 )
            plot_fn = '%s/%s.%s.png' % (out_dir, dataset_id, obj_type )
            plt.savefig( plot_fn )
            sys.stderr.write( 'Info: saved plot to %s\n' % plot_fn )
            plt.show()


if __name__ == '__main__':

    parser = argparse.ArgumentParser( description = 'DIVA system script' );
    subparsers = parser.add_subparsers( dest='verb' )
    parser_sample = subparsers.add_parser( "sample", help="write sample experiment file to stdout" )
    parser_run = subparsers.add_parser( "run", help="run experiment file", )
    parser_run.add_argument( "expfn", action="store", help = "user experiment file" )
    parser_score = subparsers.add_parser( "score", help="score experiment" )
    parser_score.add_argument( "expfn", action="store", help = "user experiment file" )
    parser.add_argument( "-n", "--dry-run", action = "store_true" )
    parser_load = subparsers.add_parser ("load" )
    parser_load.add_argument( "expfn", action="store" )
    args = parser.parse_args()
    if args.verb == 'sample':
        write_sample_experiment()
    elif args.verb == 'run':
        run_experiment( args.expfn, args.dry_run )
    elif args.verb == 'score':
        score_experiment( args.expfn, args.dry_run )
    elif args.verb == 'load':
        c = read_cfg( args.expfn )
        for k,v in c.iteritems():
            sys.stderr.write( 'loaded "%s" = "%s"\n' % (k, v))
    else:
        sys.stderr.write( 'Logic error: unhandled verb %s\n' % (args.verb) )


    # all done
