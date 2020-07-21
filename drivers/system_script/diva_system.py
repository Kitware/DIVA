#
# DIVA driver script
#

import os
import sys
import subprocess
import re
import argparse
import csv
import diva_python_utils

can_plot = 0
try:
    import matplotlib
    if os.environ.get('DISPLAY','') == '':
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    can_plot = 1
except ImportError:
    sys.stderr.write('matlplotlib / numpy not available; cannot generate plots\n')
    sys.stderr.write('you need to have these python packages installed: matplotlib and numpy\n')
    sys.stderr.write('you also need to: sudo apt-get install python-tk\n')

def run_experiment( expfn, dry_run_flag ):
    exp = diva_python_utils.experiment()
    exp.read_experiment(expfn)
    cmd = exp.get_algorithm_executable()
    if not cmd:
        return
    cmd = cmd.replace('$expfn', expfn)
    if dry_run_flag:
        sys.stdout.write('Command: "%s"\n' % cmd)
    else:
        subprocess.call( cmd, shell=True )


def score_experiment (expfn, dry_run_flag ):
    exp = diva_python_utils.experiment()
    exp.read_experiment(expfn)
    #print exp.to_string()

    if not exp.has_dataset_id():
        return

    score_exe = exp.get_score_events_executable()
    ref_geom = exp.get_scoring_reference_geometry()
    out_dir = exp.get_scoring_evaluation_output_dir()
    dataset_id = exp.get_dataset_id()
    comp_geom = exp.get_output_filename() + '.geom.yml'
    exp_type = exp.get_type()

    for i in [ score_exe, ref_geom, comp_geom ]:
        if not i:
            return
        if not os.path.exists( i ):
            sys.stderr.write( 'File %s does not exist\n' % i )
            return
    if not os.path.isdir( out_dir ):
        sys.stderr.write( 'Output directory %s is not a directory' % out_dir )
        return

    cmd = None
    title = None

    if exp_type == diva_python_utils.experiment_type.object_detection:
        ref_types = exp.get_scoring_object_detection_reference_types()
        obj_type = exp.get_scoring_object_detection_target()
        iou = exp.get_scoring_object_detection_iou()
        time_window = exp.get_scoring_object_detection_time_window()
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
    parser_run = subparsers.add_parser( "run", help="run experiment file", )
    parser_run.add_argument( "expfn", action="store", help = "user experiment file" )
    parser_score = subparsers.add_parser( "score", help="score experiment" )
    parser_score.add_argument( "expfn", action="store", help = "user experiment file" )
    parser.add_argument( "-n", "--dry-run", action = "store_true" )
    parser_load = subparsers.add_parser ("load" )
    parser_load.add_argument( "expfn", action="store" )
    args = parser.parse_args()
    if args.verb == 'run':
        run_experiment( args.expfn, args.dry_run )
    elif args.verb == 'score':
        score_experiment( args.expfn, args.dry_run )
    elif args.verb == 'load':
        exp = diva_python_utils.experiment()
        exp.read_experiment(args.expfn)
        print(exp.to_string())
    else:
        sys.stderr.write( 'Logic error: unhandled verb %s\n' % (args.verb) )


    # all done
