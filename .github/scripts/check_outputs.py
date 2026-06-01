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
    simulated_run_dirs_glob = os.path.join(simulated_runs_dir, '*', '*', '*')
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
    Parse a symlink-seqs output CSV, annotating each row with the sequencing run ID
    extracted from the R1 path.
    """
    MISEQ_REGEX = r'\d{6}_M\d{5}_\d{4}_\d{9}-[A-Z0-9]{5}'
    NEXTSEQ_REGEX = r'\d{6}_VH\d{5}_\d+_[A-Z0-9]{9}'
    GRIDION_REGEX = r'\d{8}_\d{4}_X\d_[A-Z]{3}\d+_[a-z0-9]{8}'
    rows = []
    with open(symlink_seqs_output_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            r1 = row.get('R1', '')
            run_id = None
            for pattern in (GRIDION_REGEX, NEXTSEQ_REGEX, MISEQ_REGEX):
                m = re.search(pattern, r1)
                if m:
                    run_id = m.group(0)
                    break
            row['RUN_ID'] = run_id
            rows.append(row)
    return rows


def check_no_qc_failed_runs_are_symlinked(symlink_seqs_output, qc_status_by_run_id):
    """
    Return True if every row in symlink_seqs_output maps to a PASS QC status.
    """
    for library in symlink_seqs_output:
        run_id = library['RUN_ID']
        if run_id not in qc_status_by_run_id:
            print(f"ERROR: run ID {run_id!r} not found in QC status dict")
            return False
        if qc_status_by_run_id[run_id] != 'PASS':
            return False
    return True


def load_csv(path):
    """Return list of row dicts from a CSV file."""
    with open(path, 'r') as f:
        return list(csv.DictReader(f))


def check_csv_row_count(path, expected_count):
    """Return (passed, message) asserting exact row count."""
    rows = load_csv(path)
    actual = len(rows)
    if actual != expected_count:
        return False, f"{os.path.basename(path)}: expected {expected_count} rows, got {actual}"
    return True, f"{os.path.basename(path)}: row count {actual} OK"


def check_csv_sample_ids(path, expected_ids, forbidden_ids=None):
    """Return (passed, message) asserting expected IDs are present and forbidden IDs absent."""
    rows = load_csv(path)
    actual_ids = {row['ID'] for row in rows}
    missing = set(expected_ids) - actual_ids
    forbidden_found = (set(forbidden_ids) & actual_ids) if forbidden_ids else set()
    if missing or forbidden_found:
        parts = []
        if missing:
            parts.append(f"missing IDs: {sorted(missing)}")
        if forbidden_found:
            parts.append(f"forbidden IDs present: {sorted(forbidden_found)}")
        return False, f"{os.path.basename(path)}: " + "; ".join(parts)
    return True, f"{os.path.basename(path)}: sample IDs OK"


def check_csv_r1_paths_exist(path):
    """Return (passed, message) asserting every R1 path is non-empty."""
    rows = load_csv(path)
    bad = [row['ID'] for row in rows if not row.get('R1', '').strip()]
    if bad:
        return False, f"{os.path.basename(path)}: rows with empty R1: {bad}"
    return True, f"{os.path.basename(path)}: all R1 paths non-empty OK"


def main(args):
    artifacts_dir = 'artifacts/symlink-seqs'
    all_checks = []

    # ── deterministic test_run_dirs checks ──────────────────────────────────

    # MiSeq underscore normalisation: 5 samples expected
    miseq_us = os.path.join(artifacts_dir, 'miseq_251202_M04446_0426_000000000-M7L2J_alignment_2_samples_with_underscores.csv')
    for label, passed, msg in [
        ('miseq_underscore_row_count',  *check_csv_row_count(miseq_us, 5)),
        ('miseq_underscore_r1_paths',   *check_csv_r1_paths_exist(miseq_us)),
        ('miseq_underscore_sample_ids', *check_csv_sample_ids(miseq_us,
            expected_ids={'SAM001-1-research', 'SAM002-1-research', 'SAM003-1-research', 'NTC', 'control'})),
    ]:
        all_checks.append({'test_name': label, 'test_passed': passed, '_msg': msg})

    # NextSeq project-2 filter: 4 samples expected, no project-1 samples
    nextseq_p2 = os.path.join(artifacts_dir, 'nextseq_240719_VH00278_220_AAFMTYGM5_alignment_1_project-2.csv')
    for label, passed, msg in [
        ('nextseq_project2_row_count',  *check_csv_row_count(nextseq_p2, 4)),
        ('nextseq_project2_r1_paths',   *check_csv_r1_paths_exist(nextseq_p2)),
        ('nextseq_project2_sample_ids', *check_csv_sample_ids(nextseq_p2,
            expected_ids={'SAM005', 'SAM006', 'SAM007', 'SAM008'},
            forbidden_ids={'SAM001', 'SAM002', 'SAM003', 'SAM004'})),
    ]:
        all_checks.append({'test_name': label, 'test_passed': passed, '_msg': msg})

    # GridION all samples: 4 expected
    gridion_all = os.path.join(artifacts_dir, 'gridion_20260514_1837_X1_FBF94296_d5e6734f_all.csv')
    for label, passed, msg in [
        ('gridion_all_row_count',  *check_csv_row_count(gridion_all, 4)),
        ('gridion_all_r1_paths',   *check_csv_r1_paths_exist(gridion_all)),
    ]:
        all_checks.append({'test_name': label, 'test_passed': passed, '_msg': msg})

    # GridION project-1 filter: 2 expected, project-2 samples absent
    gridion_p1 = os.path.join(artifacts_dir, 'gridion_20260514_1837_X1_FBF94296_d5e6734f_project-1.csv')
    for label, passed, msg in [
        ('gridion_project1_row_count',  *check_csv_row_count(gridion_p1, 2)),
        ('gridion_project1_sample_ids', *check_csv_sample_ids(gridion_p1,
            expected_ids={'SAMPLE-001', 'SAMPLE-002'},
            forbidden_ids={'SAMPLE-003', 'SAMPLE-004'})),
    ]:
        all_checks.append({'test_name': label, 'test_passed': passed, '_msg': msg})

    # GridION underscore project IDs: alias SAMPLE-001_ecoli_test -> project_id 'ecoli_test' preserved
    gridion_us = os.path.join(artifacts_dir, 'gridion_20260601_1200_X1_GZB00001_b1c2d3e4_all.csv')
    gridion_us_filtered = os.path.join(artifacts_dir, 'gridion_20260601_1200_X1_GZB00001_b1c2d3e4_ecoli_test.csv')
    for label, passed, msg in [
        ('gridion_underscore_project_all_row_count',      *check_csv_row_count(gridion_us, 2)),
        ('gridion_underscore_project_filter_row_count',   *check_csv_row_count(gridion_us_filtered, 1)),
        ('gridion_underscore_project_filter_sample_ids',  *check_csv_sample_ids(gridion_us_filtered,
            expected_ids={'SAMPLE-001'},
            forbidden_ids={'SAMPLE-002'})),
    ]:
        all_checks.append({'test_name': label, 'test_passed': passed, '_msg': msg})

    # ── simulated-runs QC check ─────────────────────────────────────────────
    # mysterious_experiment: row count is deterministic when add_qc_check_complete.py uses --seed 42
    mysterious = os.path.join(artifacts_dir, 'mysterious_experiment.csv')
    label, passed, msg = 'mysterious_experiment_row_count', *check_csv_row_count(mysterious, 260)
    all_checks.append({'test_name': label, 'test_passed': passed, '_msg': msg})

    qc_status_by_run_id = collect_qc_status_by_run_id(args.simulated_runs_dir)
    simulated_output = parse_symlink_seqs_output_csv(args.symlink_seqs_output_csv)
    qc_passed = check_no_qc_failed_runs_are_symlinked(simulated_output, qc_status_by_run_id)
    all_checks.append({'test_name': 'no_qc_failed_runs_are_symlinked', 'test_passed': qc_passed, '_msg': ''})

    # ── report ───────────────────────────────────────────────────────────────
    for check in all_checks:
        status = "PASS" if check['test_passed'] else "FAIL"
        print(f"  [{status}] {check['test_name']}: {check['_msg']}")

    output_path = args.output
    with open(output_path, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=['test_name', 'test_result'], extrasaction='ignore')
        writer.writeheader()
        for check in all_checks:
            check['test_result'] = 'PASS' if check['test_passed'] else 'FAIL'
            writer.writerow(check)

    if any(not check['test_passed'] for check in all_checks):
        exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--simulated-runs-dir', default='artifacts/simulated_runs', help='Directory containing simulated runs')
    parser.add_argument('--symlink-seqs-output-csv', default='artifacts/symlink-seqs/mysterious_experiment.csv', help='Path to symlink-seqs output CSV')
    parser.add_argument('-o', '--output', type=str, help='Path to the output file')
    args = parser.parse_args()
    main(args)
