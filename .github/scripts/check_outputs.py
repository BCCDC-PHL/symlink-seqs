#!/usr/bin/env python3

import argparse
import csv
import glob
import json
import os
import re


def collect_qc_status_by_run_id(simulated_runs_dir):
    """
    Collect the QC status for each simulated run.

    :param simulated_runs_dir: Directory containing simulated runs
    :type simulated_runs_dir: str
    :return: QC status by run ID
    :rtype: dict[str, str]
    """
    qc_status_by_run_id = {}
    simulated_run_dirs_glob = os.path.join(args.simulated_runs_dir, '*', '*', '*')
    simulated_run_dirs = glob.glob(simulated_run_dirs_glob)

    for run_dir in simulated_run_dirs:
        run_id = os.path.basename(run_dir)
        qc_check_complete_file = os.path.join(run_dir, 'qc_check_complete.json')
        with open(qc_check_complete_file, 'r') as f:
            qc_check = json.load(f)
            qc_status_by_run_id[run_id] = qc_check['overall_pass_fail']

    return qc_status_by_run_id


def parse_symlink_seqs_output_csv(symlink_seqs_output_csv):
    """
    """
    symlink_seqs_output = []
    miseq_regex = '\\d{6}_M\\d{5}_\\d{4}_\\d{9}-[A-Z0-9]{5}'
    nextseq_regex = '\d{6}_VH\d{5}_\d+_[A-Z0-9]{9}'
    with open(symlink_seqs_output_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            miseq_match = re.search(miseq_regex, row['R1'])
            nextseq_match = re.search(nextseq_regex, row['R1'])
            run_id = None
            if nextseq_match:
                run_id = nextseq_match.group(0)
            elif miseq_match:
                run_id = miseq_match.group(0)
            row['RUN_ID'] = run_id
            symlink_seqs_output.append(row)

    return symlink_seqs_output


def check_no_qc_failed_runs_are_symlinked(symlink_seqs_output, qc_status_by_run_id):
    """
    Check that no QC failed runs are symlinked.

    :param symlink_seqs_output: Symlink-seqs output
    :type symlink_seqs_output: list[dict[str, str]]
    :param qc_status_by_run_id: QC status by run ID
    :type qc_status_by_run_id: dict[str, str]
    :return: Whether or not no QC failed runs are symlinked (True if no QC failed runs are symlinked, False otherwise)
    :rtype: bool
    """
    qc_statuses = []
    for library in symlink_seqs_output:
        run_id = library['RUN_ID']
        qc_status = qc_status_by_run_id[run_id]
        qc_statuses.append(qc_status)

    all_qc_statuses_passed = all([qc_status == 'PASS' for qc_status in qc_statuses])

    return all_qc_statuses_passed
    

def main(args):
    qc_status_by_run_id = collect_qc_status_by_run_id(args.simulated_runs_dir)

    symlink_seqs_output = parse_symlink_seqs_output_csv(args.symlink_seqs_output_csv)

    no_qc_failed_runs_are_symlinked = check_no_qc_failed_runs_are_symlinked(symlink_seqs_output, qc_status_by_run_id)

    tests = [
        {
            'test_name': 'no_qc_failed_runs_are_symlinked',
            'test_passed': no_qc_failed_runs_are_symlinked,
        },
    ]

    output_fields = [
        "test_name",
        "test_result"
    ]

    output_path = args.output
    with open(output_path, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=output_fields, extrasaction='ignore')
        writer.writeheader()
        for test in tests:
            if test["test_passed"]:
                test["test_result"] = "PASS"
            else:
                test["test_result"] = "FAIL"
            writer.writerow(test)

    for test in tests:
        if not test['test_passed']:
            exit(1)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--simulated-runs-dir', default='artifacts/simulated_runs', help='Directory containing simulated runs')
    parser.add_argument('--symlink-seqs-output-csv', default='artifacts/symlink-seqs/mysterious_experiment.csv', help='Path to symlink-seqs output CSV')
    parser.add_argument('-o', '--output', type=str, help='Path to the output file')
    args = parser.parse_args()
    main(args)
