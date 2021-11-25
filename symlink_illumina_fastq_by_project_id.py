#!/usr/bin/env python

import argparse
import glob
import json
import logging
import os
import re


# https://stackoverflow.com/a/1176023
def camel_to_snake(name):
  name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
  return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


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
    cloud_data_lines = []
    cloud_data = []
    with open(samplesheet_path, 'r') as f:
        for line in f:
            if line.strip().startswith('[Cloud_Data]'):
                break
        for line in f:
            if line.strip().startswith('[Cloud_Settings]') or line.strip().rstrip(',') == "":
                break
            cloud_data_lines.append(line.strip().rstrip(','))

    if cloud_data_lines:
        cloud_data_keys = [camel_to_snake(x) for x in cloud_data_lines[0].split(',')]
        for line in cloud_data_lines[1:]:
            d = {}
            values = line.strip().split(',')
            if not all([x == '' for x in values]):
                for idx, key in enumerate(cloud_data_keys):
                    try:
                        d[key] = values[idx]
                    except IndexError as e:
                        d[key] = ""
                cloud_data.append(d)
  
    return cloud_data


def has_necessary_fields_for_symlinking_miseq(sample):
    selected = False
    conditions = []
    if 'sample_name' in sample and sample['sample_name'] != "":
        conditions.append(True)
    elif 'sample_id' in sample and sample['sample_id'] != "":
        sample['sample_name'] = sample['sample_id']
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


def has_necessary_fields_for_symlinking_nextseq(sample):
    selected = False
    conditions = []
    if 'sample_id' in sample and sample['sample_id'] != "":
        conditions.append(True)
    else:
        conditions.append(False)

    if 'project_name' in sample and sample['project_name'] != "":
        conditions.append(True)
    else:
        conditions.append(False)

    if all(conditions):
        selected = True

    return selected


def create_symlinks(samples, sequencer_type, run_dir, outdir, simplify_sample_id):
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    fastq_subdir = None
    if sequencer_type == "miseq":
        fastq_subdir = "Data/Intensities/BaseCalls"
    elif sequencer_type == "nextseq":
        fastq_subdir = "Analysis/1/Data/fastq"
    for sample in samples:
        if sequencer_type == 'miseq':
            sample_id = sample['sample_name']
        elif sequencer_type == 'nextseq':
            sample_id = sample['sample_id']
        sample_fastq_files = glob.glob(os.path.join(run_dir, fastq_subdir, sample_id + '_*.fastq'))
        sample_fastq_gz_files = glob.glob(os.path.join(run_dir, fastq_subdir, sample_id + '_*.fastq.gz'))
        for sample_fastq_file in sample_fastq_files + sample_fastq_gz_files:
            if os.path.exists(sample_fastq_file):
                src = os.path.abspath(sample_fastq_file)
                dest_filename = os.path.basename(sample_fastq_file)
                if simplify_sample_id:
                    read = ""
                    if re.search('_R1_', dest_filename):
                        read = 'R1'
                    elif re.search('_R2_', dest_filename):
                        read = 'R2'
                    extension = '.fastq'
                    if dest_filename.split('.')[-1] == 'gz':
                        extension += '.gz'
                    dest_filename = dest_filename.split('_')[0] + '_' + read + extension
                dest = os.path.join(outdir, dest_filename)
                try:
                    os.symlink(src, dest)
                except OSError as e:
                    print(str(e) + ". sample_id: " + sample_id + ", file: " + dest)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--run-dir')
    parser.add_argument('-p', '--project-id')
    parser.add_argument('-s', '--simplify-sample-id', action='store_true')
    parser.add_argument('-o', '--outdir')
    args = parser.parse_args()

    run_id = os.path.basename(args.run_dir.rstrip('/'))
    sequencer_type = determine_sequencer_type(run_id)

    if sequencer_type == 'miseq':
        samplesheet_path = os.path.join(args.run_dir, 'SampleSheet.csv')
        all_samples = parse_samplesheet_miseq(samplesheet_path)
        candidate_samples = filter(has_necessary_fields_for_symlinking_miseq, all_samples)
        selected_samples = filter(lambda x: x['sample_project'] == args.project_id, candidate_samples)
        
    elif sequencer_type == 'nextseq':
        samplesheet_paths = glob.glob(os.path.join(args.run_dir, 'SampleSheet*.csv'))
        samplesheet_path = samplesheet_paths[0] # If multiple samplesheets exist, how do we choose the correct one?
        all_samples = parse_samplesheet_nextseq(samplesheet_path)
        candidate_samples = filter(has_necessary_fields_for_symlinking_nextseq, all_samples)
        selected_samples = filter(lambda x: x['project_name'] == args.project_id, candidate_samples)

    create_symlinks(selected_samples, sequencer_type, args.run_dir, args.outdir, args.simplify_sample_id)


if __name__ == '__main__':
    main()
