#!/usr/bin/env python

import argparse
import glob
import json
import logging
import os
import re


def determine_sequencer_type(run_id):
    miseq_regex = '\d{6}_M\d{5}_\d{4}_\d{9}-[A-Z0-9]{5}'
    nextseq_regex = '\d{6}_VH\d{5}_\d+_[A-Z0-9]{9}'
    sequencer_type = None
    if re.match(miseq_regex, run_id):
        sequencer_type = "miseq"
    elif re.match(nextseq_regex, run_id):
        sequencer_type = "nextseq"

    return sequencer_type


def parse_samplesheet_miseq(samplesheet_path):
    data = []
    with open(samplesheet_path, 'r') as f:
        for line in f:
            if not line.strip().startswith('[Data]'):
                continue
            else:
                break
          
        data_header = [x.lower() for x in next(f).strip().split(',')]
      
        for line in f:
            if not all([x == '' for x in line.strip().split(',')]):
                data_line = {}
                for idx, data_element in enumerate(line.strip().split(',')):
                    try:
                        data_line[data_header[idx]] = data_element
                    except IndexError as e:
                        pass
                data.append(data_line)

    return data


def parse_samplesheet_nextseq(samplesheet_path):
    pass


def has_necessary_fields_for_symlinking(sample):
    selected = False
    conditions = []
    if 'sample_name' in sample and sample['sample_name'] != "":
        conditions.append(True)
    else:
        conditions.append(False)

    if 'sample_project' in sample and sample['sample_project'] != "":
        conditions.append(True)
    else:
        conditions.append(False)

    if all(conditions):
        selected = True

    return selected


def create_symlinks(samples, sequencer_type, run_dir, outdir):
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    fastq_subdir = None
    if sequencer_type == "miseq":
        fastq_subdir = "Data/Intensities/BaseCalls"
    elif sequencer_type == "nextseq":
        fastq_subdir = "Analysis/1/Data/fastq"
    for sample in samples:
        sample_fastq_files = glob.glob(os.path.join(run_dir, fastq_subdir, sample['sample_name'] + '*.fastq'))
        sample_fastq_gz_files = glob.glob(os.path.join(run_dir, fastq_subdir, sample['sample_name'] + '*.fastq.gz'))
        for sample_fastq_file in sample_fastq_files + sample_fastq_gz_files:
            if os.path.exists(sample_fastq_file):
                try:
                    os.symlink(os.path.abspath(sample_fastq_file), os.path.join(outdir, os.path.basename(sample_fastq_file)))
                except OSError as e:
                    print(e)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--run-dir')
    parser.add_argument('-p', '--project-id')
    parser.add_argument('-o', '--outdir')
    args = parser.parse_args()

    run_id = os.path.basename(args.run_dir.rstrip('/'))
    sequencer_type = determine_sequencer_type(run_id)

    if sequencer_type == 'miseq':
        samplesheet_path = os.path.join(args.run_dir, 'SampleSheet.csv')
        all_samples = parse_samplesheet_miseq(samplesheet_path)
        candidate_samples = filter(has_necessary_fields_for_symlinking, all_samples)
        selected_samples = filter(lambda x: x['sample_project'] == args.project_id, candidate_samples)
        create_symlinks(selected_samples, sequencer_type, args.run_dir, args.outdir)
    

if __name__ == '__main__':
    main()
