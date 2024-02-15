#!/usr/bin/env python3

# This script is used to temporarily fix an issue with the illumina-run-simulator
# where the samplesheet is not being written to the demultiplexed output directory.

import argparse
import glob
import json
import os
import shutil


def get_instrument_type(run_id):
    """
    Get the instrument type ("miseq" or "nextseq"), based on the run ID.

    :param run_id: Run directory
    :type run_id: str
    :return: Instrument type
    :rtype: str|None
    """
    instrument_type = None
    instrument_id = run_id.split('_')[1]
    if instrument_id.startswith('M'):
        instrument_type = 'miseq'
    elif instrument_id.startswith('V'):
        instrument_type = 'nextseq'

    return instrument_type


def get_demultiplexing_outdir(run):
    """
    Find the appropriate subdirectory to copy the samplesheet to.

    :param run: Run directory
    :type run: str
    :return: Demultiplexing output directory
    :rtype: str|None
    """
    demultiplexing_outdir = None
    run_id = os.path.basename(run)
    instrument_type = get_instrument_type(run_id)
    if instrument_type == 'miseq':
        if os.path.exists(os.path.join(run, 'Data')):
            demultiplexing_outdir = os.path.join(run)
        else:
            demultiplexing_outdir_glob = os.path.join(run, 'Alignment_*', '*')
            demultiplexing_outdir = sorted(glob.glob(demultiplexing_outdir_glob), reverse=True)[0]
    elif instrument_type == 'nextseq':
        demultiplexing_outdir_glob = os.path.join(run, 'Analysis', '*', 'Data')
        demultiplexing_outdir = sorted(glob.glob(demultiplexing_outdir_glob), reverse=True)[0]

    return demultiplexing_outdir


def main(args):
    simulated_runs_glob = os.path.join(args.simulated_runs_dir, '*', '*', '*')
    simulated_runs = glob.glob(simulated_runs_glob)
    for run in simulated_runs:
        samplesheet_path_src = os.path.join(run, 'SampleSheet.csv')
        run_id = os.path.basename(run)
        instrument_type = get_instrument_type(run_id)
        if instrument_type is None:
            continue
        demultiplexing_outdir = get_demultiplexing_outdir(run)
        samplesheet_path_dst = os.path.join(demultiplexing_outdir, 'SampleSheet.csv')
        try:
            shutil.copy(samplesheet_path_src, samplesheet_path_dst)
        except FileNotFoundError:
            continue
        except shutil.SameFileError:
            continue
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--simulated-runs-dir', default='artifacts/simulated_runs', help='Directory containing simulated runs')
    args = parser.parse_args()
    main(args)
